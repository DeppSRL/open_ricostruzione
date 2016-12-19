//javascript di open-ricostruzione
//NOTE: THIS FILE IS FULL OF BUG FIX FROM STEFANO, DON'T REPLACE WITH GIANGIULIO FILE!!!
    
function gestione_cerchi_top() {
    //########### GESTIONE CERCHI TOP
    var interventi_programmati = parseFloat($(".much.programmati .num").html().replace(",", "."));
    var interventi_pianificati = parseFloat($(".much.pianificati .num").html().replace(",", "."));
    var interventi_attuali = parseFloat($(".much.attuati .num").html().replace(",", "."));
    var totale_interventi = interventi_programmati + interventi_pianificati + interventi_attuali;
    var programmati_percentuale = (interventi_programmati * 100) / totale_interventi ;
    var pianificati_percentuale = (interventi_pianificati * 100) / totale_interventi ;
    var attuali_percentuale = (interventi_attuali * 100) / totale_interventi ; 
    
    //ordino in modo crescente in modo da settare correttamente gli z-index in qualunque caso
    var list = [
                { name: 'programmati', value: programmati_percentuale },
                { name: 'pianificati', value: pianificati_percentuale },
                { name: 'attuali', value: attuali_percentuale }
            ];
    masterList = list.sort(function (a, b) {
        return a.value - b.value;
    });
    masterList.reverse();
    for (item in masterList) {
        $(".interventi ."+masterList[item].name).css("z-index",item);
        //console.log(masterList[item].value);
    }
    
    $(".interventi .programmati").css("height",programmati_percentuale+"%");
    $(".interventi .programmati").css("width",programmati_percentuale+"%");
    $(".interventi .programmati").css("top",(100 - programmati_percentuale) / 2 +"%");
    $(".interventi .pianificati").css("height",pianificati_percentuale+"%");
    $(".interventi .pianificati").css("width",pianificati_percentuale+"%");
    $(".interventi .pianificati").css("top",(100 - pianificati_percentuale) / 2 +"%");
    $(".interventi .attuali").css("height",attuali_percentuale+"%");
    $(".interventi .attuali").css("width",attuali_percentuale+"%");
    $(".interventi .attuali").css("top",(100 - attuali_percentuale) / 2 +"%");
}
  

function gestione_grafico_barre() {
    //########### GESTIONE "GRAFICO BARRE"

//    for (i in data_array_programmazione) {
//        //console.log("altezza",(data_array_programmazione[i].programmati * 100) / totale_interventi_progr);
//        var tot_row = data_array_programmazione[i].programmati + data_array_programmazione[i].pianificati + data_array_programmazione[i].attuali;
//
//        $(".programmazione ."+data_array_programmazione[i].classe + " .interventi-programmati span").html(data_array_programmazione[i].programmati);
//        $(".programmazione ."+data_array_programmazione[i].classe + " .interventi-pianificati span").html(data_array_programmazione[i].pianificati);
//        $(".programmazione ."+data_array_programmazione[i].classe + " .interventi-attuali span").html(data_array_programmazione[i].attuali);
//
//        $(".programmazione ."+data_array_programmazione[i].classe + " .interventi-programmati").css("height",(data_array_programmazione[i].programmati * 100) / tot_row +"%");
//        $(".programmazione ."+data_array_programmazione[i].classe + " .interventi-pianificati").css("height",(data_array_programmazione[i].pianificati * 100) / tot_row +"%");
//        $(".programmazione ."+data_array_programmazione[i].classe + " .interventi-attuali").css("height",(data_array_programmazione[i].attuali * 100) / tot_row +"%");
//
//    }
//    $( ".programmazione > div > div" ).animate({
//        height: "300px"
//    }, 1000, function() {
//      // Animation complete.
//    });
}

function grafico_cerchi_soggetti_attuatori() {
//    $( ".lista-soggetti-attuatori .list-item" ).each(function() {
//        console.log($(this).attr("soggetto"));
//        var soggetto = $(this).attr("soggetto");
//
//        var soggetti_programmati = parseFloat($(".soggetti-attuatori-"+soggetto+" .importo-soggetti-programmati").html().replace(",", "."));
//        var soggetti_pianificati = parseFloat($(".soggetti-attuatori-"+soggetto+" .importo-soggetti-pianificati").html().replace(",", "."));
//        var soggetti_attuali = parseFloat($(".soggetti-attuatori-"+soggetto+" .importo-soggetti-attuati").html().replace(",", "."));
//        var totale_soggetti = soggetti_programmati + soggetti_pianificati + soggetti_attuali;
//        var soggetti_programmati_percentuale = (soggetti_programmati * 100) / totale_soggetti;
//        var soggetti_pianificati_percentuale = (soggetti_pianificati * 100) / totale_soggetti;
//        var soggetti_attuali_percentuale = (soggetti_attuali * 100) / totale_soggetti;
//
//        //ordino in modo crescente in modo da settare correttamente gli z-index in qualunque caso
//        var list = [
//                    { name: 'programmati', value: soggetti_programmati_percentuale },
//                    { name: 'pianificati', value: soggetti_pianificati_percentuale },
//                    { name: 'attuali', value: soggetti_attuali_percentuale }
//                ];
//        masterList = list.sort(function (a, b) {
//            return a.value - b.value;
//        });
//        masterList.reverse();
//        var temp_riferimento = 0;
//        for (item in masterList) {
//            $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("z-index",item);
//            if (item == 0) {
//                $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("height","100%");
//                $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("width","100%");
//                $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("top","0");
//                temp_riferimento = masterList[item].value;
//            } else {
//                $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("height",(masterList[item].value * 100) / temp_riferimento +"%");
//                $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("width",(masterList[item].value * 100) / temp_riferimento +"%");
//                $(".soggetti-attuatori-"+soggetto+" ."+masterList[item].name).css("top",(100 - (masterList[item].value * 100) / temp_riferimento) / 2 +"%");
//            }
//        }
//        });

}

function grafico_pie_soggetti_attuatori() {
        //stefano fix
    if (typeof data_array_pie !== 'undefined') {

        for (i = 0; i < data_array_pie.length; ++i) {
            colore = $("#pie .highcharts-series path:nth-child("+ (i+1) +")").attr("fill");

            $(".lista-pie").append('<li><span style="background:'+colore+'"> </span><a id="'+data_array_pie[i]['name']+'" href="'+data_array_pie[i]['url']+'">'+data_array_pie[i]['name']+'</a></li>');
        }
    }

}

function grafico_pie_donazioni() {

    //stefano fix
    if (typeof data_array_pie_donazioni !== 'undefined') {

        for (i = 0; i < data_array_pie_donazioni.length; ++i) {
            colore = $("#pie-donazioni .highcharts-series path:nth-child("+ (i+1) +")").attr("fill");

            $(".lista-pie-donazioni").append('<li><span style="background:'+colore+'"> </span><a id="'+data_array_pie_donazioni[i]['name']+'" href="'+data_array_pie_donazioni[i]['url']+'">'+data_array_pie_donazioni[i]['name']+'</a></li>');
        }
    }
}


function getTooltip(element, x, id) {
    element.hover(
        function () {
            //console.log("ss", element.attr("id"));
            $('#'+id).highcharts().series[0].data[x].setState('hover');
            $('#'+id).highcharts().tooltip.refresh($('#'+id).highcharts().series[0].data[x]);
        }, 
        function () {
            $('#'+id).highcharts().series[0].data[x].setState("");
            $('#'+id).highcharts().tooltip.hide();
        }
    );
}
    
$( document ).ready(function() {
    // giangiulio new part

    var click = 0;
    var click_cofinanziati = 0;
    var click_liquidati = 0;
    var altezza = "";
    var altezza_cofinanziati = "";
    var altezza_liquidati = "";

    $(".link-dati").on("click", function(e) {
        e.preventDefault();

        if (click == 0) {
            altezza = "200px";
            $( ".freccia-verde" ).css("display","block");
            click = 1;
            $(".link-dati").removeClass("glyphicon-plus-sign");
            $(".link-dati").addClass("glyphicon-minus-sign");
        } else {
            altezza = "0";
            $( ".freccia-verde" ).css("display","none");
            click = 0;
            $(".link-dati").removeClass("glyphicon-minus-sign");
            $(".link-dati").addClass("glyphicon-plus-sign");
        }


        $( ".box-dati" ).animate({
            height: ""+altezza
        }, 300, function() {
          // Animation complete.
        });

    });


    $(".link-dati-cofinanziati").on("click", function(e) {
        e.preventDefault();

        if (click_cofinanziati == 0) {
            altezza_cofinanziati = "250px";
            $( ".freccia-verde-cofinanziati" ).css("display","block");
            click_cofinanziati = 1;
            $(".link-dati-cofinanziati").removeClass("glyphicon-plus-sign");
            $(".link-dati-cofinanziati").addClass("glyphicon-minus-sign");
            $( ".box-dati-cofinanziati" ).css("overflow","visible");

        } else {
            altezza_cofinanziati = "0";
            $( ".freccia-verde-cofinanziati" ).css("display","none");
            click_cofinanziati = 0;
            $(".link-dati-cofinanziati").removeClass("glyphicon-minus-sign");
            $(".link-dati-cofinanziati").addClass("glyphicon-plus-sign");
            $( ".box-dati-cofinanziati" ).css("overflow","hidden");
        }


        $( ".box-dati-cofinanziati" ).animate({
            height: ""+altezza_cofinanziati
        }, 300, function() {
          // Animation complete.
        });

        $( ".box-dati-liquidati" ).animate({
            height: "0"
        }, 300, function() {
          // Animation complete.
        });
        click_liquidati = 0;
        $(".link-dati-liquidati").removeClass("glyphicon-minus-sign");
        $(".link-dati-liquidati").addClass("glyphicon-plus-sign");
        $(".freccia-verde-liquidati" ).css("display","none");
    });


    $(".link-dati-liquidati").on("click", function(e) {
        e.preventDefault();

        if (click_liquidati == 0) {
            altezza_liquidati = "200px";
            $( ".freccia-verde-liquidati" ).css("display","block");
            click_liquidati = 1;
            $(".link-dati-liquidati").removeClass("glyphicon-plus-sign");
            $(".link-dati-liquidati").addClass("glyphicon-minus-sign");
                $( ".box-dati-cofinanziati" ).css("overflow","hidden");

        } else {
            altezza_liquidati = "0";
            $( ".freccia-verde-liquidati" ).css("display","none");
            click_liquidati = 0;
            $(".link-dati-liquidati").removeClass("glyphicon-minus-sign");
            $(".link-dati-liquidati").addClass("glyphicon-plus-sign");
        }


        $( ".box-dati-liquidati" ).animate({
            height: ""+altezza_liquidati
        }, 300, function() {
          // Animation complete.
        });

        $( ".box-dati-cofinanziati" ).animate({
            height: "0"
        }, 300, function() {
          // Animation complete.
        });
        click_cofinanziati = 0;
        $(".link-dati-cofinanziati").removeClass("glyphicon-minus-sign");
        $(".link-dati-cofinanziati").addClass("glyphicon-plus-sign");
        $( ".freccia-verde-cofinanziati" ).css("display","none");

    });



    //end new part
    var page = $("body").attr('id');

    switch (page) {
        case "index":
            gestione_cerchi_top();
            grafico_cerchi_soggetti_attuatori();
            gestione_grafico_barre();
            grafico_pie_soggetti_attuatori();
            grafico_pie_donazioni();
            
            break;
        case "territorio":
            gestione_cerchi_top();
            grafico_cerchi_soggetti_attuatori();
            gestione_grafico_barre();
            grafico_pie_soggetti_attuatori();
            grafico_pie_donazioni();

            chartPieTerr("pie-territorio-programmati",data_array_pie_territorio_programmati,'#ED450A');
            chartPieTerr("pie-territorio-pianificati",data_array_pie_territorio_pianificati,'#F4E73D');
            chartPieTerr("pie-territorio-attuati",data_array_pie_territorio_attuati,'#059e1e');

            $(".percentuale-programmati").html(percentuale_comune_programmati.replace(".", ","));
            $(".percentuale-pianificati").html(percentuale_comune_pianificati.replace(".", ","));
            $(".percentuale-attuati").html(percentuale_comune_attuati.replace(".", ","));
            

            break;
        case "tipologia":
            gestione_cerchi_top();
            grafico_cerchi_soggetti_attuatori();
            grafico_pie_soggetti_attuatori();
            grafico_pie_donazioni();

            chartPieTerr("pie-tipologia-programmati",data_array_pie_tipologia_programmati,'#ED450A');
            chartPieTerr("pie-tipologia-pianificati",data_array_pie_tipologia_pianificati,'#F4E73D');
            chartPieTerr("pie-tipologia-attuati",data_array_pie_tipologia_attuati,'#059e1e');
            
            $(".percentuale-programmati").html(percentuale_tipo_programmati.replace(".", ","));
            $(".percentuale-pianificati").html(percentuale_tipo_pianificati.replace(".", ","));
            $(".percentuale-attuati").html(percentuale_tipo_attuati.replace(".", ","));
            
            break;
        case "soggetto":
            
            break;
        case "impresa":
            
            break;

    }
    

    $( ".tip" ).tooltip({html:true});
	
	$(".btn-more").on("click", function(e) {
		e.preventDefault();
		$(".btn-more").find('i').toggleClass('glyphicon-minus-sign', 'glyphicon-plus-sign');
	});
    
    //gestione tooltip hover PIE
    var number_li_pie = 0;
    $(".lista-pie a").each(function() {
        getTooltip($(this), number_li_pie, "pie");
        number_li_pie++;
    });
    var number_li_pie_donazioni = 0;
    $(".lista-pie-donazioni a").each(function() {
        getTooltip($(this), number_li_pie_donazioni, "pie-donazioni");
        number_li_pie_donazioni++;
    });

});