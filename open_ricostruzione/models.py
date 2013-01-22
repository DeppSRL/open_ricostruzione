from decimal import Decimal
from django.db import models
from django.db import connections
from datetime import datetime
import time
from open_ricostruzione.utils.moneydate import moneyfmt,add_months
from django.db.models.aggregates import Sum, Count
from datetime import timedelta
from django.template.defaultfilters import slugify
from django.template.defaultfilters import date as _date
from django.conf import settings


class UltimoAggiornamento(models.Model):
    data_progetti = models.DateTimeField()
    data_donazioni = models.DateTimeField()

    class Meta:
        verbose_name_plural = u'Ultimo Aggiornamento'


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
    marker_max_size= 8000
    marker_min_size= 1000

    def __unicode__(self):
        return u"%s (%s)" % (self.denominazione, self.cod_comune)

    class Meta:
        verbose_name_plural = u'Territori'

    def get_danno(self):
        return Progetto.objects.filter(territorio=self, id_padre__isnull = True).\
               aggregate(s=Sum('riepilogo_importi')).values()[0]

    def get_donazioni(self):
        return Donazione.objects.filter(territorio=self, confermato = True).aggregate(s=Sum('importo')).values()[0]


    #    ritorna l'importo del danno in formato italiano
    def get_danno_ita(self):
        if self.get_danno():
            return moneyfmt(self.get_danno(),2,"",".",",")
        else:
            return "0,00"

    #    ritorna l'importo delle donazioni in formato italiano
    def get_donazioni_ita(self):
        if self.get_donazioni():
            return moneyfmt(self.get_donazioni(),2,"",".",",")
        else:
            return "0,00"



    def get_percentuale_donazioni(self):

        danno = self.get_danno()
        donazioni =  self.get_donazioni()
        if danno:
            if donazioni:
                return (100 * donazioni)/danno
            else:
                return 0
        else:
            return None

    def get_angolo_donazioni(self):

        perc =  self.get_percentuale_donazioni()
        if perc:
            return (perc*360)/100
        else:
            return None

    def get_marker_size(self):

        biggest_damage=Territorio.objects.\
                       filter(cod_comune__in=Territorio.get_territori_attivi()).\
                        annotate(s=Sum('progetto__riepilogo_importi')).order_by('-s').\
                        values_list('s',flat=True)[0]
        danno=self.get_danno()
        if danno and biggest_damage:
            return self.marker_min_size+((danno/biggest_damage)*self.marker_max_size)*Decimal('0.45')
        else:
            return 0



    def get_comuni_with_progetti(self):
        return Territorio.objects.filter(tipo_territorio="C", cod_provincia = self.cod_provincia).\
                filter(progetto__isnull = False).\
                order_by("denominazione").distinct()

    def get_provincia(self):
        if self.tipo_territorio != "P":
            return Territorio.objects.get(tipo_territorio="P", cod_provincia = self.cod_provincia)
        else:
            return None



    def get_spline_data(self):

        #tutte le donazioni nel tempo per il comune self
        #le donazioni vengono espresse con valori incrementali rispetto alla somma delle donazioni
        # del mese precedente. In questo modo se un mese le donazioni sono 0 la retta del grafico e' piatta

        donazioni_mese = Donazione.objects.filter(territorio = self).\
            extra(select={'date': connections[Donazione.objects.db].ops.date_trunc_sql('month', 'data')}).\
            values('date').annotate(sum = Sum('importo')).order_by('date')

        donazioni_spline =[]
        j = 0


        for idx, val in enumerate(donazioni_mese):
##            converto la data nel formato  Nome mese - Anno
            if type(val['date']).__name__=="datetime":
                val_date_obj = val['date']
            else:
                val_date_obj = datetime.strptime(val['date'],"%Y-%m-%d %H:%M:%S")

            val_date_print=_date(val_date_obj,"M - Y")

            if idx is not 0:
#                se le due date sono piu' distanti di un mese
#                inserisce tanti mesi quanti mancano con un importo uguale all'ultimo importo disponibile
#                per creare un grafico piatto
                if type(val['date']).__name__=="datetime":
                    donazioni_date_obj = donazioni_mese[idx-1]['date']
                else:
                    donazioni_date_obj = datetime.strptime(donazioni_mese[idx-1]['date'],"%Y-%m-%d %H:%M:%S")

                if (val_date_obj-donazioni_date_obj) > timedelta(31):
                    n_mesi = (val_date_obj - donazioni_date_obj).days / 28
                    for k in range(1, n_mesi):
                        new_month_obj = add_months(donazioni_date_obj,k)
                        new_month_print = _date(new_month_obj,"M - Y")

                        donazioni_spline.append({
                            'month':new_month_print,
                            'sum':Decimal(donazioni_spline[j-1]['sum']),
                            'sum_ita':None,
                        })
                        j += 1

#               inserisce il dato del mese corrente
                donazioni_spline.append({
                    'month':val_date_print,
                    'sum':Decimal(donazioni_spline[j-1]['sum'])+Decimal(val['sum']),
                    'sum_ita':None,
                })
                j += 1

            else:
                donazioni_spline.append({
                    'month':val_date_print,
                    'sum':Decimal(val['sum']),
                    'sum_ita':None,
                })
                j += 1


        for d in donazioni_spline:
            d['sum']=moneyfmt(Decimal(d['sum']),2,"","",".")
            d['sum_ita']=moneyfmt(Decimal(d['sum']),2,"",".",",")

        return donazioni_spline

#    get_territori_attivi restituisce la lista dei codici comune dei territori in cui abbiamo almeno un progetto attivo
    @classmethod
    def get_territori_attivi(cls):
        return Territorio.objects.filter(tipo_territorio = "C",cod_comune__in=settings.COMUNI_CRATERE).\
            annotate(c = Count("progetto")).filter(c__gt=0).order_by("-cod_provincia").values_list('cod_comune',flat=True)


    @classmethod
    def get_boundingbox_minlat(cls):
        return Territorio.objects.\
               filter(gps_lat__gt=0).order_by('gps_lat').values_list('gps_lat',flat=True)[0]
    @classmethod
    def get_boundingbox_maxlat(cls):
        return Territorio.objects.\
               filter(gps_lat__gt=0).order_by('-gps_lat').values_list('gps_lat',flat=True)[0]

    @classmethod
    def get_boundingbox_minlon(cls):
        return Territorio.objects.\
               filter(gps_lat__gt=0).order_by('gps_lon').values_list('gps_lon',flat=True)[0]
    @classmethod
    def get_boundingbox_maxlon(cls):
        return Territorio.objects.\
               filter(gps_lat__gt=0).order_by('-gps_lon').values_list('gps_lon',flat=True)[0]




    @classmethod
    def get_map_center_lat(cls):
        lat_max=Territorio.objects.\
            filter(cod_comune__in=Territorio.get_territori_attivi()).\
            filter(gps_lat__gt=0).order_by('-gps_lat').values_list('gps_lat',flat=True)[0]

        lat_min=Territorio.objects.\
                filter(cod_comune__in=Territorio.get_territori_attivi()).\
                filter(gps_lat__gt=0).order_by('gps_lat').values_list('gps_lat',flat=True)[0]
        if lat_max and lat_min:
            return lat_min+(lat_max-lat_min)/2
        else:
            return None

    @classmethod
    def get_map_center_lon(cls):
        lon_max=Territorio.objects.\
            filter(cod_comune__in=Territorio.get_territori_attivi()).\
            filter(gps_lon__gt=0).order_by('-gps_lon').values_list('gps_lon',flat=True)[0]
        lon_min=Territorio.objects.\
            filter(cod_comune__in=Territorio.get_territori_attivi()).\
            filter(gps_lon__gt=0).order_by('gps_lon').values_list('gps_lon',flat=True)[0]
        if lon_max and lon_min:
            return lon_min+(lon_max-lon_min)/2
        else:
            return None



class TipologiaProgetto(models.Model):
    codice = models.SmallIntegerField(null=True, blank=True)
    denominazione = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)

    def __unicode__(self):
        return u"%s" % self.denominazione

    class Meta:
        verbose_name_plural = u'Tipologia Progetti'

class Progetto(models.Model):

    id_progetto = models.CharField(max_length=6)
    id_padre = models.CharField(max_length=6, blank=True, null=True)
    tipologia = models.ForeignKey('TipologiaProgetto', null=False)
    territorio = models.ForeignKey('Territorio', null=True)
    importo_previsto = models.TextField(max_length=4096)
    riepilogo_importi = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    denominazione = models.TextField(max_length=4096)
    slug = models.SlugField(max_length=60)
    parent = models.ForeignKey('Progetto', null=True)
    ubicazione = models.CharField(max_length=500)
    tempi_di_realizzazione = models.TextField()
    stato_attuale = models.TextField()
    interventi_previsti = models.TextField()
    epoca = models.TextField()
    cenni_storici = models.TextField()
    ulteriori_info = models.TextField()


#    ritorna l'importo lavori in formato italiano
    def get_riepilogo_importi_ita(self):
        if self.riepilogo_importi:
            return moneyfmt(self.riepilogo_importi,2,"",".",",")
        else:
            return "0,00"

    def get_donazioni_ita(self):
        donazioni_p = Donazione.objects.filter(progetto=self).aggregate(sum=Sum('importo')).values()
        if donazioni_p[0]:
            return moneyfmt(donazioni_p[0],2,"",".",",")
        else:
            return "0,00"

    def __unicode__(self):
        return u"%s ID: %s, TIPOLOGIA: %s, PADRE: [%s]" % (self.denominazione, self.id_progetto, self.tipologia, self.parent)

    class Meta:
        verbose_name_plural = u'Progetti'


class TipologiaCedente(models.Model):
    codice = models.SmallIntegerField(null=True, blank=True)
    denominazione = models.CharField(max_length=255)
    slug=models.SlugField(max_length=60)

    def __unicode__(self):
        return u"%s - %s" % (self.codice, self.denominazione)

    class Meta:
        verbose_name_plural = u'Tipologia Cedenti'


class Donazione(models.Model):

    id_donazione = models.CharField(max_length=6)
    territorio = models.ForeignKey('Territorio')
    denominazione = models.TextField(max_length=1000)
    info = models.TextField(max_length=1000,null=True, blank=True)
    modalita_r = models.TextField(max_length=20,null=True, blank=True)
    tipologia = models.ForeignKey('TipologiaCedente')
    data = models.DateField()
    avvenuto = models.BooleanField()
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    confermato = models.BooleanField()
    progetto = models.ForeignKey('Progetto',null=True, blank=True)

    def __unicode__(self):
        return u"%s (ID: %s, Data:%s)" % (self.denominazione, self.id, self.data)

    #    ritorna l'importo lavori in formato italiano
    def get_importo_ita(self):
        return moneyfmt(self.importo,2,"",".",",")

    def detail(self):
        return u"%s (ID: %s, territorio:%s, tipologia:%s, progetto:%s, avvenuto:%s, conf:%s)" % (self.denominazione, self.id, self.territorio_id, self.tipologia_id, self.progetto_id, self.avvenuto, self.confermato)


    class Meta:
        verbose_name_plural = u'Donazioni'



class Entry(models.Model):

    title= models.CharField(max_length=255)
    abstract=models.CharField(max_length=255)
    author=models.CharField(max_length=255, null=True, blank=True)
    body= models.TextField()
    published_at= models.DateTimeField(default=datetime.now())
    slug=models.SlugField(max_length=60, blank=True)

    def __unicode__(self):
        return self.title


    class Meta():
        ordering= ['-published_at']
        verbose_name= 'articolo'
        verbose_name_plural= 'articoli'

    def save(self):
        super(Entry, self).save()

        if self.published_at:
            self.slug = '%s-%s%s%s-%i' % (
                slugify(self.title), self.published_at.day,self.published_at.month,self.published_at.year, self.id
            )
        else:
            self.slug = '%s-%i' % (
                slugify(self.title), self.id
                )
        super(Entry, self).save()


class Blog(object):

    @staticmethod
    def get_latest_entries(qnt=10, end_date=None, start_date=None, single=False):
        end_date = end_date or datetime.now()
        qnt = qnt if not single else 1

        if start_date:
            entries = Entry.objects.filter(published_at__range=(start_date, end_date))[:qnt]
        else :
            entries = Entry.objects.filter(published_at__lte=end_date)[:qnt]

        if single :
            return entries[0] if entries else None

        return entries