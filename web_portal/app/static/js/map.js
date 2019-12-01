    var map;
    var mapLat = 54.687157;
    var mapLng = 25.279652;
    var mapDefaultZoom = 12;
    var vectorLayer;

    //asinchroniškai gaunami duomenys iš url
    async function getData(url) {
            const response = await fetch(url);            
            return response.json()
        }

    function initialize_map() {
        map = new ol.Map({
            target: "map",
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM({ //iš čia užkrauną žemėlapį
                        url: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    })
                })
            ],
            view: new ol.View({ //Centruojam mapo vaizdą virš vilniaus ir nustatom priartinimą
                center: ol.proj.fromLonLat([mapLng, mapLat]),
                    zoom: mapDefaultZoom
                })
            });
            
            //sumetam pinus ant map'o
            for (i = 0; i < data.data.length; i++) {
                var longitude = data.data[i].longitude
                var latitude = data.data[i].latitude
                var temp = data.data[i].lastTemp
                add_map_point(latitude,longitude,temp)
              }
        }

    function add_map_point(lat, lng, temp) {
        //sukuria markerio layerį
        var marker = new ol.layer.Vector({  //Nustatom koordinačių sistemą
            source:new ol.source.Vector({
                features: [new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.transform([parseFloat(lng), parseFloat(lat)], 'EPSG:4326', 'EPSG:3857')),
                })]
            }),
            style: new ol.style.Style({
            image: new ol.style.Icon({  //užkraunam ikoną ir nustatom poziciją
            anchor: [0.5, 1.1],
            anchorXUnits: "fraction",
            anchorYUnits: "fraction",
            src: "/static/cyan-icon3.png"
                }),
            text: new ol.style.Text({  //prie ikonos prikabinam tekstą
                font: '16px Arial',
                text: temp,
                fill: new ol.style.Fill({
                    color: [0, 0, 0, 1]  //RGB spalvos.
                  })
             })
            })
        });
        map.addLayer(marker);
    }

    function add_new_point(lat, lng) {
        map.removeLayer(vectorLayer) 
        //sukuria markerio layerį
        vectorLayer = new ol.layer.Vector({  //Nustatom koordinačių sistemą
            source:new ol.source.Vector({
                features: [new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.transform([parseFloat(lng), parseFloat(lat)], 'EPSG:4326', 'EPSG:3857')),
                })]
            }),
            style: new ol.style.Style({
                image: new ol.style.Icon({  //užkraunam ikoną ir nustatom poziciją
                anchor: [0.5, 1.0],
                anchorXUnits: "fraction",
                anchorYUnits: "fraction",
                src: "/static/cyan-icon3.png"
                })
            })
        });       
        map.addLayer(vectorLayer);
    }

    function initialize_address_map() {  
        formLat = document.getElementById('latField').value;
        formLng = document.getElementById('lngField').value;
        
        map = new ol.Map({
            target: "map",
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM({ //iš čia užkrauną žemėlapį
                        url: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    })
                })
            ],
            view: new ol.View({ //Centruojam mapo vaizdą virš vilniaus ir nustatom priartinimą
                center: ol.proj.fromLonLat([mapLng, mapLat]),
                    zoom: mapDefaultZoom
                })
            });  
          
        //jei redaguojam adresą, tuomet centruojam ir uždedam pin'ą
        if (formLat != "" && formLng != ""){
            map.getView().setCenter(ol.proj.fromLonLat([formLng, formLat]));
            map.getView().setZoom(16);
            add_new_point(formLat,formLng)
        }
            
          map.on('click', async function(evt){
            var coords = ol.proj.toLonLat(evt.coordinate);
            var latitude = coords[1];
            var longitude = coords[0];
            add_new_point(latitude,longitude)
            document.getElementById('latField').value = latitude;
            document.getElementById('lngField').value = longitude;

            const data_for_url = {lon: longitude, lat: latitude, format: "json", limit: 1};

            // ENCODED DATA for URL
            const encoded_data = Object.keys(data_for_url).map(function (k) {
                return encodeURIComponent(k) + '=' + encodeURIComponent(data_for_url[k])
            }).join('&');

            // FULL URL for searching address of mouse click
            const url = 'https://nominatim.openstreetmap.org/reverse?' + encoded_data;
                                              
            const data = await getData(url);
            
            var street = (typeof data.address.road === "undefined" ? '' : data.address.road + ' ');
            var houseNr = (typeof data.address.house_number === "undefined" ? '' : data.address.house_number + ', ');
            var city = (typeof data.address.city === "undefined" ? '' : data.address.city + ' ');
            var fullAddress = street + houseNr + city;
            document.getElementById('addressField').value = fullAddress;
        });
    }