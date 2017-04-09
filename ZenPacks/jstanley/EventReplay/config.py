from Products.Zuul.utils import ZuulMessageFactory as _t

configSchema = [
    {
        'id': 'eventReplayRedisServer',
        'name': _t("Redis server to save events to and read from"),
        'xtype': 'textfield',
        '_default': 'localhost',
        '_type': 'string',
    },{
        'id': 'eventReplayRedisPort',
        'name': _t("Redis server port. Default zredis port: 16379"),
        'xtype': 'numberfield',
        '_default': 16379,
        '_type': 'int',
    },{
        'id': 'eventReplayRedisDB',
        'name': _t("Redis database to save events to and read from"),
        'xtype': 'numberfield',
        '_default': 15,
        '_type': 'int',
    },{
        'id': 'eventReplayLimit',
        'name': _t("Max raw events to save to redis"),
        'xtype': 'numberfield',
        '_default': 4001,
        '_type': 'int',
    },{
        'id': 'eventReplayFilter',
        'name': _t("Filter what events get saved. COMING SOON"),
#        'xtype': 'eventreplayfilter',
        'xtype': 'textfield',
        '_default': 'ALL',
        '_type': 'string',
    },{
        'id': 'eventReplayFilterCode',
        'xtype': 'hidden',
        '_default': '',
        '_type': 'string',
    },{
        'id': 'eventReplayState',
        'name': _t("Turn on saving events to redis"),
        'xtype': 'checkbox',
        '_default': False,
        '_type': 'bool',
    },
]

