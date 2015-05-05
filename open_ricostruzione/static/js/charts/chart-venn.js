$(function(){
    var progr  = parseFloat($(".riepilogo .programmati .num").html());
    var pianif = parseFloat($(".riepilogo .pianificati .num").html());
    var attual = parseFloat($(".riepilogo .attuati .num").html());

    $('#chart-venn').highcharts({
      chart:{
        backgroundColor: "rgba(255, 255, 255, 0)",
        margin: 0,
        padding: 0
      },
      title: {
          text: ''
      },
      tooltip: { enabled: false },
      plotOptions: {
          series: {
            showInLegend: false
            //point: {
            //  events: {
            //    mouseOver: function(){
            //      this.graphic.element.setAttribute('stroke-width', 2);
            //      this.graphic.element.setAttribute('stroke', '#00f');
            //    },
            //    mouseOut: function () {
            //      this.graphic.element.setAttribute('stroke-width', 0);
            //    }
            //  }
            //}
          }
      },
      series: [{
          type: 'venn',
          data: [
              ['A', + attual],
              ['B', + pianif],
              ['C', + progr],
              ['A - B', + attual],
              ['B - C', + pianif],
              ['A - C', + 0]
          ]
      }]
    });
    //return false;


//
//
//
//    var progr1  = parseFloat($(".soggetti-attuatori-1 .importo-soggetti-programmati").html());
//    var pianif1 = parseFloat($(".soggetti-attuatori-1 .importo-soggetti-pianificati").html());
//    var attual1 = parseFloat($(".soggetti-attuatori-1 .importo-soggetti-attuati").html());

//    $('#chart-venn-soggetti1').highcharts({
//      chart:{
//        backgroundColor: "rgba(255, 255, 255, 0)",
//        margin: 0,
//        padding: 0
//      },
//      title: {
//          text: ''
//      },
//      tooltip: { enabled: false },
//      plotOptions: {
//          series: {
//            showInLegend: false,
//            //point: {
//            //  events: {
//            //    mouseOver: function(){
//            //      this.graphic.element.setAttribute('stroke-width', 2);
//            //      this.graphic.element.setAttribute('stroke', '#00f');
//            //    },
//            //    mouseOut: function () {
//            //      this.graphic.element.setAttribute('stroke-width', 0);
//            //    }
//            //  }
//            //}
//          }
//      },
//      series: [{
//          type: 'venn',
//          data: [
//              ['A', + attual1],
//              ['B', + pianif1],
//              ['C', + progr1],
//              ['A - B', + attual1],
//              ['B - C', + pianif1],
//              ['A - C', + 0]
//          ]
//      }]
//    });
    //return false;
    
    
    
    
    
    
//    var progr2  = parseFloat($(".soggetti-attuatori-2 .importo-soggetti-programmati").html());
//    var pianif2 = parseFloat($(".soggetti-attuatori-2 .importo-soggetti-pianificati").html());
//    var attual2 = parseFloat($(".soggetti-attuatori-2 .importo-soggetti-attuati").html());
//
//    $('#chart-venn-soggetti2').highcharts({
//      chart:{
//        backgroundColor: "rgba(255, 255, 255, 0)",
//        margin: 0,
//        padding: 0
//      },
//      title: {
//          text: ''
//      },
//      tooltip: { enabled: false },
//      plotOptions: {
//          series: {
//            showInLegend: false,
//            //point: {
//            //  events: {
//            //    mouseOver: function(){
//            //      this.graphic.element.setAttribute('stroke-width', 2);
//            //      this.graphic.element.setAttribute('stroke', '#00f');
//            //    },
//            //    mouseOut: function () {
//            //      this.graphic.element.setAttribute('stroke-width', 0);
//            //    }
//            //  }
//            //}
//          }
//      },
//      series: [{
//          type: 'venn',
//          data: [
//              ['A', + attual2],
//              ['B', + pianif2],
//              ['C', + progr2],
//              ['A - B', + attual2],
//              ['B - C', + pianif2],
//              ['A - C', + 0]
//          ]
//      }]
//    });
    //return false;
    
    
    
//
//
//    var progr3  = parseFloat($(".soggetti-attuatori-3 .importo-soggetti-programmati").html());
//    var pianif3 = parseFloat($(".soggetti-attuatori-3 .importo-soggetti-pianificati").html());
//    var attual3 = parseFloat($(".soggetti-attuatori-3 .importo-soggetti-attuati").html());

//    $('#chart-venn-soggetti3').highcharts({
//      chart:{
//        backgroundColor: "rgba(255, 255, 255, 0)",
//        margin: 0,
//        padding: 0
//      },
//      title: {
//          text: ''
//      },
//      tooltip: { enabled: false },
//      plotOptions: {
//          series: {
//            showInLegend: false,
//            //point: {
//            //  events: {
//            //    mouseOver: function(){
//            //      this.graphic.element.setAttribute('stroke-width', 2);
//            //      this.graphic.element.setAttribute('stroke', '#00f');
//            //    },
//            //    mouseOut: function () {
//            //      this.graphic.element.setAttribute('stroke-width', 0);
//            //    }
//            //  }
//            //}
//          }
//      },
//      series: [{
//          type: 'venn',
//          data: [
//              ['A', + attual3],
//              ['B', + pianif3],
//              ['C', + progr3],
//              ['A - B', + attual3],
//              ['B - C', + pianif3],
//              ['A - C', + 0]
//          ]
//      }]
//    });
    //return false;



});
