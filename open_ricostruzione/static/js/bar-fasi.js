function formatPercentage(percentage) {
    if (percentage < 0.01) {
        return 'minore di ' + Highcharts.numberFormat(0.01) + '%';
    } else {
        return Highcharts.numberFormat(percentage) + '%';
    }
}

$(function () {

    if (typeof fasi_data_array === 'undefined' )
        return;

    var hasTouch = !!('ontouchstart' in window);

    var color_array = {
        '1': '#5eb3e4',
        '2': '#1f8fcf',
        '3': '#149350',
        '4': '#d2312c'
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
            backgroundColor: 'rgb(255, 255, 255)',
            borderColor: 'rgb(255, 0, 0)',
            borderWidth: 1,
            borderRadius: 4,
            shadow:false,
            style: {
                zIndex: '999999 !important',
                overflow: 'visible',
                padding: 10
            }
//            formatter: function() {
//                var txt = '';
//
////                txt += '<div style="color: ' + this.series.color + '">';
////                txt += '<div style="font-size: 18px">' + this.series.name + ': ' + formatPercentage(this.percentage) + '</div>';
////                txt += '<div>Importi impegnati: € ' + Highcharts.numberFormat(this.y) + '</div>';
////                txt += '<div>Totale progetti: ' + Highcharts.numberFormat(this.point.num, 0) + '</div>';
////                txt += '<div><a href="' + this.point.url + '">» Vedi tutti</a></div>';
////                txt += '</div>';
//                return txt;
//            }
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