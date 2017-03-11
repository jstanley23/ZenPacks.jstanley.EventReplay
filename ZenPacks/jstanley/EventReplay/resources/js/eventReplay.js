Ext.onReady(function(){
Ext.ns("Zenoss.CheckTrigger.dialogs")

var gridId = "events_grid";

function getSelectedEventReplayIds() {
    var grid = Ext.getCmp(gridId),
        selected = grid.selModel.getSelection();
    return Ext.pluck(Ext.Array.map(selected, function(value, ind, array) { return value.getData() }), 'evid');
}
function getSelectedEvents() {
    var grid = Ext.getCmp(gridId);
    return grid.getSelectionModel().getSelection();
}

function replayEvents() {
    Zenoss.remote.EventReplayRouter.replay({
        events: getSelectedEvents();
    });
}

var addEventReplayButton = function(event_grid) {
    var eventsToolbar = event_grid.tbar;

    var createEventReplayButton = new Ext.Button({
        id: Ext.id('','create-eventreplay-button'),
        text: 'Event Replay',
        menu: {
            items: [{
                text: 'Replay event',
                tooltip: 'Send raw event back through the system',
                handler: replayEvents(),
            }]
        }
    });

    event_grid.child(0).add(createEventReplayButton);
    return createEventReplayButton;
};

var setupEventReplayButton = function(event_grid) {
    var new_grid = Ext.getCmp('events_grid');
    var createEventReplayButton = addEventReplayButton(new_grid);
    new_grid.on('selectionchange', function(selectionmodel) {
        var newDisabledValue = !selectionmodel.hasSelection() && selectionmodel.selectState !== 'All',
            history_combo = Ext.getCmp('history_combo'),
            archive = Ext.isDefined(history_combo) ? history_combo.getValue() === 1 : false;
        if (archive) {
            createEventReplayButton.setDisabled(true);
        } else {
            createEventReplayButton.setDisabled(newDisabledValue);
        }
    });
    new_grid.on('recreateGrid', setupEventReplayButton)
}

Ext.ComponentMgr.onAvailable('events_grid', setupEventReplayButton);

});

