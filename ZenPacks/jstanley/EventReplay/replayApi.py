'''
API interfaces and default implementations.
'''
import json
import logging

from zope.interface import implements

from Products import Zuul
from Products.ZenUI3.browser.streaming import StreamingView
from Products.ZenUtils.Ext import DirectRouter, DirectResponse
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade

class IEventReplayFacade(IFacade):
    def replay(self, events):
        """Replay an event from redis using eventReplayId(s)"""


class EventReplayFacade(ZuulFacade):
    implements(IEventReplayFacade)

    def replay(self, events):
       import pdb; pdb.set_trace()


class EventReplayRouter(DirectRouter):
    def _getFacade(self):
        return Zuul.getFacade('eventreplay', self.context)

    def replay(self, events):
        facade = self._getFacade()
        data = facade.replay(events)
        return DirectResponse.succeed(data=data)
