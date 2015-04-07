/**
 * Created by stefano on 3/11/15.
 */

var chart_initialization = false;

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

function initmap(bounds, center, territorio_label) {

        var map;
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
        map.addLayer(osm);
        L.marker([center.lat,center.lon]).addTo(map)
            .bindPopup('Comune di '+territorio_label+'<br>')
            .openPopup();
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