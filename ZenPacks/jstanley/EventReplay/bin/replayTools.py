#!/usr/bin/env python
import json
import os
import redis
import sys

from ast import literal_eval

import Globals
from zenoss.toolbox import ZenToolboxUtils
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from ZenPacks.jstanley.EventReplay.utils import buildEvent


scriptSummary = "Export event from redis or send exported to Zenoss"


def sendEventToZenoss(dmd, event):
    eventManager = dmd.ZenEventManager
    eventManager.sendEvent(event)


def writeToFile(file, events, pretty=False):
    with open(file, 'w') as _file:
        if pretty:
            _file.write(json.dumps(events, sort_keys=True, indent=4))
        else:
            _file.write(json.dumps(events))


def importEvents(dmd, file):
    with open(file, 'r') as _file:
        contents =  _file.read()
        events = json.loads(contents)

    for event in events:
        key = event.keys()[0]
        newEvent = buildEvent(event[key])
        sendEventToZenoss(dmd, newEvent)


def exportEvents(redisConnection, file, format):
    events = []
    for key in redisConnection.lrange('eventKeyList', 0, -1):
        data = redisConnection.hgetall(key)
        event = { key: literal_eval(data.get('event', "{}")) }
        events.append(event)

    writeToFile(file, events, format)


def main():
    scriptSummary = "Export event from redis or send exported to Zenoss"
    scriptName = os.path.basename(__file__).split('.')[0]
    scriptVersion = '1.0.0'

    parser = ZenToolboxUtils.parse_options(
        scriptVersion,
        "%s: %s" % (scriptName, scriptSummary)
    )
    parser.add_argument('-e', '--export', action='store', metavar='FILENAME',
        help='Export events from redis')
    parser.add_argument('-p', '--pretty', action='store_true', default=False,
        help='Export events in a pretty format')
    parser.add_argument('-l', '--load', action='store', metavar='FILENAME',
        help='Send events from file into Zenoss')

    cli_options = vars(parser.parse_args())

    dmd = ZenScriptBase(noopts=True, connect=True).dmd

    r = redis.StrictRedis(
        dmd.getProperty('eventReplayRedisServer'),
        dmd.getProperty('eventReplayRedisPort'),
        db=dmd.getProperty('eventReplayRedisDB'),
    )

    if cli_options['export']:
        exportEvents(r, cli_options['export'], cli_options['pretty'])
        sys.exit()
    elif cli_options['load'] and os.path.isfile(cli_options['load']):
        importEvents(dmd, cli_options['load'])


if __name__ == "__main__":
    main()
