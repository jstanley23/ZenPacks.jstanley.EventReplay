from zenoss.protocols.protobufs.model_pb2 import _MODELELEMENTTYPE


class imitationDevice(object):
    def __init__(self, event):
        details = {}
        eventInfo = event.get('event', {})
        if eventInfo:
            eventDetails = eventInfo.get('details', [])
            details = { x['name']:x['value'] for x in eventDetails }
        self.ip_address = details.get('zenoss.device.ip_address', [''])[0]
        self.device_class = details.get('', [''])
        self.production_state = int(details.get('zenoss.device.production_state', [-10])[0])
        self.priority = int(details.get('zenoss.device.priority', [-10])[0])
        self.location = details.get('zenoss.device.location', [''])[0]
        self.systems = details.get('zenoss.device.systems', [''])
        self.groups = details.get('zenoss.device.groups', [''])


class imitationEvent(object):
    def __init__(self, event):
        eventDetails = {}
        eventInfo = event.get('event', {})
        self.severity = int(eventInfo.get('severity', -10))
        self.event_key = eventInfo.get('event_key', '')
        self.event_class = eventInfo.get('event_class', '')
        self.event_class_key = eventInfo.get('event_class_key', '')
        self.summary = eventInfo.get('summary', '')
        self.message = eventInfo.get('message', '')
        self.fingerprint = eventInfo.get('fingerprint', '')
        self.agent = eventInfo.get('agent', '')
        self.monitor = eventInfo.get('monitor', '')
        self.count = int(event.get('count', 1))
        self.status = int(event.get('status', -10))
        self.syslog_priority = int(eventInfo.get('syslog_priority', -10))
        self.syslog_facility = int(eventInfo.get('syslog_facility', -10))
        self.nt_event_code = int(eventInfo.get('nt_event_code', -10))
        self.current_user_name = event.get('current_user_name', '')


class imitationElement(object):
    def __init__(self, event):
        actor = {}
        eventInfo = event.get('event', {})
        if eventInfo:
            actor = eventInfo.get('actor', {})
        elementType = actor.get('element_type_id', -10)
        elementLookup = _MODELELEMENTTYPE.values_by_number.get(elementType)
        self.name = actor.get('element_title', '')
        self.type = getattr(elementLookup, 'name', '')


class imitationSubElement(object):
    def __init__(self, event):
        actor = {}
        eventInfo = event.get('event', {})
        if eventInfo:
            actor = eventInfo.get('actor', {})
        elementType = actor.get('element_sub_type_id', -10)
        elementLookup = _MODELELEMENTTYPE.values_by_number.get(elementType)
        self.name = actor.get('element_sub_title', '')
        self.type = getattr(elementLookup, 'name', '')


class imitationEventDetails(object):
    def __init__(self, event):
        eventInfo = event.get('event', {})
        eventDetails = eventInfo.get('details', [])
        for field in eventDetails:
            setattr(self, field['name'], field['value'][0])


def buildImitationObjects(event):
    dev = imitationDevice(event)
    evt = imitationEvent(event)
    elem = imitationElement(event)
    sub_elem = imitationSubElement(event)
    zp_det = imitationEventDetails(event)
    return (dev, evt, elem, sub_elem, zp_det)


def checkEvent(event, trigger):
    dev, evt, elem, sub_elem, zp_det = buildImitationObjects(event)
    testFunction = eval('lambda dev, evt, elem, sub_elem, zp_det: ' + trigger)
    result = testFunction(dev, evt, elem, sub_elem, zp_det)
    return result


def buildEvent(event):
    """
    Only an event formatted like a to_dict(_zepRawEvent) should be passed here
    Example:
    {
        'severity': 4,
        'agent': u'zenping',
        'event_class': u'/Status/Heartbeat',
        'created_time': 1489153711064L,
        'details': [
            {'name': u'zenoss.device.production_state', 'value': [u'1000']}
        ],
        'summary': u'localhost zenping heartbeat failure',
        'uuid': u'000c296a-eaca-a595-11e7-05983f25d037',
        'actor': {
            'element_identifier': u'localhost',
            'element_sub_type_id': 2,
            'element_type_id': 1,
            'element_sub_identifier': u'zenping'
        },
        'monitor': u'localhost'
    }
    """
    actor = event.get('actor', {})
    element = actor.get('element_identifier', '')
    subElement = actor.get('element_sub_identifier', '')
    eventDetails = dict(
        device=element,
        component=subElement,
        eventClass=event.get('event_class'),
        severity=event.get('severity'),
        eventKey=event.get('event_key'),
        eventClassKey=event.get('event_class_key'),
        eventReplayInfo="Replayed from %s" % event.get('uuid'),
    )
    details = event.get('details', [])

    remapDetails = {
        'zenoss.device.ip_address': 'ipAddress',
        'zenoss.device.device_class': 'DeviceClass',
        'zenoss.device.location': 'Location',
    }
    remapDetailLists = {
        'zenoss.device.systems': 'Systems',
        'zenoss.device.groups': 'DeviceGroups',
    }
    remapDetailInts = {
        'zenoss.device.production_state': 'prodState',
        'zenoss.device.priority': 'DevicePriority',
    }

    for field in details:
        if field['name'] in remapDetails:
            eventDetails[remapDetails.get(field['name'])] = field['value'][0]
            continue
        elif field['name'] in remapDetailLists:
            eventDetails[remapDetailList.get(field['name'])] = field['value']
            continue
        elif field['name'] in remapDetailInts:
            eventDetails[remapDetailInts.get(field['name'])] = int(field['value'][0])
            continue
        # For some reason the event details values are always a list
        # This puts us in an awkward situation if it is supposed to be a list or not
        if len(field['value']) > 1:
            value = field['value']
        else:
            value = field['value'][0]
        eventDetails[field['name']] = value

    itemsToRemove = [
        'actor',
        'created_time',
        'details',
        'event_key',
        'created_time',
        'event_class',
        'first_seen_time',
        'event_class_key',
        'uuid',
    ]

    for i in itemsToRemove:
        if i in event:
            _ = event.pop(i)

    for key, value in event.iteritems():
        eventDetails[key] = value

    return eventDetails

