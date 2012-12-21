from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, DetailView, ListView
from django.db.models.aggregates import Count, Sum
from open_ricostruzione import settings
from open_ricostruzione.models import *
from django.db import connections
import datetime
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
from django.http import HttpResponseRedirect
from open_ricostruzione.settings import COMUNI_CRATERE
from django.template.defaultfilters import date as _date

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

        context['ultimo_aggiornamento'] = UltimoAggiornamento.objects.all()[0].data_progetti.date()

        #news in home page
        news_big = Entry.objects.all().order_by('-published_at')[0]


        ##   converto la data nel formato  Nome mese - Anno
        context['news_big']={'day':news_big.published_at.day,
                             'month':_date(news_big.published_at,"M"),
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
                 'month':_date(news_big.published_at,"M"),
                 'year':val.published_at.year,
                 'title':val.title,
                 'abstract':val.abstract,
                 'slug':val.slug,
                 }
            )

        context['news_small']=news_small

        # importi dei progetti per categorie
        progetti_categorie_pie =\
            Progetto.objects.filter( id_padre__isnull = True).values('tipologia__denominazione').\
            annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')

        context['progetti_categorie_pie'] = progetti_categorie_pie

        progetti_categorie_list =\
            Progetto.objects.filter( id_padre__isnull = True).values('tipologia__denominazione','tipologia__slug').\
            annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')


        for value in progetti_categorie_list:
            value['sum']=moneyfmt(value['sum'],2,"",".",",")

        context['progetti_categorie_list'] =progetti_categorie_list

        # donazioni divise per tipologia cedente
        donazioni_categorie_pie =\
            Donazione.objects.all().\
                filter(confermato = True).values('tipologia__denominazione').\
                annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')

        context['donazioni_categorie_pie'] = donazioni_categorie_pie


        donazioni_categorie_list =\
            Donazione.objects.all().\
            filter(confermato = True).values('tipologia__denominazione','tipologia__slug').\
            annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')


        for value in donazioni_categorie_list:
            value['sum']=moneyfmt(value['sum'],2,"",".",",")

        context['donazioni_categorie_list'] = donazioni_categorie_list

        #trasforma la data di oggi in timestamp come base per creare un indice randomico sulla base del giorno
        today = int(time.mktime(datetime.date.today().timetuple()))

        #comuni oggi in evidenza

#        comuni con progetti padre con importo maggiore di zero
        c_progetti=Territorio.objects.\
           filter(
            tipo_territorio="C",
            progetto__parent__isnull=True,
            progetto__riepilogo_importi__gt=0
            ).\
            annotate(p=Count("progetto"),p_sum=Sum("progetto__riepilogo_importi")).\
            values_list('cod_comune',flat=True)

#        comuni con donazioni confermate e importo maggiore di zero
        c_donazioni=Territorio.objects.filter(
            tipo_territorio="C",
            progetto__parent__isnull=True,
            donazione__importo__gt=0,
            donazione__confermato=True
            ).annotate(c=Count("donazione"),sum=Sum("donazione__importo")).\
            values_list('cod_comune',flat=True)


        donazioni_considerate_cod=Donazione.objects.filter(
            importo__gt=0,
            confermato=True,
            territorio__cod_comune__in=c_donazioni
            ).values_list('id_donazione',flat=True)


        progetti_considerati_cod=Progetto.objects.\
            filter(id_padre__isnull=True, riepilogo_importi__gt=0).\
            values_list('id_progetto',flat=True)



#        codici dei comuni che sono presenti nei tre insiemi
        cod_considerati=set.intersection(set(c_donazioni), set(c_progetti),set( COMUNI_CRATERE))

        comuni_considerati = Territorio.objects.\
            filter(cod_comune__in=cod_considerati, donazione__id_donazione__in=donazioni_considerate_cod).\
            annotate(c=Count('cod_comune'))


        comuni_evidenza=[]
        #progetti oggi in evidenza
        c_considerati_num = comuni_considerati.count()
        i = today%c_considerati_num

        for j in range(1,4):
            c_evidenza={}
            comune = comuni_considerati[((i+j)%c_considerati_num)+1]
            comune_donazioni = Donazione.objects.filter(territorio=comune, id_donazione__in=donazioni_considerate_cod).\
                aggregate(d_sum=Sum('importo'))

            comune_danno = Progetto.objects.filter(
                territorio=comune,
                id_progetto__in=progetti_considerati_cod
            ).aggregate(p_sum=Sum('riepilogo_importi'))

#           inserisce il comune e le somme di danno e donazioni nel diz. in evidenza e fa lo humanize delle cifre
            c_evidenza={
                'comune':comune,
                'd_sum':moneyfmt(Decimal(comune_donazioni['d_sum']),2,"",".",","),
                'p_sum':moneyfmt(Decimal(comune_danno['p_sum']),2,"",".",","),
            }

            comuni_evidenza.append(c_evidenza)

        context['comuni_evidenza']=comuni_evidenza

        #progetti oggi in evidenza
        
        progetti_considerati = Progetto.objects.filter(id_padre__isnull=True, riepilogo_importi__gt=0)

        i = today%progetti_considerati.count()
        progetti_evidenza=[]
        for j in range(1,4):
            progetti_evidenza.append(progetti_considerati[((i+j)%progetti_considerati.count())+1])


        #humanize cifre monetarie
        for val in progetti_evidenza:
            val.riepilogo_importi=moneyfmt(val.riepilogo_importi,2,"",".",",")


        context['progetti_evidenza'] =progetti_evidenza

        donazioni_campovolo=Donazione.objects.filter(tipologia=TipologiaCedente.objects.get(denominazione="Regione Emilia-Romagna"),
            confermato=True,denominazione="Emilia-Romagna",
            info__contains="Iniziativa patrocinata dalla Regione Emilia-Romagna - Concerto Campo Volo").\
            aggregate(sum=Sum('importo')).values()[0]

        donazioni_campovolo= moneyfmt(donazioni_campovolo,2,"",".",",")
        context['donazioni_campovolo']=donazioni_campovolo

        donazioni_sms = Donazione.objects.filter(tipologia=TipologiaCedente.objects.get(denominazione="Regione Emilia-Romagna"),
            confermato=True,denominazione="Emilia-Romagna",
            modalita_r__exact="SMS").\
            aggregate(sum=Sum('importo')).values()[0]

        donazioni_sms= moneyfmt(donazioni_sms,2,"",".",",")
        context['donazioni_sms']=donazioni_sms

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

        # numero donazioni
        context['n_donazioni'] = Donazione.objects.filter(confermato = True, progetto=p).count()
        # donazioni per il territorio considerato
        tot_donazioni = Donazione.objects.filter(confermato = True, progetto=p).aggregate(s=Sum('importo')).values()
        if tot_donazioni[0]:
            context['tot_donazioni'] = tot_donazioni[0]


        context['territorio_nome'] = p.territorio.denominazione
        iban =  Progetto.objects.get(pk = p.pk).territorio.iban
        if iban:
            context['iban'] = iban

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
            return Progetto.objects.filter(id_padre__isnull=True,denominazione__icontains=qterm)[0:50]

        else:
           return  Progetto.objects.all()[0:50]



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
            progetti_categorie_list =\
                Progetto.objects.filter(territorio=t).values('tipologia__denominazione','tipologia__slug').\
                annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')

            for p in progetti_categorie_list:
                p['sum'] =moneyfmt(p['sum'] ,2,"",".",",")

            context['progetti_categorie_list']=progetti_categorie_list

            progetti_categorie_pie=\
                Progetto.objects.filter(territorio=t).values('tipologia__denominazione','tipologia__slug').\
                annotate(sum=Sum('riepilogo_importi')).annotate(c=Count('pk')).order_by('-sum')
            for p in progetti_categorie_pie:
                p['sum'] =moneyfmt(p['sum'] ,2,"","",".")

            context['progetti_categorie_pie']=progetti_categorie_pie

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
            for p in projects:
                p.riepilogo_importi =moneyfmt( Decimal(p.riepilogo_importi),2,"",".",",")

            context['progetti_top'] = projects


        # donazioni divise per tipologia cedente
        donazioni_categorie_list = \
            Donazione.objects.filter( territorio=t).\
            filter(confermato = True).values('tipologia__denominazione','tipologia__slug').\
            annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')

        for d in donazioni_categorie_list:
            d['sum'] =moneyfmt(d['sum'] ,2,"",".",",")

        context['donazioni_categorie_list']=donazioni_categorie_list

        donazioni_categorie_pie =\
            Donazione.objects.filter( territorio=t).\
            filter(confermato = True).values('tipologia__denominazione','tipologia__slug').\
            annotate(sum = Sum('importo')).annotate(c=Count('pk')).order_by('-sum')

        context['donazioni_categorie_pie']=donazioni_categorie_pie


        #iban territorio
        iban = Territorio.objects.get(cod_comune = t.cod_comune, cod_comune__in=settings.COMUNI_CRATERE).iban
        if iban:
            context['iban'] = iban

        donazioni_spline = t.get_spline_data()

        if donazioni_spline and len(donazioni_spline)>1:
            context['donazioni_spline'] = donazioni_spline

#       ultime donazioni per il comune considerato

        donazioni_temp=Donazione.objects.filter(territorio=t,confermato=True).\
            extra(select={'date': connections[Donazione.objects.db].ops.date_trunc_sql('month', 'data')}).\
            order_by('-data')[:3]

        donazioni_last =[]


        for idx, val in enumerate(donazioni_temp):
##      converto la data nel formato  Nome mese - Anno

            if type(val.date).__name__=="datetime":
                val_date_obj =val.date
            else:
                val_date_obj = datetime.datetime.strptime(val.date,"%Y-%m-%d %H:%M:%S")

            val_date_day = val.data.day
            val_date_month = _date(val_date_obj,"M")
            val_date_year = time.strftime("%Y", val_date_obj.timetuple())
            donazioni_last.append({'day':val_date_day,
                                   'month':val_date_month,
                                   'year':val_date_year,
                                   'tipologia':val.tipologia,
                                   'importo':moneyfmt(val.importo,2,"",".",","),
                                   'slug':val.tipologia.slug
            })

        context['donazioni_last'] = donazioni_last

# coordinate del comune

        if t.gps_lat:
            context['gps_lat']=t.gps_lat
        if t.gps_lon:
            context['gps_lon']=t.gps_lon

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
            if type(val['date']).__name__=="datetime":
                val_date_obj = val['date']
            else:
                val_date_obj = datetime.datetime.strptime(val['date'],"%Y-%m-%d %H:%M:%S")

            val_date_print=_date(val_date_obj,"M - Y")

            if idx is not 0:
#                se le due date sono piu' distanti di un mese
#                inserisce tanti mesi quanti mancano con un importo uguale all'ultimo importo disponibile
#                per creare un grafico piatto
                if type(donazioni_mese[idx-1]['date']).__name__=="datetime":
                    donazioni_date_obj=donazioni_mese[idx-1]['date']
                else:
                    donazioni_date_obj = datetime.datetime.strptime(donazioni_mese[idx-1]['date'],"%Y-%m-%d %H:%M:%S")

                if (val_date_obj-donazioni_date_obj) > timedelta(31):
                    n_mesi = (val_date_obj - donazioni_date_obj).days / 28
                    for k in range(1, n_mesi):
                        new_month_obj = add_months(donazioni_date_obj,k)
                        new_month_print = _date(new_month_obj,"M - Y")
                        donazioni_spline.append({'month':new_month_print,'sum':donazioni_spline[j-1]['sum'],'sum_ita':None})
                        j += 1

#               inserisce il dato del mese corrente
                donazioni_spline.append({'month':val_date_print,'sum':(donazioni_spline[j-1]['sum']+val['sum']),'sum_ita':None})
                j += 1

            else:
                donazioni_spline.append({'month':val_date_print,'sum':val['sum'],'sum_ita':None})
                j += 1


        if donazioni_spline and len(donazioni_spline)>1:
#            rende i numeri Decimal delle stringhe per il grafico

            for value in donazioni_spline:
                value['sum_ita']=moneyfmt(value['sum'],2,"",".",",")
                value['sum']=moneyfmt(value['sum'],2,"","",".")

            context['donazioni_spline'] = donazioni_spline

        #donazioni per tipologia
        donazioni_categorie_list = Donazione.objects.all().\
            filter(confermato=True).values('tipologia__denominazione','tipologia__slug').\
            annotate(c=Count('tipologia__denominazione')).annotate(sum = Sum('importo')).order_by('-sum')

        for idx, val in enumerate(donazioni_categorie_list):
            val['sum'] = moneyfmt(val['sum'],2,"",".",",")

        context['donazioni_categorie_list']=donazioni_categorie_list

        #donazioni per tipologia
        donazioni_categorie_pie = Donazione.objects.all().\
            filter(confermato=True).values('tipologia__denominazione').\
            annotate(c=Count('tipologia__denominazione')).annotate(sum = Sum('importo'))

        for idx, val in enumerate(donazioni_categorie_pie):
            val['sum'] = moneyfmt(val['sum'],2,"","",".")

        context['donazioni_categorie_pie']=donazioni_categorie_pie



        #       ultime donazioni per il comune considerato
        donazioni_temp = Donazione.objects.select_related().filter(confermato=True).order_by('-data')[:3]
        donazioni_last=[]

        for idx, val in enumerate(donazioni_temp):
        ##            converto la data nel formato  Nome mese - Anno
            val_date_day = val.data.day
            val_date_month= _date(val.data,"M")
            val_date_year = time.strftime("%Y", val.data.timetuple())
            donazioni_last.append({'day':val_date_day,
                                   'month':val_date_month,
                                   'year':val_date_year,
                                   'tipologia':val.tipologia,
                                   'importo':moneyfmt(val.importo,2,"",".",","),
                                   'slug':val.tipologia.slug
            })



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


class TipologieCedenteView(TemplateView):
    template_name = "donazione_list.html"
    n_donazioni = 0
    tot_donazioni = 0
    tipologia = None
    comune = None
    donazioni = None
    page = 1
    donazioni_pagina = 50 # numero di elementi per pagina

    def get_context_data(self, **kwargs):

        context = super(TipologieCedenteView, self).get_context_data(**kwargs)
        paginator =None
        self.n_donazioni = self.donazioni.count()
        self.tot_donazioni= self.donazioni.aggregate(s=Sum('importo')).values()[0]
#        if self.tipologia == TipologiaCedente.objects.get(slug="privati-cittadini"):
#            return HttpResponseRedirect(reversed('home'))


        if self.donazioni:

            paginator = Paginator(self.donazioni, self.donazioni_pagina)
            try:
                page_obj = paginator.page(self.page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                page_obj = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                page_obj = paginator.page(paginator.num_pages)

            donazioni_page=[]
            for idx, val in enumerate(page_obj.object_list):
                donazioni_page.append(
                    {'day':val.data.day,
                     'month':_date(val.data,"M"),
                     'year':val.data.year,
                     'donazione':val,
                     }
                )

            context['donazioni_page'] = donazioni_page
            context['paginator']=paginator
            context['page_obj']=page_obj
            context['page']=self.page

        if self.n_donazioni:
            context['n_donazioni']=self.n_donazioni
        if self.tot_donazioni:
            context['tot_donazioni']=moneyfmt(self.tot_donazioni,2,"",".",",")
        if self.tipologia:
            context['tipologia']=self.tipologia
        if self.comune:
            context['comune']=self.comune
        if paginator:
            context['n_pages']=paginator._get_num_pages()

        return context

class DonazioniCompleta(TipologieCedenteView):

    def get_context_data(self, **kwargs):

        self.donazioni= Donazione.objects.filter(confermato=True).order_by('denominazione')
        self.page = self.request.GET.get('page')
        self.context = super(DonazioniCompleta, self).get_context_data(**kwargs)
        return self.context

class DonazioniTipologiaComune(TipologieCedenteView):

    def get_context_data(self, **kwargs):

        self.comune = Territorio.objects.get(slug=kwargs['comune'])
        self.tipologia = TipologiaCedente.objects.get(slug=kwargs['tipologia'])
        self.donazioni= Donazione.objects.filter(territorio=self.comune, tipologia=self.tipologia,confermato=True).order_by('denominazione')
        self.page = self.request.GET.get('page')
        self.context = super(DonazioniTipologiaComune, self).get_context_data(**kwargs)
        return self.context


class DonazioniTipologia(TipologieCedenteView):

    def get_context_data(self, **kwargs):

        self.tipologia = TipologiaCedente.objects.get(slug=kwargs['tipologia'])
        self.donazioni= Donazione.objects.filter( tipologia=self.tipologia,confermato=True).order_by('denominazione')
        self.page = self.request.GET.get('page')

        self.context = super(DonazioniTipologia, self).get_context_data(**kwargs)
        return self.context

class DonazioniComune(TipologieCedenteView):

    def get_context_data(self, **kwargs):

        self.comune = Territorio.objects.get(slug=kwargs['comune'])
        self.donazioni= Donazione.objects.filter(territorio=self.comune,confermato=True).order_by('denominazione')
        self.page = self.request.GET.get('page')
        self.context = super(ProgettiComune, self).get_context_data(**kwargs)
        return self.context



class TipologieProgettoView(TemplateView):

    template_name = "progetti_list.html"
    n_progetti = 0
    tot_danno = 0
    tipologia = None
    comune = None
    progetti = None
    page = 1
    progetti_pagina = 50 # numero di elementi per pagina

    def get_context_data(self, **kwargs):
        paginator =None
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
            context['tot_danno']=moneyfmt(self.tot_danno,2,"",".",",")
        if self.tipologia:
            context['tipologia']=self.tipologia
        if self.comune:
            context['comune']=self.comune
        if paginator:
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


