function setupData() {
    $(document).ready(function () {

        var table = $('#stationTable').DataTable({
            "ajax": {
                "url": "/getStationList",
                "dataType": "json",
                "dataSrc": "data",
                "contentType":"application/json"
            },
            "columns": [
                {"data": "stationId"},
                {"data": "stationName"},
                {"data": "address"},
                {"data": "lastTemp"},
                {"data": "lastUpdate"},
                {"defaultContent": "<button class='fancy-button'>Istorija</button>"},
                {"defaultContent": "<input type='button' class='fancy-button' value='Redaguoti'></input>"}
            ]
        });

        $('#stationTable tbody').on( 'click', 'button', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.stationId

            window.location = "/stationHistory/" + id;	
        });

        $('#stationTable tbody').on( 'click', 'input', function () {
            var data = table.row( $(this).parents('tr')).data();
            var id = data.stationId

            window.location = "/editStation/" + id;	
        });
    });
}
$( window ).on( "load", setupData );