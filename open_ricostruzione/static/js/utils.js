// Extend the default Number object with a formatMoney() method:
// usage: someVar.formatMoney(decimalPlaces, symbol, thousandsSeparator, decimalSeparator)
// defaults: (2, "$", ",", ".")
Number.prototype.formatMoney = function(places, symbol, thousand, decimal) {
    places = !isNaN(places = Math.abs(places)) ? places : 2;
    symbol = symbol !== undefined ? symbol : "$";
    thousand = thousand || ",";
    decimal = decimal || ".";
    var number = this,
        negative = number < 0 ? "-" : "",
        i = parseInt(number = Math.abs(+number || 0).toFixed(places), 10) + "",
        j = (j = i.length) > 3 ? j % 3 : 0;
    return symbol + negative + (j ? i.substr(0, j) + thousand : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousand) + (places ? decimal + Math.abs(number - i).toFixed(places).slice(2) : "");
};


//funzione invocata dalla select box nelle pagine generiche o dal bottone DONA nella pagina progetto / territorio
function click_donate(territorio, progetto){

    // precarica i dati del comune nella form
    if(territorio!=null){
        $('#payerCausale').attr('value',territorio);

    }

    if(progetto!=null){
        $('#payerCespite').attr('value',progetto);
    }

    //    show the lightbox
    $('#donation_form').lightbox_me({
        centered: false,
        modalCSS: {top: '10px'},
        onLoad: function() {
            $('#donation_form').find('input:first').focus()
        }
    });
}


//if an input is null return true, otherwise false

function check_input_is_null(id){

    if($(id).length){
        if($(id).val()!='')
            return false;
    }

    return true;
}

//check if n is numeric or not
function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function addFlashMessage(id, type, text){

    var div_class = '';
    if(type=='error')
        div_class='alert-error';
    else
        div_class='alert-info';

    var el = $('<div class="alert '+div_class+'" id="error">').text(text);
    $(id).append(el);

}

function removeErrorFlashMessage(id){
    $(id).children().remove();
}