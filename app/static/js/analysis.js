/*
 * Entrypoint for the analysis page
 */

var notice = function(string, dict) {

    var str = "<p>";
    for (i in dict) {
        str += (i + ": " + dict[i] + "<br/>");
    }
    str += "</p>"
    $("#notice").html("<h4>" + string + "</h4>" + str);

}

var AnalysisManager = (function() {

    var db = {};

    var analysis = [];

    return {

        validate: function(data) {
            return data && data['params'] && data['counts'];
        },

        start: function(data) {
            db = data;
            //notice("ANALYSIS IS RUNNING!", data['counts']);
            window.db = db;
            for (var i = 0; i < analysis.length; i++) {
                if (analysis[i].validate(db)) {
                    analysis[i].run(db);
                } else {
                    analysis[i].fails();
                    
                }
            }

        },

        addAnalysis: function(a) {
            analysis.push(a);
        }

    }

})();

var Analysis = {
    
    analysisTitle: '',
    selector: null,
    requires: '',

    render: function(data) { 
        document.getElementById(this.selector).innerHTML = 
            '<h3>Analysis: ' + this.analysisTitle + '</h3>'
            + '<div class="analysis-results">' + data + '</div>' 
    },

    validate: function(db) { return true },

    run: function() {},

    fails: function(reason) { render(); },
}

/************ COUNTS ************/
var CountsAnalysis = AnalysisManager.addAnalysis(_.extend({}, Analysis, {

    analysisTitle: 'Message types present in Logfile',

    selector: 'counts-analysis',

    requires: 'Logfile needs to contain SBP-type messages.',

    requires: function(db) {
        return db['params'];
    },

    run: function(db) {

        this.render(
            ''+
            (db['counts']['PARM'] || 0) + ' Parameters (<i>PARM</i>) <br/>' +            
            (db['counts']['SBPH'] || 0) + ' SBP Health Messages (<i>SBPH</i>) <br/>' +
            (db['counts']['SBPL'] || 0) + ' SBP GPS Location Messages (<i>SBPL</i>) <br/>' +
            (db['counts']['SBPB'] || 0) + ' SBP Baseline Messages (<i>SBPB</i>) <br/>' +
            (db['counts']['GPS'] || 0) + ' Primary GPS Messages (<i>GPS</i>) <br/>' +
            (db['counts']['GPS2'] || 0) + ' Secondary GPS Messages (<i>GPS2</i>) <br/>'
        );
    },

}));

/************ Params ************/
var ParmAnalysis = AnalysisManager.addAnalysis(_.extend({}, Analysis, {

    analysisTitle: 'ArduPilot Parameter Values',

    selector: 'parm-analysis',

    requires: 'Logfile needs to contain Parameters',

    requires: function(db) {
        return db['counts'];
    },

    run: function(db) {
        this.render(
            ''

        );
    },

}));


$(document).ready(function() {
    $.ajax('/apm/log_jsonSoA/' + logUUID).then(function(data, status, xhr) {
            $("#bar_loader").hide();

            if (!AnalysisManager.validate(data)) {
                notice("The received log data is invalid.", {'Now what?':'Please report this to njoubert@gmail.com'});
            } else {
                AnalysisManager.start(data);
            }

        }).fail(function(xhr, status, error) {

            $("#bar_loader").hide();
            notice("Unfortuately an error occured while attempting to load the log!", {'Status':status, 'Error':error});

        });  
})