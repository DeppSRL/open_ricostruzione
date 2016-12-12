Highcharts.setOptions({
    title: null,
    credits: {
        enabled: false
    },
    chart: {
        backgroundColor: 'transparent'
    },
    lang: {
        numericSymbols: [null, ' mln', ' mld'],
        decimalPoint: ',',
        thousandsSep: '.'
    }
});

(function( $ ) {
    $.fn.dataLegend = function(options) {
        return this.each(function() {
            var highcharts = $(this).highcharts();

            var data_array = highcharts.series[0].data;
            var tooltip = highcharts.tooltip;

            var container = $(options.container);
            var formatter = options.formatter;

            container.html('');
            for (var i = 0; i < data_array.length; i++) {
                container.append(formatter(data_array[i]));
            }

            container.find('a').each(function(idx, obj) {
                var data = data_array[idx];
                $(obj).hover(
                    function() {
                        data.setState('hover');
                        tooltip.refresh(data);
                    },
                    function() {
                        data.setState('');
                        tooltip.hide();
                    }
                );
            });
        });
    };
}( jQuery ));

function formatPercentage(percentage) {
    if (percentage < 0.01) {
        return 'minore di ' + Highcharts.numberFormat(0.01) + '%';
    } else {
        return Highcharts.numberFormat(percentage) + '%';
    }
}