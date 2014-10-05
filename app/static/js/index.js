/*
 * Entrypoint for the index page.
 */

function validateEmail(email) { 
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
} 


var validate_form = function(formdata) {
    var paramObj = {};
    $.each(formdata, function(_, kv) {
        paramObj[kv.name] = kv.value;
    });
    if (paramObj['email'] && !validateEmail(paramObj['email'])) {
        alert('The email you entered doesn\'t appear to be valid!');
        return false;
    }
    return true;
}

$(document).ready(function() {

    $("#upload_log_form").submit(function(e) {
        
        if (validate_form($(this).serializeArray())) {
            $("#loader_img").show();
            $("#upload_button").hide();
        } else {
            e.preventDefault();
        }

    })

})