function treemap_function(args) {

//gestione TOOLTIP
    var number_li_tree = 0;
    var z = 0;
    $(".lista-treemap").html('');
    
    for (z = 0; z < args.length; ++z) {
        console.log("treemap ", args[z]['id']);
        var id_treemap = args[z]['id'];
        var value_treemap = args[z]['value'];
        var url_treemap = args[z]['url'];
		var percentage_treemap = args[z]['percentage'];


        $(".lista-treemap").append('<li><span style="background:'+array_color_treemap[z]+'"> </span><a id="'+id_treemap+'" href="'+url_treemap+'">'+id_treemap+' - '+percentage_treemap+'%</a></li>');
    }
    
    //inserisco i colori nella treemap definiti nell'array
    var y = 0;
    for (y = 0; y < args.length; ++y) {
            //    args[y].push({'color':array_color_treemap[y]});
            args[y]['color'] = array_color_treemap[y];
            console.log(args[y]['color']);
    }

    function getTooltip2(element, x) {
        element.hover(
            function () {
                //console.log("ss", element.attr("id"));
                $('#treemap-stanziati').highcharts().series[0].data[x].setState('hover');
                $('#treemap-stanziati').highcharts().tooltip.refresh($('#treemap-stanziati').highcharts().series[0].data[x]);
            }, 
            function () {
                $('#treemap-stanziati').highcharts().series[0].data[x].setState("");
                $('#treemap-stanziati').highcharts().tooltip.hide();
            }
        );
    }
    
    $(".lista-treemap a").each(function() {
        //gestione tooltip
        getTooltip2($(this), number_li_tree);
        number_li_tree++;
    });
//fine tooltip    
    
    
    
    $('#treemap-stanziati').highcharts({
        credits: {
            enabled: false
        },
        series: [{
            levels: [{
                level: 1,
                layoutAlgorithm: 'stripes',
                borderRadius: 50,
                borderColor: 'black',
                borderWidth: 4
            }],
            dataLabels: {
                enabled: true,
                style: {
                    color: 'black',
                    fontWeight: 'bold',
                    HcTextStroke: '3px rgba(255,255,255,0.5)'
                }
            },
            type: "treemap",
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

            data: args
        }],
        title: {
            text: ''
        },

        plotOptions: {
            treemap: {
                allowPointSelect: true,
                cursor: 'pointer'
            }
        },
        tooltip: {
            headerFormat: '',
            //pointFormat: '<b>{point.id}</b><br/><b>{point.value} ({point.percentage}%)</b><br/><a href="{point.url}">Vai alla pagina</a><br/>',
            //pointFormat: '<b>{point.id}</b><br/><font size="14"><b>{point.value}</b></font> mln<br/><a href="{point.url}">Vai alla pagina</a><br/>',
            pointFormat: '<b>{point.id}</b><br/><font size="14"><b>{point.value}</b></font> mln',
			backgroundColor: '#fff',
			borderRadius: 10,
            useHTML: true
        }

    });

}

treemap_function(data_array_treemap[0]);


