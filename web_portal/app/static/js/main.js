function selectElement(id, valueToSelect) {    
    let element = document.getElementById(id);
    element.value = valueToSelect;
}

function notification(msg,duration)
{
    var el = document.createElement("div");
    el.setAttribute("class","notification-box");
    el.innerHTML = msg;
    setTimeout(function(){
        el.parentNode.removeChild(el);
    },duration);
    document.body.appendChild(el);
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
    notification("Klaidos: " + message, 5000);
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

//bendri mygtukai
