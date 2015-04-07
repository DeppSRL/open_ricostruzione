/**
 * Created by stefano on 3/11/15.
 */

var chart_initialization = false;
var map;
var geojson;
var map_info;

function init_highcharts(){
    // Radialize the colors
    Highcharts.getOptions().colors = Highcharts.map(Highcharts.getOptions().colors, function (color) {
        return {
            radialGradient: { cx: 0.5, cy: 0.3, r: 0.7 },
            stops: [
                [0, color],
                [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
            ]
        };
    });
    chart_initialization = true;
}

function paint_chart(pie_title, container_id, data) {

    if(chart_initialization == false)
        init_highcharts();


    // Build the chart
    $("#"+container_id).highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: pie_title
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.2f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.2f} %',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    },
                    connectorColor: 'silver'
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Percentuale',
            data: data
        }]
    });
}


/* initmap
*   sets bounds, zoom and center for Leaflet map
*
* */
function initmap(bounds, center) {

    // create the tile layer with correct attribution
    var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    var osm = new L.TileLayer(osmUrl, {minZoom: 11, maxZoom: 18, attribution: osmAttrib});


    //set map bounds
    var southWest = L.latLng(bounds.sw.lat,bounds.sw.lon);
    var northEast = L.latLng(bounds.ne.lat,bounds.ne.lon);

    // set up the map
    map = new L.Map('map').setMaxBounds(L.latLngBounds(southWest, northEast));
    map.scrollWheelZoom.disable();

    // start the map on the Territorio lat/lon
    map.setView(new L.LatLng(center.lat,center.lon),13);
    // add map attribution
    map.addLayer(osm);

}

/*localita_map
* create simple localita map. sets bounds and center, adds marker on center
* */

function localita_map(bounds, center, territorio_label){
    initmap(bounds, center);


    L.marker([center.lat,center.lon]).addTo(map)
        .bindPopup('Comune di '+territorio_label+'<br>')
        .openPopup();
}



function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera) {
        layer.bringToFront();
    }

    map_info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    map_info.update();
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

function style(feature) {
    return {
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7,
        fillColor: getColor(feature.properties.value)
    };
}


function thematic_map(bounds, center, comuniEmilia){
    initmap(bounds, center);
    // control that shows state map_info on hover
    map_info = L.control();

    map_info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'map_info');
        this.update();
        return this._div;
    };

    map_info.update = function (props) {
        this._div.innerHTML = '<h4>Danno del sisma</h4>' +  (props ?
            '<b>' + props.label + '</b><br />' + props.value+ ' Euro'
            : 'Passa sopra un Comune');
    };

    map_info.addTo(map);
    geojson = L.geoJson(comuniEmilia, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

    map.attributionControl.addAttribution('');

}

!function($){

    $(document).ready(function(){
        // Fix input element click problem
        // http://mifsud.me/adding-dropdown-login-form-bootstraps-navbar/
        $('.dropdown input, .dropdown label').click(function(e) {
            e.stopPropagation();
        });

        $(".autosubmit input, .autosubmit select").on("change", function() {
            $(this).parents('form:first').submit();
        });
    });

}(jQuery);