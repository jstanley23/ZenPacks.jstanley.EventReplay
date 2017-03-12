/*****************************************************************************
 * 
 * Copyright (C) Zenoss, Inc. 2010, all rights reserved.
 * 
 * This content is made available according to terms specified in
 * License.zenoss under the directory where your Zenoss product is installed.
 * 
 ****************************************************************************/


Ext.onReady(function() {

    Ext.ns('Zenoss.settings');
    var router = Zenoss.remote.EventReplayRouter;


    function saveConfigValues(results, callback) {
        var values = results.values;
        router.setConfig(results, callback);
    }

    function buildPropertyGrid(response) {
        var propsGrid,
            data;
        data = response.data;

        propsGrid = new Zenoss.form.SettingsGrid({
            renderTo: 'propList',
            width: 500,
            saveFn: saveConfigValues
        }, data);

//        Ext.each(data, function(row){
//            Zenoss.registerTooltipFor(row.id);
//        });

    }

    function loadProperties() {
        router.getConfig({}, buildPropertyGrid);
    }

    loadProperties();

});
