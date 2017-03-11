import os


def first_of(*choices):
    '''
    Return the first choice that isn't None.
    '''
    for x in choices:
        if x is not None:
            return x


def value_from_conf(conf, name):
    '''
    Return value of named property from given standard configuration.
    '''
    zenhome = os.environ.get('ZENHOME', '/opt/zenoss')
    conf_filename = os.path.join(zenhome, 'etc', '%s.conf' % conf)
    try:
        conf_file = open(conf_filename, 'r')
        for line in conf_file:
            line = line.strip()
            if line.startswith(name):
                return line.split()[1]

        conf_file.close()

    except Exception:
        pass


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
