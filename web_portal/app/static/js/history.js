            
	function setupData() {
		$(document).ready(function () {
            stationId = model.stationId;
			var table = $('#stationHistoryTable').DataTable({
				"ajax": {
					"url": "/getStationHistoryList/" + stationId,
					"dataType": "json",
					"dataSrc": "data",
					"contentType":"application/json"
				},
				"columns": [
					{"data": "id"},
					{"data": "temp"},
					{"data": "date"},
					{"defaultContent": "<button class='fancy-button'>Ištrinti</a>"}
				]
			});

			$('#stationHistoryTable tbody').on( 'click', 'button', function () {
				var data = table.row( $(this).parents('tr') ).data();
				var id = data.id

				$.ajax({
					url: "/deleteHistoricalData/" + id,
					type: "POST",
				   success: function(){
						alert("Įrašas pašalintas!")
				   },
					error: function() {
						alert("Įvyko klaida!")
					}
				  });
			});
		});
	}

	$(window).on( "load", setupData );