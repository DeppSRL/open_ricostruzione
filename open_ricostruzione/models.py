from decimal import Decimal
# from django.contrib.markup.templatetags.markup import markdown
from django.db import models
from model_utils import Choices
from django.db import connections
from datetime import datetime
import time
from open_ricostruzione.utils.moneydate import moneyfmt, add_months
from django.db.models.aggregates import Sum, Count
from datetime import timedelta
from django.template.defaultfilters import slugify
from django.template.defaultfilters import date as _date
from django.conf import settings


class Territorio(models.Model):
    tipo_territorio = models.CharField(max_length=2)
    cod_comune = models.CharField(max_length=10)
    cod_provincia = models.CharField(max_length=3)
    denominazione = models.CharField(max_length=255)
    iban = models.CharField(max_length=30, null=True, blank=True)
    tipologia_cc = models.CharField(max_length=2, null=True, blank=True)
    slug = models.SlugField(max_length=60)
    sigla_provincia = models.CharField(max_length=3, null=True, blank=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    marker_max_size = 8000
    marker_min_size = 1000

    def __unicode__(self):
        return u"%s (%s)" % (self.denominazione, self.cod_comune)

    class Meta:
        verbose_name_plural = u'Territori'

    def get_danno(self):
        return Progetto.objects.filter(territorio=self, id_padre__isnull=True). \
            aggregate(s=Sum('riepilogo_importi')).values()[0]

    def get_donazioni(self):
        return Donazione.objects.filter(territorio=self, confermato=True).aggregate(s=Sum('importo')).values()[0]


    #    ritorna l'importo del danno in formato italiano
    def get_danno_ita(self):
        if self.get_danno():
            return moneyfmt(self.get_danno(), 2, "", ".", ",")
        else:
            return "0,00"

    #    ritorna l'importo delle donazioni in formato italiano
    def get_donazioni_ita(self):
        if self.get_donazioni():
            return moneyfmt(self.get_donazioni(), 2, "", ".", ",")
        else:
            return "0,00"


    def get_percentuale_donazioni(self):

        danno = self.get_danno()
        donazioni = self.get_donazioni()
        if danno:
            if donazioni:
                return (100 * donazioni) / danno
            else:
                return 0
        else:
            return None

    def get_angolo_donazioni(self):

        perc = self.get_percentuale_donazioni()
        if perc:
            return (perc * 360) / 100
        else:
            return None

    def get_marker_size(self):

        biggest_damage = Territorio.objects. \
            filter(cod_comune__in=Territorio.get_territori_attivi()). \
            annotate(s=Sum('progetto__riepilogo_importi')).order_by('-s'). \
            values_list('s', flat=True)[0]
        danno = self.get_danno()
        if danno and biggest_damage:
            return self.marker_min_size + ((danno / biggest_damage) * self.marker_max_size) * Decimal('0.45')
        else:
            return 0


    def get_comuni_with_progetti(self):
        return Territorio.objects.filter(tipo_territorio="C", cod_provincia=self.cod_provincia). \
            filter(progetto__isnull=False). \
            order_by("denominazione").distinct()

    def get_provincia(self):
        if self.tipo_territorio != "P":
            return Territorio.objects.get(tipo_territorio="P", cod_provincia=self.cod_provincia)
        else:
            return None


    def get_spline_data(self):

        #tutte le donazioni nel tempo per il comune self
        #le donazioni vengono espresse con valori incrementali rispetto alla somma delle donazioni
        # del mese precedente. In questo modo se un mese le donazioni sono 0 la retta del grafico e' piatta

        donazioni_mese = Donazione.objects.filter(territorio=self). \
            extra(select={'date': connections[Donazione.objects.db].ops.date_trunc_sql('month', 'data')}). \
            values('date').annotate(sum=Sum('importo')).order_by('date')

        donazioni_spline = []
        j = 0

        for idx, val in enumerate(donazioni_mese):
        ##            converto la data nel formato  Nome mese - Anno
            if type(val['date']).__name__ == "datetime":
                val_date_obj = val['date']
            else:
                val_date_obj = datetime.strptime(val['date'], "%Y-%m-%d %H:%M:%S")

            val_date_print = _date(val_date_obj, "M - Y")

            if idx is not 0:
            #                se le due date sono piu' distanti di un mese
            #                inserisce tanti mesi quanti mancano con un importo uguale all'ultimo importo disponibile
            #                per creare un grafico piatto
                if type(val['date']).__name__ == "datetime":
                    donazioni_date_obj = donazioni_mese[idx - 1]['date']
                else:
                    donazioni_date_obj = datetime.strptime(donazioni_mese[idx - 1]['date'], "%Y-%m-%d %H:%M:%S")

                if (val_date_obj - donazioni_date_obj) > timedelta(31):
                    n_mesi = (val_date_obj - donazioni_date_obj).days / 28
                    for k in range(1, n_mesi):
                        new_month_obj = add_months(donazioni_date_obj, k)
                        new_month_print = _date(new_month_obj, "M - Y")

                        donazioni_spline.append({
                            'month': new_month_print,
                            'sum': Decimal(donazioni_spline[j - 1]['sum']),
                            'sum_ita': None,
                        })
                        j += 1

                        #               inserisce il dato del mese corrente
                donazioni_spline.append({
                    'month': val_date_print,
                    'sum': Decimal(donazioni_spline[j - 1]['sum']) + Decimal(val['sum']),
                    'sum_ita': None,
                })
                j += 1

            else:
                donazioni_spline.append({
                    'month': val_date_print,
                    'sum': Decimal(val['sum']),
                    'sum_ita': None,
                })
                j += 1

        for d in donazioni_spline:
            d['sum'] = moneyfmt(Decimal(d['sum']), 2, "", "", ".")
            d['sum_ita'] = moneyfmt(Decimal(d['sum']), 2, "", ".", ",")

        return donazioni_spline

    #    get_territori_attivi restituisce la lista dei codici comune dei territori in cui abbiamo almeno un progetto attivo
    @classmethod
    def get_territori_attivi(cls):
        return Territorio.objects.filter(tipo_territorio="C", cod_comune__in=settings.COMUNI_CRATERE). \
            annotate(c=Count("progetto")).filter(c__gt=0).order_by("-cod_provincia").values_list('cod_comune',
                                                                                                 flat=True)


    @classmethod
    def get_boundingbox_minlat(cls):
        return Territorio.objects. \
            filter(gps_lat__gt=0).order_by('gps_lat').values_list('gps_lat', flat=True)[0]

    @classmethod
    def get_boundingbox_maxlat(cls):
        return Territorio.objects. \
            filter(gps_lat__gt=0).order_by('-gps_lat').values_list('gps_lat', flat=True)[0]

    @classmethod
    def get_boundingbox_minlon(cls):
        return Territorio.objects. \
            filter(gps_lat__gt=0).order_by('gps_lon').values_list('gps_lon', flat=True)[0]

    @classmethod
    def get_boundingbox_maxlon(cls):
        return Territorio.objects. \
            filter(gps_lat__gt=0).order_by('-gps_lon').values_list('gps_lon', flat=True)[0]

    @classmethod
    def get_map_center_lat(cls):
        lat_max = Territorio.objects. \
            filter(cod_comune__in=Territorio.get_territori_attivi()). \
            filter(gps_lat__gt=0).order_by('-gps_lat').values_list('gps_lat', flat=True)[0]

        lat_min = Territorio.objects. \
            filter(cod_comune__in=Territorio.get_territori_attivi()). \
            filter(gps_lat__gt=0).order_by('gps_lat').values_list('gps_lat', flat=True)[0]
        if lat_max and lat_min:
            return lat_min + (lat_max - lat_min) / 2
        else:
            return None

    @classmethod
    def get_map_center_lon(cls):
        lon_max = Territorio.objects. \
            filter(cod_comune__in=Territorio.get_territori_attivi()). \
            filter(gps_lon__gt=0).order_by('-gps_lon').values_list('gps_lon', flat=True)[0]
        lon_min = Territorio.objects. \
            filter(cod_comune__in=Territorio.get_territori_attivi()). \
            filter(gps_lon__gt=0).order_by('gps_lon').values_list('gps_lon', flat=True)[0]
        if lon_max and lon_min:
            return lon_min + (lon_max - lon_min) / 2
        else:
            return None


class Progetto(models.Model):
    territorio = models.ForeignKey('Territorio', null=True)
    importo_previsto = models.TextField(max_length=4096)
    denominazione = models.TextField(max_length=4096)
    slug = models.SlugField(max_length=60)

    def __unicode__(self):
        return u"{}".format(self.denominazione)

    class Meta:
        verbose_name_plural = u'Progetti'


class Donazione(models.Model):
    TIPO_DONAZIONE = Choices(
        (u'1', u'Diretta', u'Diretta'),
        (u'2', u'Regione', u'Regione'),
    )

    TIPO_CEDENTE = Choices(
        (u'0', u'privato', u'privato'),
    )

    territorio = models.ForeignKey('Territorio')
    denominazione = models.CharField(max_length=256)
    informazioni = models.TextField(max_length=800, blank=True, null=True, default=None)
    tipologia_cedente = models.CharField(max_length=2, choices=TIPO_CEDENTE, blank=False, null=False, default='')
    tipologia_donazione = models.CharField(max_length=2, choices=TIPO_DONAZIONE, blank=False, null=False, default='')
    data = models.DateField(null=True, blank=True)
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, blank=False, null=False, )

    def __unicode__(self):
        return "{}".format(self.denominazione)

    #    ritorna l'importo lavori in formato italiano
    def get_importo_ita(self):
        return moneyfmt(self.importo, 2, "", ".", ",")

    class Meta:
        verbose_name_plural = u'Donazioni'
