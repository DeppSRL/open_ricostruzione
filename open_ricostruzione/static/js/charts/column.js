$(function () {
    
    //var url = 'dati-grafico-column.json';
    //var array_categories =[];
    //var array_data =[];
    //
    //$.ajax({
    //    type: 'POST',
    //    url: url,
    //    async: false,
    //    contentType: "application/json",
    //    dataType: 'json',
    //    success: function (json) {
    //        $.each(json, function (key, data) {
    //            $.each(data, function (index, data) {
    //                //console.log('index', data.valore)
    //                array_categories.push(data.etichetta);
    //                array_data.push(parseFloat(data.valore));
    //            })
    //        })        
    //    },
    //    error: function (e) {
    //        alert('error');
    //        console.log(e);
    //    }
    //});
    //

    
    var array_etichetta_column = []; 
    var array_data_column = [];
    var array_data_column2 = [];
    var array_data_column3 = [];
        //stefano fix
    if (typeof data_array_programmazione == 'undefined') {
        return;

    }
    
    for (var k in data_array_programmazione){
            var obj = data_array_programmazione[k];
            
            //console.log(obj);
            //console.log(obj.programmati);
            
            array_etichetta_column.push(obj.label); //etichette
            array_data_column.push({ y : parseFloat(obj.programmati),
                                   link: obj.link,
                                   programmati_ita: obj.programmati_ita,
                                   pianificati_ita: obj.pianificati_ita,
                                   attuali_ita: obj.attuali_ita,
                                   interventi_programmati : obj.interventi_programmati_ita,
                                   interventi_pianificati : obj.interventi_pianificati_ita,
                                   interventi_attuali : obj.interventi_attuali_ita,
                                   classe: obj.classe
                                   });  //programmati
            
            array_data_column2.push({ y : parseFloat(obj.pianificati),
                                   link: obj.link,
                                   programmati_ita: obj.programmati_ita,
                                   pianificati_ita: obj.pianificati_ita,
                                   attuali_ita: obj.attuali_ita,
                                   interventi_programmati : obj.interventi_programmati_ita,
                                   interventi_pianificati : obj.interventi_pianificati_ita,
                                   interventi_attuali : obj.interventi_attuali_ita,
                                   classe: obj.classe
                                   });  //pianificati
            
            array_data_column3.push({ y : parseFloat(obj.attuali),
                                   link: obj.link,
                                   programmati_ita: obj.programmati_ita,
                                   pianificati_ita: obj.pianificati_ita,
                                   attuali_ita: obj.attuali_ita,
                                   interventi_programmati : obj.interventi_programmati_ita,
                                   interventi_pianificati : obj.interventi_pianificati_ita,
                                   interventi_attuali : obj.interventi_attuali_ita,
                                   classe: obj.classe
                                   });  //attuali
    }

    $('#columns').highcharts({
        chart: {
            type: 'column',
            backgroundColor: 'transparent'
        },
        title: {
            text: ''
        },
        subtitle: {
            text: ''
        },
        xAxis: { // ETICHETTE X
            categories: array_etichetta_column
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Euro'
            }
        },
        tooltip: { // QUI QUELLO CHE APPARE NEL TOOLTIP
            followPointer: false,
            borderWidth: 0,
            shadow:false,
            style: {
                zIndex: '999999 !important',
                overflow: 'visible',
                padding:0,
                margin:0
            },
            headerFormat: '',
            formatter: function() {
                //console.log("poinnnnttt", this.x);
                return "<h3><i class='ico-settori green "+this.points[0].point.classe+"'></i> "+ this.x +" </h3>" +
                            "<table>"+
                            "<tr><td stule='text-align:left; width:20%'><strong>" + this.points[0].point.interventi_programmati + "</td><td>Interventi programmati</strong></td><td style='text-align:right'> <strong>"+this.points[0].point.programmati_ita+" €</strong></td></tr>"+
                            "<tr><td stule='text-align:left; width:20%'><strong>" + this.points[0].point.interventi_pianificati +"</td><td>Interventi pianificati</strong></td><td style='text-align:right'> <strong>"+this.points[1].point.pianificati_ita+" €</strong></td></tr>"+
                            "<tr><td stule='text-align:left; width:20%'><strong>" + this.points[0].point.interventi_attuali +"</td><td>Interventi attuati***</strong></td><td style='text-align:right'> <strong>"+this.points[2].point.attuali_ita+" €</strong></td></tr>"+
                            "<tr><td colspan='3'><a href='"+this.points[0].point.link+"' style='text-aligh:right'><strong>» Vedi tutti</strong></a></td></tr>"+
                            "</table>";
							
                },
            footerFormat: '',
            shared: true,
            useHTML: true,
            positioner: function(boxWidth, boxHeight, point) {
                return {
                    x: point.plotX - 160,
                    y: -30
                };
            }

        },
        //tooltip: { // QUI QUELLO CHE APPARE NEL TOOLTIP
        //    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        //    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        //        '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
        //    footerFormat: '</table>',
        //    shared: true,
        //    useHTML: true
        //},
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0,
                events: {
                    mouseOver: function () {
                        $('.highcharts-tooltip span').css("display","block");
                    }
                }
            },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function () {
                           // alert('Category: ' + this.category + ', value: ' + this.y);
                        }
                    }
                }
            }

        },
        series: [{
            name: 'Programmati', // NOME COLONNA
            data: array_data_column,
            color: "#ED450A" // orange
        },
        {
            name: 'Pianificati', // NOME COLONNA
            data: array_data_column2,
            color: '#F4E73D' // yellow
        },
        {
            name: 'Attuati', // NOME COLONNA
            data: array_data_column3,
            color: '#059e1e' // green
        }
        ]
    });
    


});