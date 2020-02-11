function selectElement(id, valueToSelect) {    
    let element = document.getElementById(id);
    element.value = valueToSelect;
}

//Klaidos ir informaciniai pranešimai
function fadeIn(el){
    var steps = 0;
    document.body.appendChild(el);
    var timer = setInterval(function() {
        steps++;
        el.style.opacity = 0.05 * steps;
        if(steps >= 20) {
            clearInterval(timer);
            timer = undefined;
        }
    }, 20);
}

function fadeOut(el){
    var steps = 20;
    var timer = setInterval(function() {
        steps--;
        el.style.opacity = 0.05 * steps;
        if(steps == 0) {
            clearInterval(timer);
            timer = undefined;
            el.parentNode.removeChild(el);
        }
    }, 20);
    
}

function createLoader(){
    if (!$("#loader-div")[0]){
        var el = document.createElement("div");
        el.setAttribute("class","loader");
        el.setAttribute("id","loader-div");
        //fadeIn(el);
        document.body.appendChild(el);
        el.style.opacity=1;

        //uztemdom ekrana
        var overlay = document.createElement("div");
        overlay.setAttribute("class","overlay");
        document.body.appendChild(overlay);
        overlay.style.opacity=1;
        //fadeIn(overlay);
    }
}

function removeLoader(){
    var elements = document.getElementsByClassName("loader");
    for (var i = 0; i < elements.length; i++){
        //fadeOut(elements[i]);
        elements[i].style.opacity = 0;
        elements[i].parentNode.removeChild(elements[i]);
    }
    //atstatom ekrana
    var overlays = document.getElementsByClassName("overlay");
    for (var i = 0; i < overlays.length; i++){
        //fadeOut(overlays[i]);
        overlays[i].style.opacity = 0;
        overlays[i].parentNode.removeChild(overlays[i]);
    }
}

function notification(msg,duration){
    var el = document.createElement("div");
    el.setAttribute("class","notification-box");

    var text = document.createElement("h1");
    text.setAttribute("class","otification-textnotification-text");

    text.innerHTML = msg;
    el.appendChild(text);
    el.style.opacity = 0;

    setTimeout(function(){
        fadeOut(el);        
    },duration);
    fadeIn(el);
}

function notificationDanger(msg,duration)
{
    var el = document.createElement("div");    
    el.setAttribute("class","notification-box-danger");

    var text = document.createElement("h1");
    text.setAttribute("class","otification-textnotification-text");

    text.innerHTML = msg;
    el.appendChild(text);

    setTimeout(function(){
        fadeOut(el);
    },duration);
    fadeIn(el);
}

function getResponseMessage(response){
    var success = JSON.parse(response).success
    var message = JSON.parse(response).message
    if (success != null && message != null)
        if(success){
            notification(message,2000);
        }
        else{
            notificationDanger(message,5000);
        }    
    else{
        notificationDanger(response.rensponseText,5000);
    }
}

function getErrorMessage(response){
    var message = response.responseText
    var code = response.status
    notificationDanger("Klaidos: " + message, 5000);
}

function GetBoolean(data){            
    if (data == "True" || data == "1" || data =="Yes" || data =="yes"){
        return true;
    }
    else{
        return false
    }
}

function ControlDevice(device_id, command){
    createLoader()
    $.ajax({
        url: '/device-action',
        type: 'POST',
        data: {
            'device_id': device_id,
            'command': command,
        },
        success: function(response) {
            removeLoader()
            getResponseMessage(response); 
        },
        error: function(error) {
            removeLoader()
            getErrorMessage(error)
        }
    });
    
}

function ConfigDevice(device_id, type, data){
    createLoader()
    $.ajax({
        url: '/configure-device',
        type: 'POST',
        data: {
            'device_id': device_id,
            'type': type,
            'data': data
        },
        success: function(response) {
            removeLoader()
            getResponseMessage(response); 
        },
        error: function(error) {
            removeLoader()
            getErrorMessage(error)
        }
    });
    
}

$(document).ready(function () {
    //Submit mygtuko veiksmai
    $('form').submit(function (e) {
        createLoader();
    });

    $('#refresh-btn').on('click', function() {
        createLoader();
    });
});

