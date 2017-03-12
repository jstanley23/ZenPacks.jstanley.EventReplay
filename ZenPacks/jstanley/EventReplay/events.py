import redis

from zenoss.protocols.jsonformat import to_dict


class EventReplayPreEventPlugin(object):
    def apply(self, eventProxy, dmd):
        if not dmd.getProperty('eventReplayState'):
            return

        if hasattr(eventProxy, 'eventReplayInfo'):
            return

        rawEvent = to_dict(eventProxy._zepRawEvent)
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

