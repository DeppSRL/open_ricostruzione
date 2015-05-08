function chartPieTerr(id, arr, colore) {

    $(function () {
        
        // Monocromo
        Highcharts.getOptions().plotOptions.pie.colors = (function () {
            var colors = [colore, '#666'],
                base = '#b70404', // QUI VA DEFINITO IL COLORE MASTER 
                i;
    
            for (i = 0; i < 10; i += 1) {
                // Start out with a darkened base color (negative brighten), and end
                // up with a much brighter color
                colors.push(Highcharts.Color(base).brighten((i - 3) / 7).get());
            
    
            
            }
            return colors;
        }());
        
    
    
    
    
        // Build the chart
        $('#'+id).highcharts({
            credits: {
                enabled: false
            },
            chart: {
                backgroundColor: 'rgba(0,0,0,0)',
                plotBorderWidth: 0,
                plotShadow: false,
                height: 100,
                width:145,
                marginBottom: 0,
                marginTop:0,
                spacingTop: 0,
                spacingBottom: 0
            },
            title: {
                text: ''
            },
            tooltip: {
                //pointFormat: '{point.y} ({point.percentage:.1f}%)</b><br/><a href="{point.url}">Vai alla pagina</a><br/>', // QUI QUELLO CHE APPARE NEL TOOLTIP
                pointFormat: '{point.y} ({point.percentage:.1f}%)</b><br/><a href="{point.url}"></a><br/>', // QUI QUELLO CHE APPARE NEL TOOLTIP
                followPointer: false,
                backgroundColor: '#fff',
                borderRadius: 10,
                enabled: false
    
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
                point: {
                    events: {
                        click: function(e) {
                            //this.slice();
                            console.log(e.point);
                            //location.href = e.point.url;
                            e.preventDefault();
                        }
                    }
                },
                data: arr
            }]
        });
        
    });
    
    
}