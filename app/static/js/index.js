/*
 * Entrypoint for the index page.
 */

$(document).ready(function() {

    console.log("haha")

    $("#upload_log_form").submit(function(e) {
        $("#loader_img").show();
        $("#upload_button").hide();
    })

})