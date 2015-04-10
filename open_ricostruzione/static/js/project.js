/**
 * Created by stefano on 3/11/15.
 */

var chart_initialization = false;
var map_danno, map_attuazione;
var geojson_danno,geojson_attuazione;
var map_info_danno, map_info_attuazione;


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


/* init_map
*   sets bounds, zoom and center for Leaflet map
*
* */
function init_map(div_id, bounds, center, default_zoom, min_zoom, max_zoom) {

    // create the tile layer with correct attribution
    var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    var osm = new L.TileLayer(osmUrl, {minZoom: min_zoom, maxZoom: max_zoom, attribution: osmAttrib});


    //set map bounds
    var southWest = L.latLng(bounds.sw.lat,bounds.sw.lon);
    var northEast = L.latLng(bounds.ne.lat,bounds.ne.lon);
    var leaf_bounds = L.latLngBounds(southWest, northEast);
    // set up the map
    var map = new L.Map(div_id).setMaxBounds(leaf_bounds);
    map.scrollWheelZoom.disable();

    // start the map on the Territorio lat/lon
    map.setView(new L.LatLng(center.lat,center.lon),default_zoom);
    // add map attribution
    map.addLayer(osm);
    return map;

}

/*localita_map
* create simple localita map. sets bounds and center, adds marker on center
* */

function localita_map(bounds, center, territorio_label){
    var map = init_map('localita_map',bounds, center, 13, 11, 18);


    L.marker([center.lat,center.lon]).addTo(map)
        .bindPopup('Comune di '+territorio_label+'<br>')
        .openPopup();
}

/* THEME MAP FUNCTIONS */

function zoomToFeature(e,geojson, map_info, map) {
    map.fitBounds(e.target.getBounds());
}

function navigateToFeatureURL(e) {
    window.location = e.target.feature.properties.url;
}

function resetHighlight(e, geojson, map_info, map) {
    geojson.resetStyle(e.target);
    map_info.update();
}


function highlightFeature(e,geojson, map_info, map) {
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

function onEachFeature_danno(feature, layer) {
    layer.on('mouseout', function(e){resetHighlight(e,geojson_danno, map_info_danno, map_danno )});
    layer.on('mouseover', function(e){highlightFeature(e,geojson_danno, map_info_danno, map_danno )});
    layer.on('click', function(e){navigateToFeatureURL(e,geojson_danno, map_info_danno, map_danno )});

}

function onEachFeature_attuazione(feature, layer) {
    layer.on('mouseout', function(e){resetHighlight(e,geojson_attuazione, map_info_attuazione, map_attuazione )});
    layer.on('mouseover', function(e){highlightFeature(e,geojson_attuazione, map_info_attuazione, map_attuazione )});
    layer.on('click', function(e){navigateToFeatureURL(e,geojson_attuazione, map_info_attuazione, map_attuazione )});

}


function style_danno(feature) {
    return {
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7,
        fillColor: getColor_danno(feature.properties.value)
    };
}

function style_attuazione(feature) {
    return {
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7,
        fillColor: getColor_attuazione(feature.properties.value)
    };
}

function init_mapinfo(){
    var map_info = L.control();
    map_info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'map_info');
        this.update();
        return this._div;
    };
    return map_info;
}

function thematic_map(map_type, bounds, center, geojson_data){

    var div_id, map_info ;
    
    //if type == 'danno', initialize map type A,
    // else initialize map type B on attuazione
    map_info = init_mapinfo();
    div_id = 'mappa_'+map_type;

    if(map_type == 'danno'){
        map_info.update = function (props) {
            this._div.innerHTML = '<h4>Danno del sisma</h4>' +  (props ?
                '<b>' + props.label + '</b><br />' + props.value+ ' Euro'
                : 'Passa sopra un Comune');
        };
    }
    else{
        map_info.update = function (props) {
        this._div.innerHTML = '<h4>Attuazione</h4>' +  (props ?
            '<b>' + props.label + '</b><br />' + props.value+ ' Euro'
            : 'Passa sopra un Comune');
        };
    }

    
    var map = init_map(div_id, bounds, center, 9, 8, 11);
    // control that shows state map_info on hover


    map_info.addTo(map);
    
    if(map_type == 'danno'){

        map_info_danno= map_info;
        geojson_danno = L.geoJson(geojson_data, {
            style: style_danno,
            onEachFeature: onEachFeature_danno
        }).addTo(map);
        map_danno = map;

    }
    else{
        map_info_attuazione = map_info;
        geojson_attuazione = L.geoJson(geojson_data, {
            style: style_attuazione,
            onEachFeature: onEachFeature_attuazione
        }).addTo(map);
        map_attuazione = map;

    }
    
    map.attributionControl.addAttribution('');
//    add_legend(map);
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