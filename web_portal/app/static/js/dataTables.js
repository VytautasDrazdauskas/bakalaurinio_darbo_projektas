function loadProfileTable() {
    $(document).ready(function () {

        var table = $('#profilesTable').DataTable({
            "ajax": {
                "url": "/adminPanel/getProfilesList",
                "dataType": "json",
                "dataSrc": "data",
                "contentType":"application/json",
                "error": function (xhr){
                    notification("Klaida: " + xhr.responseText, 5000);
                }  
            },
            "columns": [
                {"data": "email"},
                {"data": "name"},
                {"data": "devCount"},
                {"data": "uuid"},
                {"defaultContent": "<button class='fancy-button'>Prietaisai</button>"},
                {"defaultContent": "<input type='button' class='fancy-button' value='Redaguoti'></input>"}
            ]
        });

        $('#profilesTable tbody').on( 'click', 'button', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.id

            window.location = "/adminPanel/profileDevices/" + id;	
        });

        $('#profilesTable tbody').on( 'click', 'input', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.id

            window.location = "/adminPanel/profileEdit/" + id;	
        });
    });
}


function loadDevicesTable() {
    $(document).ready(function () {

        var table = $('#devicesTable').DataTable({
            "ajax": {
                "url": "/adminPanel/getDevicesList",
                "dataType": "json",
                "dataSrc": "data",
                "contentType":"application/json",
                "error": function (xhr){
                    notification("Klaida: " + xhr.responseText, 5000);
                }  
            },
            "columns": [
                {"data": "mac"},
                {"data": "uuid"},
                {"data": "user"},
                {"data": "state"},
                {"defaultContent": "<button class='fancy-button'>Perkrauti</button>"}
            ]
        });

        $('#devicesTable tbody').on( 'click', 'button', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.id

            window.location = "/adminPanel/device/" + id;	
        });
       
    });
}

function loadUserDevicesTable() {
    $(document).ready(function () {

        var table = $('#userDevicesTable').DataTable({
            "ajax": {
                "url": "/getUserDevicesList",
                "dataType": "json",
                "dataSrc": "data",
                "contentType":"application/json",
                "error": function (xhr){
                    notification("Klaida: " + xhr.responseText, 5000);
                }  
            },
            "columns": [
                {"data": "deviceName"},
                {"data": "mac"},
                {"data": "state"},
                {"data": "dateAdded"},
                {"data": "deviceTypeName"},
                {"defaultContent": "<button1 class='fancy-button'>Peržiūrėti</button1>"}      
            ]
        });

        $('#userDevicesTable tbody').on( 'click', 'button1', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.id

            window.location = "/userDevices/deviceControlPanel/" + id;	//perziuros langas
        });       
    });
}


function loadUserDeviceDataTable() {
    $(document).ready(function () {
        var deviceId = window.location.href.split("deviceEdit/")[1];

        $('#userDeviceDataTable').DataTable({
            "ajax": {
                "url": "/getUserDeviceData/" + deviceId,
                "dataType": "json",
                "dataSrc": "data",
                "contentType":"application/json",
                "error": function (xhr){
                    notification("Klaida: " + xhr.responseText, 5000);
                }  
            },
            "columns": [
                {"data": "ledState"},
                {"data": "temp"},
                {"data": "date"}
            ],
            "order": [
                [ 2, "asc" ]
            ]
        });  
    });
}

