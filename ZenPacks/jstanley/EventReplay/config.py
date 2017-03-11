_REDIS_SERVER = 'localhost'
_REDIS_PORT = 16379
# Zenoss seems to only use db 0
# But just in case, let us use the last db available.
_REDIS_DB = 15

# Limit of events to store in redis and set if its on or off
# TODO: Change these into a Setting in webUI
_LIMIT = 2000
_STATE = True
