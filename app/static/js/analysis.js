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

var Analysis = (function() {

    var db = {};

    return {

        validate: function(data) {
            return data && data['params'] && data['counts'];
        },

        start: function(data) {
            db = data;
            notice("ANALYSIS IS RUNNING!", data['counts'])
        },

    }

})();


$(document).ready(function() {
    $.ajax('/apm/log_jsonSoA/' + logUUID).then(function(data, status, xhr) {
            $("#bar_loader").hide();

            if (!Analysis.validate(data)) {
                notice("The received log data is invalid.", {'Now what?':'Please report this to njoubert@gmail.com'});
            } else {
                Analysis.start(data);
            }

        }).fail(function(xhr, status, error) {

            $("#bar_loader").hide();
            notice("Unfortuately an error occured while attempting to load the log!", {'Status':status, 'Error':error});

        });  
})