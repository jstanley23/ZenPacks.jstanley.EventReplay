import redis

from .config import _REDIS_SERVER, _REDIS_PORT, _REDIS_DB, _LIMIT, _STATE

from zenoss.protocols.jsonformat import from_dict, to_dict


class EventReplayPreEventPlugin(object):
    def __init__(self):
        self.redisServer = _REDIS_SERVER
        self.redisPort = _REDIS_PORT
        self.redisDb = _REDIS_DB

    def apply(self, eventProxy, dmd):
        if hasattr(eventProxy, 'eventReplayInfo'):
            return
        rawEvent = to_dict(eventProxy._zepRawEvent)
        r = redis.StrictRedis(_REDIS_SERVER, _REDIS_PORT, db=_REDIS_DB)
        event = rawEvent.get('event', {})
        uuid = event.get('uuid')
        if not uuid:
            return

        listId = r.rpush('eventKeyList', uuid)
        hashResult = r.hmset(uuid, dict(event=event))

        if listId > _LIMIT:
            hashId = r.lpop('eventKeyList')
            r.delete(hashId)

        eventProxy.eventReplayId = uuid


