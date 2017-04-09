#!/usr/bin/env python
import json
import os
import redis
import sys

import Globals
from zenoss.toolbox import ZenToolboxUtils
from Products.ZenUtils.ZenScriptBase import ZenScriptBase


scriptSummary = "Export event from redis or send exported to Zenoss"


def buildEvent(self, jsonEvent):
    from .utils import buildEvent
    try:
        eventDict = json.loads(rawEvent)
    except ValueError:
        eventDict = {}
    return buildEvent(eventDict)


def sendEventToZenoss(dmd, event):
    eventManager = dmd.ZenEventManager
    eventManager.sendEvent(event)


def writeToFile(file, events, pretty=False):
    with open(file, 'w') as _file:
        for event in events:
            _file.write("%s\n" % event)


def importEvents(file):
    with open(file, 'r') as _file:
        for line in _file.read():
            newEvent = buildEvent(event)
            sendEventToZenoss(dmd, newEvent)


def exportEvents(redisConnection, file, format):
    events = []
    for key in redisConnection.keys():
        events.append(redisConnection.hgetall(key))

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
