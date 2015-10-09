$(function () {
    
    
    // Monocromo
    Highcharts.getOptions().plotOptions.pie.colors = (function () {
        var colors = ['#75910c', '#7faa0b', '#a1c22d', '#89876D', '#cdcd95', '#007A00', '#ccdd66', '#666666', '#cecbbe', '#99ff33','#99cc66','#99FF99','#009933','#339933','#336600'];

        return colors;
    }());


    //stefano fix
    if (typeof data_array_pie !== 'undefined') {

        // Build the chart
        $('#pie').highcharts({
            credits: {
                enabled: false
            },
            chart: {
                backgroundColor: 'rgba(0,0,0,0)',
                plotBorderWidth: 0,
                plotShadow: false,
                height: 250
            },
            title: {
                text: ''
            },
            tooltip: {
                //pointFormat: '{point.y} ({point.percentage:.1f}%)</b><br/><a href="{point.url}">Vai alla pagina</a><br/>', // QUI QUELLO CHE APPARE NEL TOOLTIP
                pointFormat: '{point.y} ({point.percentage:.1f}%)</b><br/><a href="{point.url}"></a><br/>', // QUI QUELLO CHE APPARE NEL TOOLTIP
                followPointer: false,
                backgroundColor: '#fff',
                borderRadius: 10

            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false,

                       // format: '<b>{point.name}</b><br/><b>{point.value} ({point.percentage:.1f}%)</b><br/><a href="{point.url}">Vai alla pagina</a><br/>',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: '',
                stickyTracking: false,
                point: {
                    events: {
                        click: function(e) {
                            //this.slice();
                            console.log(e.point);
                            location.href = e.point.url;
                            e.preventDefault();
                        }
                    }
                },
                data: data_array_pie
            }]
        });
    }

});