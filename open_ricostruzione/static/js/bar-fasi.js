$(function () {

    if (typeof fasi_data_array === 'undefined' )
        return;

    var hasTouch = !!('ontouchstart' in window);

    var color_array = {
        '1': '#0ee832',
        '2': '#0cbe2a',
        '3': '#09ae24'
    };

    for (var color, i = 0; i < fasi_data_array.length; i++) {
        fasi_data_array[i]['color'] = color_array[fasi_data_array[i]['code']];
    }

    $('#bars').highcharts({
        chart: {
            type: 'bar',
            height: 180
        },
        series: fasi_data_array,
        legend: {
            verticalAlign: 'top'
        },
        tooltip: {
            useHTML: true,
            backgroundColor: 'rgb(0, 0, 0)',
            borderColor: '#000',
            color: '#ffffff',
            borderWidth: 1,
            borderRadius: 4,
            shadow:false,
            style: {
                zIndex: '999999 !important',
                overflow: 'visible',
                padding: 10
            },

            formatter: function() {
                var txt = '';

                txt += '<div style="color:#fff">';
                txt += '<div style="font-size: 18px">' + this.series.name + ': ' + formatPercentage(this.percentage) + '</div>';
                txt += '<div>Importi impegnati: € ' + Highcharts.numberFormat(this.point.sum) + '</div>';
                txt += '<div>Totale progetti: ' + Highcharts.numberFormat(this.point.y, 0) + '</div>';
                txt += '<div><a  style="color:#fff" href="' + this.point.url + '">» Vedi tutti</a></div>';
                txt += '</div>';
                return txt;
            }
        },
        xAxis: {
            title: null,
            lineWidth: 0,
            gridLineWidth: 0,
            tickWidth: 0,
            labels: {
                enabled: false
            }
        },
        yAxis: {
            reversedStacks: false,
            title: null,
            lineWidth: 0,
            gridLineWidth: 0,
            tickWidth: 0,
            labels: {
                enabled: false
            }
        },
        plotOptions: {
            series: {
                pointWidth: 80,
                stacking: 'percent',
                cursor: !hasTouch ? 'pointer' : 'default',
                point: {
                    events: {
                        click: function() {
                            if (!hasTouch) {
                                location.href = this.options.url;
                            }
                        }
                    }
                }
            }
        }
    });
});