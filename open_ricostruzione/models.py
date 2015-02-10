from decimal import Decimal
from model_utils import Choices
import time
from django.db import models
from django.conf import settings
from open_ricostruzione.utils.moneydate import moneyfmt, add_months


class InterventoAProgramma(models.Model):
    id_progr = models.SmallIntegerField(null=False, blank=False)
    id_interv_a_progr = models.SmallIntegerField(null=False, blank=False)
    n_ordine = models.CharField(max_length=20, null=False, blank=False)
    importo_generale = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    importo_a_programma = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    id_sogg_att = models.SmallIntegerField(null=False, blank=False)
    territorio = models.ForeignKey('territori.Territorio', null=True)

    id_tipo_imm = models.SmallIntegerField(null=False, blank=False)
    id_categ_imm = models.SmallIntegerField(null=False, blank=False)
    id_propr_imm = models.SmallIntegerField(null=False, blank=False)

    slug = models.SlugField(max_length=60)

    def __unicode__(self):
        return u"{}".format(self.denominazione)

    class Meta:
        verbose_name_plural = u'Interventi a programma'


class Cofinanziamento(models.Model):
    TIPO_COFINANZIAMENTO = Choices()

    tipologia = models.CharField(max_length=2, choices=TIPO_COFINANZIAMENTO, blank=False, null=False, default='')
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    intervento_a_programma = models.ForeignKey('InterventoAProgramma', null=False, blank=False)


class Piano(models.Model):
    TIPO_PIANO = Choices()
    tipologia = models.CharField(max_length=2, choices=TIPO_PIANO, blank=False, null=False, default='')


class InterventoAPiano(models.Model):
    intervento_a_programma = models.ForeignKey('InterventoAProgramma', null=False, blank=False)
    id_interv_a_piano = models.SmallIntegerField(null=False, blank=False)
    imp_a_piano = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    piano = models.ForeignKey('Piano', null=False, blank=False)


class Intervento(models.Model):
    intervento_a_programma = models.ForeignKey('InterventoAPiano', null=False, blank=False)
    id_interv = models.SmallIntegerField(null=False, blank=False)
    is_variante = models.BooleanField(null=False, blank=False, default=False)
    imp_congr_spesa = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    id_tipo_interv = models.SmallIntegerField(null=False, blank=False)
    id_stato_interv = models.SmallIntegerField(null=False, blank=False)


class Liquidazione(models.Model):
    TIPO_LIQUIDAZIONE = Choices()
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_LIQUIDAZIONE, null=False, blank=False, default='')
    data = models.DateField(blank=False, null=False)
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)


class EventoContrattuale(models.Model):
    TIPO_EVENTO = Choices()
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_EVENTO, null=False, blank=False, default='')
    data = models.DateField(blank=False, null=False)


class Impresa(models.Model):
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    ragione_sociale = models.CharField(max_length=200, null=False, blank=False)
    partita_iva = models.CharField(max_length=30, null=False, blank=False)


class QuadroEconomico(models.Model):
    TIPO_QUADRO_ECONOMICO = Choices()
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_QUADRO_ECONOMICO, blank=False, null=False, default='')
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)


class Progetto(models.Model):
    TIPO_PROGETTO = Choices()
    STATO_PROGETTO = Choices()
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_PROGETTO, blank=False, null=False, default='')
    stato_progetto = models.CharField(max_length=2, choices=STATO_PROGETTO, blank=False, null=False, default='')
    data_deposito = models.DateField(blank=False, null=False)


class Donazione(models.Model):
    TIPO_DONAZIONE = Choices(
        (u'1', u'Diretta', u'Diretta'),
        (u'2', u'Regione', u'Regione'),
    )

    TIPO_CEDENTE = Choices(
        (u'0', u'privato', u'privato'),
    )

    territorio = models.ForeignKey('territori.Territorio')
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
