from . import zenpacklib


CFG = zenpacklib.load_yaml()


import logging
from . import schema

from Products.ZenModel.DataRoot import DataRoot
from Products.ZenModel.UserSettings import UserSettingsManager
from Products.ZenModel.ZenPackManager import ZenPackManager
from Products.ZenModel.ZenossInfo import ZenossInfo


LOG = logging.getLogger('zen.EventReplay')

_PROPERTIES = [
    ('eventReplayRedisServer', 'localhost', 'string'),
    ('eventReplayRedisPort', 16379, 'int'),
    ('eventReplayRedisDB', 15, 'int'),
    ('eventReplayLimit', 4000, 'int'),
    ('eventReplayState', False, 'bool'),
    ('eventReplayFilter', "", 'string'),
]


class ZenPack(schema.ZenPack):
    def install(self, app):
        super(ZenPack, self).install(app)
        LOG.info("Adding new DMD properties")
        self.addNewProperties(app)
        LOG.info("Finished")

    def remove(self, app, leaveObjects=False):
        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)
        if not leaveObjects:
            dmd = app.zport.dmd
            dmd.manage_delProperties(ids=[x[0] for x in _PROPERTIES])

    def addNewProperties(self, app):
        dmd = app.zport.dmd
        for name, value, type in _PROPERTIES:
            if not hasattr(dmd, name):
                dmd.manage_addProperty(id=name, value=value, type=type)


# add ldap config to the data root factory type information.
# This adds the LDAP menu on the Advanced -> Settings
action = dict(
    id='manageEventReplayConfig',
    name='Event Replay',
    action='manageEventReplayConfig',
    permissions=("Manage DMD",)
)

userAction = action.copy()
userAction['action'] = '../manageEventReplayConfig'

zenossInfoAction = action.copy()
zenossInfoAction['action'] = '../dmd/manageEventReplayConfig'

actions = DataRoot.factory_type_information[0]['actions']
DataRoot.factory_type_information[0]['actions'] = actions + (action,)

actions = UserSettingsManager.factory_type_information[0]['actions']
UserSettingsManager.factory_type_information[0]['actions'] = actions + (userAction,)

actions = ZenPackManager.factory_type_information[0]['actions']
ZenPackManager.factory_type_information[0]['actions'] = actions + (userAction,)

actions = ZenossInfo.factory_type_information[0]['actions']
ZenossInfo.factory_type_information[0]['actions'] = actions + (zenossInfoAction,)

