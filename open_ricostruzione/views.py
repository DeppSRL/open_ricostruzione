from django.views.generic import TemplateView, DetailView, ListView
from django.db.models.aggregates import Count, Sum
from open_ricostruzione import settings
from open_ricostruzione.models import *
from django.db import connections
from datetime import datetime
import time
from open_ricostruzione.utils.moneydate import moneyfmt, add_months
from datetime import timedelta
import json
from json.encoder import JSONEncoder
from django.db.models.query import QuerySet
from django.core.serializers import serialize
from django.utils.functional import curry
from django.http import HttpResponse, HttpResponseNotFound


class HomeView(TemplateView):
    template_name = "home.html"

class ProgettoView(DetailView):
    model = Progetto
    context_object_name = "progetto"
    template_name = 'progetto.html'

    def get_context_data(self, **kwargs ):
        p = self.get_object()
        context = super(ProgettoView, self).get_context_data(**kwargs)

        #sotto progetti
        sottoprogetti = Progetto.objects.filter(id_padre=p.id_progetto).order_by('denominazione')
        if sottoprogetti:
            context['sottoprogetti']=sottoprogetti

        # importi progetto
        stima_danno = Progetto.objects.filter(id_progetto=p.id_progetto).\
            aggregate(s=Sum('riepilogo_importi')).values()

        if stima_danno[0]:
            context['stima_danno'] = stima_danno[0]

        # donazioni per il progetto
        # mancano perche' non abbiamo i dati relativi

        context['territorio_nome'] = p.territorio.denominazione
        iban =  Progetto.objects.get(pk = p.pk).territorio.iban
        if iban:
            context['iban'] = iban

#        mancano le donazioni perche' ci mancano i le relazioni fra donazioni e progetti

        return context

#    def get_queryset(self):
#        if 'qterm' in self.request.GET:
#            qterm = self.request.GET['qterm']
#            return Progetto.objects.filter(denominazione__icontains=qterm)[0:50]
#        else:
#            return Progetto.objects.all()[0:50]

class ProgettoListView(ListView):
    model=Progetto
    template_name = "tipologieprogetto.html"

    def get_context_data(self, **kwargs):
        context = super(ProgettoListView, self).get_context_data(**kwargs)
        context['SITE_URL'] = settings.PROJECT_ROOT
        return context

    def get_queryset(self):
        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return Progetto.objects.filter(denominazione__icontains=qterm)[0:50]
        else:
            return Progetto.objects.all()[0:50]


class TerritorioView(DetailView):
    model = Territorio
    context_object_name = "territorio"
    template_name = 'territorio.html'

    def get_context_data(self, **kwargs ):
        t = self.get_object()
        context = super(TerritorioView, self).get_context_data(**kwargs)

        context['sigla_provincia'] = Territorio.objects.get(tipo_territorio = 'P', cod_provincia = t.cod_provincia, cod_comune = "0").sigla_provincia

        #numero progetti
        context['n_progetti']=  Progetto.objects.filter(territorio=t, id_padre__isnull = True).count()
        # importi progetti totale
        stima_danno = Progetto.objects.filter(territorio=t, id_padre__isnull = True).\
            aggregate(s=Sum('riepilogo_importi')).values()

        if stima_danno[0]:
            context['stima_danno'] = stima_danno[0]

        # numero donazioni
        context['n_donazioni'] = Donazione.objects.filter(territorio=t).count()
        # donazioni per il territorio considerato
        tot_donazioni = Donazione.objects.filter(territorio=t, confermato = True).aggregate(s=Sum('importo')).values()
        if tot_donazioni[0]:
            context['tot_donazioni'] = tot_donazioni[0]

        context['donazioni_comune'] = Donazione.objects.filter(territorio=t)

        # importi dei progetti per categorie
        context['progetti_categorie'] =  \
            Progetto.objects.filter(territorio=t).values('tipologia__denominazione').\
            annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')

        # donazioni divise per tipologia cedente
        context['donazioni_categorie'] = \
            Donazione.objects.filter( territorio=t).\
            filter(confermato = True).values('tipologia__denominazione').\
            annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')

        #iban territorio
        iban = Territorio.objects.get(pk = t.pk).iban
        if iban:
            context['iban'] = iban

        #lista progetti per questo territorio in ordine di costo decrescente
        projects = Progetto.objects.filter(territorio = t).order_by('-riepilogo_importi')[:10]

        if projects:
            context['progetti_top'] = projects

        donazioni_spline = t.get_spline_data()

        if donazioni_spline and len(donazioni_spline)>1:
        #            rende i numeri Decimal delle stringhe per il grafico
        #            TODO: creare i dati per le label in formato italiano

            for value in donazioni_spline:
                value['sum']=moneyfmt(value['sum'],2,"","",".")

            context['donazioni_spline'] = donazioni_spline

#        ultime donazioni per il comune considerato
        donazioni_last = Donazione.objects.select_related().filter(territorio=t,confermato=True).order_by('-data')[:3]

        context['donazioni_last'] = donazioni_last
        return context

class DonazioneView(TemplateView):

    template_name = "donazioni.html"


    def get_context_data(self, **kwargs):
        context = super(DonazioneView, self).get_context_data(**kwargs)

        # numero donazioni
        context['n_donazioni'] = Donazione.objects.filter(confermato = True).count()

        # tutte le donazioni
        tot_donazioni = Donazione.objects.all().aggregate(s=Sum('importo')).values()
        if tot_donazioni[0]:
            context['tot_donazioni'] = tot_donazioni[0]

        #numero progetti
        context['n_progetti']=  Progetto.objects.filter( id_padre__isnull = True).count()
        # importi progetti totale
        stima_danno = Progetto.objects.filter( id_padre__isnull = True).\
            aggregate(s=Sum('riepilogo_importi')).values()

        if stima_danno[0]:
            context['stima_danno'] = stima_danno[0]

        #tutte le donazioni nel tempo
        #le donazioni vengono espresse con valori incrementali rispetto alla somma delle donazioni
        # del mese precedente. In questo modo se un mese le donazioni sono 0 la retta del grafico e' piatta

        donazioni_mese = Donazione.objects.\
                        extra(select={'date': connections[Donazione.objects.db].ops.date_trunc_sql('month', 'data')}).\
                        values('date').annotate(sum = Sum('importo'))

        donazioni_spline =[]
        j = 0

        for idx, val in enumerate(donazioni_mese):
##            converto la data nel formato  Nome mese - Anno
            val_date_obj = datetime.strptime(val['date'],"%Y-%m-%d %H:%M:%S")
            val_date_print = time.strftime("%b - %Y", val_date_obj.timetuple())

            if idx is not 0:
#                se le due date sono piu' distanti di un mese
#                inserisce tanti mesi quanti mancano con un importo uguale all'ultimo importo disponibile
#                per creare un grafico piatto
                donazioni_date_obj = datetime.strptime(donazioni_mese[idx-1]['date'],"%Y-%m-%d %H:%M:%S")
                if (val_date_obj-donazioni_date_obj) > timedelta(31):
                    n_mesi = (val_date_obj - donazioni_date_obj).days / 28
                    for k in range(1, n_mesi):
                        new_month_obj = add_months(donazioni_date_obj,k)
                        new_month_print = time.strftime("%b - %Y", new_month_obj.timetuple())
                        donazioni_spline.append({'month':new_month_print,'sum':donazioni_spline[j-1]['sum']})
                        j += 1

#               inserisce il dato del mese corrente
                donazioni_spline.append({'month':val_date_print,'sum':(donazioni_spline[j-1]['sum']+val['sum'])})
                j += 1

            else:
                donazioni_spline.append({'month':val_date_print,'sum':val['sum']})
                j += 1


        if donazioni_spline and len(donazioni_spline)>1:
#            rende i numeri Decimal delle stringhe per il grafico
#            TODO: creare i dati per le label in formato italiano
            for value in donazioni_spline:
                value['sum']=moneyfmt(value['sum'],2,"","",".")

            context['donazioni_spline'] = donazioni_spline

        #donazioni per tipologia
        donazioni_tipologia = Donazione.objects.all().\
            filter(confermato=True).values('tipologia__denominazione').\
            annotate(count=Count('tipologia__denominazione')).annotate(sum = Sum('importo'))

        for idx, val in enumerate(donazioni_tipologia):
            val['sum'] = moneyfmt(val['sum'],2,"","",",")

        context['donazioni_tipologia']=donazioni_tipologia

        return context


class TipologieProgettoView(TemplateView):

    template_name = "tipologieprogetto.html"


    def get_context_data(self, **kwargs):
        context = super(TipologieProgettoView, self).get_context_data(**kwargs)
        return context



class DjangoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return json.loads(serialize('json', obj))
        return JSONEncoder.default(self,obj)
dumps = curry(json.dumps, cls=DjangoJSONEncoder)

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content,
            content_type='application/json',
            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return dumps(context)


class ProgettiJSONListView(JSONResponseMixin, ProgettoListView):
    def convert_context_to_json(self, context):
        return dumps(context['progetto_list'])


