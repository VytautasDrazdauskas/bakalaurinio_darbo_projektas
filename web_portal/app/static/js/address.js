function setupData() {
    $(document).ready(function () {
        var table = $('#addressTable').DataTable({
            "ajax": {
                "url": "/getAddressList",
                "dataType": "json",
                "dataSrc": "data",
                "contentType":"application/json"
            },
            "columns": [
                {"data": "locationId"},
                {"data": "address"},
                {"data": "coordinates"},
                {"defaultContent": "<button class='fancy-button'>Redaguoti</button>"}
            ]
        });

        $('#addressTable tbody').on( 'click', 'button', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.locationId

            window.location = "/editAddress/" + id;	
        });
    });
}

$(window).on( "load", setupData );

