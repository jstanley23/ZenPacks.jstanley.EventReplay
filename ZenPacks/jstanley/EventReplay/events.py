import redis

from zenoss.protocols.jsonformat import to_dict
from .utils import checkEvent


class EventReplayPreEventPlugin(object):
    def apply(self, eventProxy, dmd):
#        import pdb; pdb.set_trace()
        if not dmd.getProperty('eventReplayState'):
            return

        if hasattr(eventProxy, 'eventReplayInfo'):
            return

        rawEvent = to_dict(eventProxy._zepRawEvent)
#        if dmd.getProperty('eventReplayFilter'):
#            result = checkEvent(rawEvent, dmd.getProperty('eventReplayFilter'))
#            import pdb; pdb.set_trace()
#            if not result:
#                return

        r = redis.StrictRedis(
            dmd.getProperty('eventReplayRedisServer'),
            dmd.getProperty('eventReplayRedisPort'),
            db=dmd.getProperty('eventReplayRedisDB'),
        )
        event = rawEvent.get('event', {})
        uuid = event.get('uuid')
        if not uuid:
            return

        listId = r.rpush('eventKeyList', uuid)
        hashResult = r.hmset(uuid, dict(event=event))

        if listId > dmd.getProperty('eventReplayLimit'):
            hashId = r.lpop('eventKeyList')
            r.delete(hashId)

        eventProxy.eventReplayId = uuid

