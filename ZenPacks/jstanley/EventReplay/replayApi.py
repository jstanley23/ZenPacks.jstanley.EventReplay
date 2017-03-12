'''
API interfaces and default implementations.
'''
import json
import logging
import redis

from ast import literal_eval
from zope.interface import implements

from Products import Zuul
from Products.ZenMessaging.audit import audit
from Products.ZenUI3.browser.streaming import StreamingView
from Products.ZenUtils.Ext import DirectRouter, DirectResponse
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade

from .config import configSchema


LOG = logging.getLogger('zen.eventReplay.api')


class IEventReplayFacade(IFacade):
    def replay(self, events):
        """Replay an event from redis using eventReplayId(s)"""


class EventReplayFacade(ZuulFacade):
    implements(IEventReplayFacade)
    def __init__(self, context):
        self.context = context
        self.redisConfig = (
            context.getProperty('eventReplayRedisServer'),
            context.getProperty('eventReplayRedisPort'),
            context.getProperty('eventReplayRedisDB'),
        )
        self.redisConnection = self.setupRedisConnection()
        self.configSchema = configSchema

    def getConfig(self):
        config = []
        for prop in self.configSchema:
            value = self.context.getProperty(prop['id'])
            value = value if value else ""
            prop['value'] = value
            config.append(prop)
        return config

    def setConfig(self, values):
        for key, value in values.iteritems():
            self.context.manage_changeProperties(**{key: value})

    def setupRedisConnection(self):
        redisConnection = redis.StrictRedis(*self.redisConfig)
        return redisConnection

    def getReplayId(self, id):
        replayId = None
        zep = Zuul.getFacade('zep')
        event = zep.getEventSummary(id)
        occurrence = event.get('occurrence', [{}])[0]
        details = occurrence.get('details', [])
        for detail in details:
            if detail['name'] == 'eventReplayId':
                replayId = detail['value'][0]
                break
        return replayId

    def replayEvents(self, events):
        LOG.info(events)
        for event in events:
            replayId = self.getReplayId(event)
            if not replayId:
                err = "No replay Id in event"
                LOG.info("Failure replaying %s: %s", event, err)
                continue

            rawEvent = self.getRawEvent(replayId)
            if not rawEvent:
                err = "No longer in redis"
                LOG.info("Failure replaying %s: %s", event, err)
                continue

            newEvent = self.buildEvent(rawEvent)
            self.sendEventToZenoss(newEvent)
            LOG.info("Success replaying %s", event)

    def getRawEvent(self, id):
        data = self.redisConnection.hgetall(id)
        event = data.get('event', {})
        return event

    def buildEvent(self, rawEvent):
        # TODO remove this method and just use import
        from .utils import buildEvent
        try:
            eventDict = literal_eval(rawEvent)
        except (NameError, ValueError):
            LOG.warn("Unable to convert to dictionary: %s", rawEvent)
            eventDict = {}
        return buildEvent(eventDict)

    def sendEventToZenoss(self, event):
        eventManager = self.context.ZenEventManager
        eventManager.sendEvent(event)


class EventReplayRouter(DirectRouter):
    def __init__(self, context, request):
        super(EventReplayRouter, self).__init__(context, request)
        self.facade = self._getFacade()

    def _getFacade(self):
        return Zuul.getFacade('eventreplay', self.context)

    def replayEvents(self, events):
        self.facade.replayEvents(events)
        return DirectResponse.succeed(msg="Check log for details")

    def getConfig(self):
        config = self.facade.getConfig()
        return DirectResponse.succeed(data=config)

    def setConfigValues(self, values):
        self.facade.setConfig(values)
        audit('UI.Event.UpdateConfiguration', values=values)
        return DirectResponse.succeed()
