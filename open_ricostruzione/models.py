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
    id_categ_imm = models.SmallIntegerField(null=True, blank=True)
    id_propr_imm = models.SmallIntegerField(null=False, blank=False)

    slug = models.SlugField(max_length=60)

    def __unicode__(self):
        return u"{}".format(self.denominazione)

    class Meta:
        verbose_name_plural = u'Interventi a programma'


class Cofinanziamento(models.Model):
    TIPO_COFINANZIAMENTO = Choices(
        ('1', 'ASSICURAZIONE', 'Assicurazione'),
        ('2', 'DONAZIONI', 'Donazioni'),
        ('3', 'OPERE_PROVVISIONALI', 'Opere provvisionali'),
        ('4', 'MESSA_IN_SICUREZZA', 'Messa in sicurezza'),
        ('5', 'FONDI_PROPRI', 'Fondi propri'),
        ('6', 'EDILIZIA_SCOLASTICA', 'Edilizia scolastica'),
    )

    tipologia = models.CharField(max_length=2, choices=TIPO_COFINANZIAMENTO, blank=False, null=False, default='')
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    intervento_a_programma = models.ForeignKey('InterventoAProgramma', null=False, blank=False)

    def __unicode__(self):
        return u"{},{},{}".format(self.intervento_a_programma.pk, self.tipologia, self.importo)

    class Meta:
        verbose_name_plural = u'Cofinanziamenti'


class Piano(models.Model):
    TIPO_PIANO = Choices(
        ('1', 'OPERE_PUBBLICHE', 'Piano opere pubbliche'),
        ('2', 'BENI_CULTURALI', 'Piano beni culturali'),
        ('3', 'EDILIZIA_SCOLASTICA', 'Piano edilizia scolastica ed universita'),
        ('4', 'MISTI', 'Piano UMI - misti'),
    )

    tipologia = models.CharField(max_length=2, choices=TIPO_PIANO, blank=False, null=False, default='')


class InterventoAPiano(models.Model):
    intervento_a_programma = models.ForeignKey('InterventoAProgramma', null=False, blank=False)
    id_interv_a_piano = models.SmallIntegerField(null=False, blank=False)
    imp_a_piano = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    piano = models.ForeignKey('Piano', null=False, blank=False)

    def __unicode__(self):
        return u"{},{},{},{}".format(self.piano, self.intervento_a_programma.pk, self.id_interv_a_piano,
                                     self.imp_a_piano)

    class Meta:
        verbose_name_plural = u'Interventi a piano'


class Intervento(models.Model):
    TIPO_INTERVENTO = Choices(
        ('1', 'RIPARAZIONE_RAFFORZAMENTO', 'Riparazione con rafforzamento locale'),
        ('2', 'RIPRISTINO', 'Ripristino con miglioramento sismico'),
        ('3', 'DEMOLIZIONE', 'Demolizione e ricostruzione e/o nuova costruzione'),
        ('4', 'NON_STRUTTURALE', 'Intervento non strutturale'),
    )

    STATO_INTERVENTO = Choices(
        ('1', 'A_PIANO', 'A piano'),
        ('2', 'BOZZA', 'In bozza'),
        ('3', 'PRESENTATO', 'Presentato'),
        ('4', 'AMMESSO', 'Ammesso'),
        ('5', 'RESPINTO', 'Respinto'),
        ('6', 'FONDI_ASSEGNATI', 'Fondi assegnati'),
        ('7', 'RINUNCIATO', 'Rinunciato'),
        ('8', '2_ACCONTO', '2 acconto'),
        ('9', '3_ACCONTO', '3 acconto'),
        ('10', 'SALDO', 'Saldo'),
        ('11', 'CHIUSO', 'Chiuso'),
        ('12', 'SOSTITUITO', 'Sostituito da variante'),
    )

    intervento_a_programma = models.ForeignKey('InterventoAPiano', null=False, blank=False)
    id_interv = models.SmallIntegerField(null=False, blank=False)
    is_variante = models.BooleanField(null=False, blank=False, default=False)
    imp_congr_spesa = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    tipologia = models.CharField(max_length=2, choices=TIPO_INTERVENTO, null=False, blank=False, default='')
    stato = models.CharField(max_length=3, choices=STATO_INTERVENTO, null=False, blank=False, default='')


    class Meta:
        verbose_name_plural = u'Interventi'


class Liquidazione(models.Model):
    TIPO_LIQUIDAZIONE = Choices(
        ('1000', 'PRIMO_ACCONTO', 'Primo acconto'),
        ('1100', 'BOZZA', 'In bozza'),
        ('1110', 'PRESENTATO', 'Presentato'),
        ('1111', 'AMMESSO', 'Ammesso'),
        ('0100', 'RESPINTO', 'Respinto'),
        ('0010', 'FONDI_ASSEGNATI', 'Fondi assegnati'),
        ('0001', 'RINUNCIATO', 'Rinunciato'),
        ('0110', '2_ACCONTO', '2 acconto'),
        ('0111', '3_ACCONTO', '3 acconto'),
        ('0011', 'SALDO', 'Saldo'),
    )

    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=5, choices=TIPO_LIQUIDAZIONE, null=False, blank=False, default='')
    data = models.DateField(blank=False, null=False)
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)

    class Meta:
        verbose_name_plural = u'Liquidazioni'


class EventoContrattuale(models.Model):
    TIPO_EVENTO = Choices()
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_EVENTO, null=False, blank=False, default='')
    data = models.DateField(blank=False, null=False)

    class Meta:
        verbose_name_plural = u'Eventi contrattuali'


class Impresa(models.Model):
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    ragione_sociale = models.CharField(max_length=200, null=False, blank=False)
    partita_iva = models.CharField(max_length=30, null=False, blank=False)

    class Meta:
        verbose_name_plural = u'Imprese'


class QuadroEconomico(models.Model):
    TIPO_QUADRO_ECONOMICO = Choices()
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_QUADRO_ECONOMICO, blank=False, null=False, default='')
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)

    class Meta:
        verbose_name_plural = u'Quadro economico'


class Progetto(models.Model):
    TIPO_PROGETTO = Choices(
        ('1', 'PROGETTO_PRELIMINARE', 'Progetto preliminare'),
        ('2', 'PROGETTO_DEFINITIVO', 'Progetto definitivo'),
        ('3', 'PROGETTO_ESECUTIVO', 'Progetto esecutivo'),
        ('4', 'PERIZIA_SISMICA', 'Perizia sismica'),
        ('5', 'PERIZIA_DEMOLIZIONE_RIPRISTINO', 'Perizia demolizione con progetto di ripristino'),
        ('6', 'PERIZIA_DEMOLIZIONE_CONVENZIONALE', 'Perizia demolizione con calcolo convenzionale'),
        ('7', 'CALCOLO_CONVENZIONALE', 'Calcolo convenzionale'),
    )

    STATO_PROGETTO = Choices(
        ('1', 'BOZZA', 'In bozza'),
        ('2', 'PRESENTATO', 'Presentato'),
        ('3', 'PRESO_IN_CARICO', 'Preso in carico'),
        ('4', 'ISTRUTTORIA', 'In istruttoria'),
        ('5', 'RESPINTO', 'Respinto'),
        ('6', 'AMMESSO', 'Ammesso'),
    )
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_PROGETTO, blank=False, null=False, default='')
    stato_progetto = models.CharField(max_length=2, choices=STATO_PROGETTO, blank=False, null=False, default='')
    data_deposito = models.DateField(blank=False, null=False)

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
