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
        }
    }, 20);
}

function notification(msg,duration)
{
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
            notification(message,5000);
        }    
    else{
        notification(response.rensponseText);
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

function ControlDevice(deviceId, command){
    $.ajax({
        url: '/deviceAction/' + deviceId + '/' + command,
        type: 'GET',
        success: function(response) {
            getResponseMessage(response); 
        },
        error: function(error) {
            getErrorMessage(error)
        }
    });
}


