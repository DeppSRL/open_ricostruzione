from django.db import models
from django.db import connections
from datetime import datetime
import time
from open_ricostruzione.utils.moneydate import add_months
from django.db.models.aggregates import Sum
from datetime import timedelta

class Territorio(models.Model):

    tipo_territorio = models.CharField(max_length=2)
    cod_comune = models.CharField(max_length=10)
    cod_provincia = models.CharField(max_length=3)
    denominazione = models.CharField(max_length=255)
    iban = models.CharField(max_length=30, null=True, blank=True)
    slug = models.SlugField(max_length=60)
    sigla_provincia = models.CharField(max_length=3, null=True, blank=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.denominazione, self.cod_comune)

    class Meta:
        verbose_name_plural = u'Territori'

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

        return donazioni_spline

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

    def __unicode__(self):
        return u"%s ID: %s, TIPOLOGIA: %s, PADRE: [%s]" % (self.denominazione, self.id_progetto, self.tipologia, self.parent)

    class Meta:
        verbose_name_plural = u'Progetti'


class TipologiaCedente(models.Model):
    codice = models.SmallIntegerField(null=True, blank=True)
    denominazione = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s - %s" % (self.codice, self.denominazione)

    class Meta:
        verbose_name_plural = u'Tipologia Cedenti'


class Donazione(models.Model):

    id_donazione = models.CharField(max_length=6)
    territorio = models.ForeignKey('Territorio')
    denominazione = models.TextField(max_length=1000)
    tipologia = models.ForeignKey('TipologiaCedente')
    data = models.DateField()
    avvenuto = models.BooleanField()
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    confermato = models.BooleanField()

    def __unicode__(self):
        return u"%s (ID: %s, Data:%s)" % (self.denominazione, self.id, self.data)

    class Meta:
        verbose_name_plural = u'Donazioni'

