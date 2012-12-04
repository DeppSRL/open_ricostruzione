from django.views.generic import TemplateView, DetailView
from django.db.models.aggregates import Count, Sum
from open_ricostruzione.models import *
from django.db import connections
from datetime import datetime
import time
from open_ricostruzione.utils.moneydate import moneyfmt, add_months
from datetime import timedelta




class HomeView(TemplateView):
    template_name = "home.html"

class ProgettoView(DetailView):
    model = Progetto
    context_object_name = "progetto"
    template_name = 'progetto.html'

    def get_context_data(self, **kwargs ):
        p = self.get_object()
        context = super(ProgettoView, self).get_context_data(**kwargs)

        context['territorio_nome'] = p.territorio.denominazione
        iban =  Progetto.objects.get(pk = p.pk).territorio.iban
        if iban:
            context['iban'] = iban

#        mancano le donazioni perche' ci mancano i le relazioni fra donazioni e progetti

        return context

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
        tot_donazioni = Donazione.objects.filter(territorio=t).aggregate(s=Sum('importo')).values()
        if tot_donazioni[0]:
            context['tot_donazioni'] = tot_donazioni[0]

        context['donazioni_comune'] = Donazione.objects.filter(territorio=t)


        # importi dei progetti per categorie
        context['progetti_categorie'] =  \
            Progetto.objects.filter(territorio=t).values('tipologia').\
            annotate(somma_categoria=Sum('riepilogo_importi'))

        # donazioni divise per tipologia cedente
        context['donazioni_categorie'] = \
            Donazione.objects.filter( territorio=t).\
            filter(confermato = True).values('tipologia').\
            annotate(somma_categoria = Sum('importo'))

        #iban territorio
        iban = Territorio.objects.get(pk = t.pk).iban
        if iban:
            context['iban'] = iban

        #lista progetti per questo territorio in ordine di costo decrescente
        projects = Progetto.objects.filter(territorio = t).order_by('-riepilogo_importi')[:5]

        if projects:
            context['projects_top5'] = projects

        return context

class DonazioneView(TemplateView):

    template_name = "donazioni.html"


    def get_context_data(self, **kwargs):
        context = super(DonazioneView, self).get_context_data(**kwargs)

        # donazioni totali
        tot_donazioni = Donazione.objects.all().aggregate(s=Sum('importo')).values()
        if tot_donazioni:
            context['tot_donazioni']= moneyfmt(tot_donazioni[0],2,"",".",",")

        # importi progetti totale
        tot_danno = Progetto.objects.all().aggregate(s=Sum('riepilogo_importi')).values()
        if tot_danno:
            context['tot_danno'] =  moneyfmt(tot_danno[0],2,"",".",",")

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


        if donazioni_spline:
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


