from django.core.exceptions import ObjectDoesNotExist
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs ):
        context={}

        #numero di comuni con almeno 1 progetto attivo
        context['n_comuni'] = Territorio.objects.filter(tipo_territorio = "C",cod_comune__in=settings.COMUNI_CRATERE).\
                annotate(c = Count("progetto")).filter(c__gt=0).count()

        #numero progetti
        context['n_progetti']=  Progetto.objects.filter(id_padre__isnull = True).count()
        # importi progetti totale
        stima_danno = Progetto.objects.filter( id_padre__isnull = True).\
            aggregate(s=Sum('riepilogo_importi')).values()

        if stima_danno[0]:
            context['stima_danno'] = stima_danno[0]

        # numero donazioni
        context['n_donazioni'] = Donazione.objects.filter(confermato=True).count()
        # donazioni per il territorio considerato
        tot_donazioni = Donazione.objects.filter(confermato = True).aggregate(s=Sum('importo')).values()
        if tot_donazioni[0]:
            context['tot_donazioni'] = tot_donazioni[0]


        # importi dei progetti per categorie
        context['progetti_categorie'] =\
            Progetto.objects.filter( id_padre__isnull = True).values('tipologia__denominazione').\
            annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')

        # donazioni divise per tipologia cedente
        context['donazioni_categorie'] =\
        Donazione.objects.all().\
            filter(confermato = True).values('tipologia__denominazione').\
            annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')

        #comuni oggi in evidenza
        context['comuni_evidenza'] = Territorio.objects.filter(tipo_territorio="C",cod_comune__in=settings.COMUNI_CRATERE).\
            annotate(p=Count("progetto"),p_sum=Sum("progetto__riepilogo_importi"),d = Count("donazione"),d_sum=Sum("donazione")).\
            filter(p__gt=0,d__gt=0, d_sum__gt=0).order_by('-pk')[:3]

        #progetti oggi in evidenza
        context['progetti_evidenza'] = Progetto.objects.filter(id_padre__isnull=True).order_by("-riepilogo_importi")[:3]

        context['ultimo_aggiornamento'] = UltimoAggiornamento.objects.all()[0].data_progetti.date()

        #news in home page
        news_big = Entry.objects.all().order_by('-published_at')[0]


        ##            converto la data nel formato  Nome mese - Anno
        context['news_big']={'day':news_big.published_at.day,
                     'month':news_big.published_at.strftime("%B")[:3],
                     'year':news_big.published_at.year,
                     'title':news_big.title,
                     'abstract':news_big.abstract,
                     'slug':news_big.slug,
                     'body':news_big.body,
                     }


        news_temp = Entry.objects.all().order_by('-published_at')[1:3]
        news_small=[]
        for idx, val in enumerate(news_temp):
            news_small.append(
                {'day':val.published_at.day,
                 'month':val.published_at.strftime("%B")[:3],
                 'year':val.published_at.year,
                 'title':val.title,
                 'abstract':val.abstract,
                 'slug':val.slug,
                 }
            )

        context['news_small']=news_small

        context['donazioni_campovolo']=Donazione.objects.filter(tipologia=TipologiaCedente.objects.get(denominazione="Regione Emilia-Romagna"),
            confermato=True,denominazione="Emilia-Romagna",
            info__contains="Iniziativa patrocinata dalla Regione Emilia-Romagna - Concerto Campo Volo").\
            aggregate(sum=Sum('importo')).values()[0]

        context['donazioni_sms']=Donazione.objects.filter(tipologia=TipologiaCedente.objects.get(denominazione="Regione Emilia-Romagna"),
            confermato=True,denominazione="Emilia-Romagna",
            modalita_r__exact="SMS").\
            aggregate(sum=Sum('importo')).values()[0]


        return context


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



class ProgettoListView(ListView):
    model=Progetto
    template_name = "tipologieprogetto.html"

    def get_context_data(self, **kwargs):
        context = super(ProgettoListView, self).get_context_data(**kwargs)
        context['SITE_URL'] = settings.PROJECT_ROOT
        return context

    def get_queryset(self):
#        context = super(ProgettoListView, self).get_context_data(**kwargs)

        if 'qterm' in self.request.GET:
            qterm = self.request.GET['qterm']
            return Progetto.objects.filter(denominazione__icontains=qterm)[0:50]
#        else:
#            if self.kwargs['slug']:
#                s = self.kwargs['slug']
#
#                object = TipologiaProgetto.objects.get(slug = s)
#                context['tipologia'] = object.denominazione
#                context['slug'] = object.slug
#                context['project_list'] = Progetto.objects.filter(tipologia=object)
        else:
           return  Progetto.objects.all()[0:50]
#            return context


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
            # importi dei progetti per categorie
            context['progetti_categorie'] =\
                Progetto.objects.filter(territorio=t).values('tipologia__denominazione').\
                annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')


        # numero donazioni
        context['n_donazioni'] = Donazione.objects.filter(confermato = True).filter(territorio=t).count()
        # donazioni per il territorio considerato
        tot_donazioni = Donazione.objects.filter(territorio=t, confermato = True).aggregate(s=Sum('importo')).values()
        if tot_donazioni[0]:
            context['tot_donazioni'] = tot_donazioni[0]

        context['donazioni_comune'] = Donazione.objects.filter(confermato = True).filter(territorio=t)

        #lista progetti per questo territorio in ordine di costo decrescente
        projects = Progetto.objects.filter(territorio = t).order_by('-riepilogo_importi')[:10]

        if projects:
            context['progetti_top'] = projects


        # donazioni divise per tipologia cedente
        context['donazioni_categorie'] = \
            Donazione.objects.filter( territorio=t).\
            filter(confermato = True).values('tipologia__denominazione').\
            annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')

        #iban territorio
        iban = Territorio.objects.get(cod_comune = t.cod_comune, cod_comune__in=settings.COMUNI_CRATERE).iban
        if iban:
            context['iban'] = iban

        donazioni_spline = t.get_spline_data()

        if donazioni_spline and len(donazioni_spline)>1:
        #            rende i numeri Decimal delle stringhe per il grafico
        #            TODO: creare i dati per le label in formato italiano

            for value in donazioni_spline:
                value['sum']=moneyfmt(value['sum'],2,"","",".")

            context['donazioni_spline'] = donazioni_spline

#       ultime donazioni per il comune considerato
#        donazioni_last = Donazione.objects.select_related().filter(territorio=t,confermato=True).order_by('-data')[:3]
        donazioni_temp=Donazione.objects.filter(territorio=t,confermato=True).\
            extra(select={'date': connections[Donazione.objects.db].ops.date_trunc_sql('month', 'data')}).\
            order_by('-data')[:3]

        donazioni_last =[]

        for idx, val in enumerate(donazioni_temp):
        ##            converto la data nel formato  Nome mese - Anno
            val_date_obj = datetime.strptime(val.date,"%Y-%m-%d %H:%M:%S")
#            val_date_day = time.strftime("%d", val_date_obj.timetuple()).lstrip('0')
            val_date_day = val.data.day
            val_date_month = time.strftime("%b", val_date_obj.timetuple())
            val_date_year = time.strftime("%Y", val_date_obj.timetuple())
            donazioni_last.append({'day':val_date_day,'month':val_date_month,'year':val_date_year,'donazione':val})

        context['donazioni_last'] = donazioni_last
        return context

class DonazioneView(TemplateView):

    template_name = "donazioni.html"


    def get_context_data(self, **kwargs):
        context = super(DonazioneView, self).get_context_data(**kwargs)

        # numero donazioni
        context['n_donazioni'] = Donazione.objects.filter(confermato = True).count()

        # tutte le donazioni
        tot_donazioni = Donazione.objects.filter(confermato = True).aggregate(s=Sum('importo')).values()
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

        donazioni_mese = Donazione.objects.filter(confermato = True).\
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
        donazioni_categorie = Donazione.objects.all().\
            filter(confermato=True).values('tipologia__denominazione').\
            annotate(c=Count('tipologia__denominazione')).annotate(sum = Sum('importo'))

#        for idx, val in enumerate(donazioni_categorie):
#            val['sum'] = moneyfmt(val['sum'],2,"","",",")

        context['donazioni_categorie']=donazioni_categorie


        #       ultime donazioni per il comune considerato
        donazioni_last = Donazione.objects.select_related().filter(confermato=True).order_by('-data')[:3]


        context['donazioni_last'] = donazioni_last

        return context

class EntryView(DetailView):
    model = Entry
    context_object_name = "entry"
    template_name = "static.html"

    def get_context_data(self, **kwargs):
        context = super(EntryView, self).get_context_data(**kwargs)
        entry = self.get_object()

        return context





class TipologieProgettoView(TemplateView):

    template_name = "progetti_list.html"
    n_progetti = 0
    tot_danno = 0
    tipologia = None
    comune = None
    progetti = None
    page = 1
    progetti_pagina = 5 # numero di progetti per pagina

    def get_context_data(self, **kwargs):

        context = super(TipologieProgettoView, self).get_context_data(**kwargs)

        self.n_progetti = self.progetti.count()
        self.tot_danno= self.progetti.aggregate(s=Sum('riepilogo_importi')).values()[0]

        if self.progetti:
            paginator = Paginator(self.progetti, self.progetti_pagina)
            try:
                page_obj = paginator.page(self.page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                page_obj = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                page_obj = paginator.page(paginator.num_pages)

            context['paginator']=paginator
            context['page_obj']=page_obj
            context['page']=self.page

        if self.n_progetti:
            context['n_progetti']=self.n_progetti
        if self.tot_danno:
            context['tot_danno']=self.tot_danno
        if self.tipologia:
            context['tipologia']=self.tipologia
        if self.comune:
            context['comune']=self.comune

        context['n_pages']=paginator._get_num_pages()

        return context

class ProgettiTipologiaComune(TipologieProgettoView):

    def get_context_data(self, **kwargs):

        self.comune = Territorio.objects.get(slug=kwargs['comune'])
        self.tipologia = TipologiaProgetto.objects.get(slug=kwargs['tipologia'])
        self.progetti= Progetto.objects.filter(territorio=self.comune, tipologia=self.tipologia,id_padre__isnull=True).order_by('-riepilogo_importi')
        self.page = self.request.GET.get('page')
        self.context = super(ProgettiTipologiaComune, self).get_context_data(**kwargs)
        return self.context


class ProgettiTipologia(TipologieProgettoView):

    def get_context_data(self, **kwargs):

        self.tipologia = TipologiaProgetto.objects.get(slug=kwargs['tipologia'])
        self.progetti= Progetto.objects.filter(tipologia=self.tipologia,id_padre__isnull=True).order_by('-riepilogo_importi')
        self.page = self.request.GET.get('page')

        self.context = super(ProgettiTipologia, self).get_context_data(**kwargs)
        return self.context

class ProgettiComune(TipologieProgettoView):

    def get_context_data(self, **kwargs):

        self.comune = Territorio.objects.get(slug=kwargs['comune'])
        self.progetti= Progetto.objects.filter(territorio=self.comune,id_padre__isnull=True).order_by('-riepilogo_importi')
        self.page = self.request.GET.get('page')
        self.context = super(ProgettiComune, self).get_context_data(**kwargs)
        return self.context


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


