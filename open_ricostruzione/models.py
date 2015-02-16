from decimal import Decimal
from model_utils import Choices
import time
from django.db import models
from django.conf import settings
from open_ricostruzione.utils.moneydate import moneyfmt, add_months


class InterventoProgramma(models.Model):
    TIPO_IMMOBILE = Choices(
        ('1', 'ALTRO', 'ATTR. INFRASTRUTTURE E MOBILITA'),
        ('2', 'ATTR_INFRASTRUTTURE', 'ATTR. INFRASTRUTTURE E MOBILITA'),
        ('3', 'ATTR_INFRASTRUTTURE_FC', 'ATTR. INFRASTRUTTURE E MOBILITA\' - FUORI CRATERE'),
        ('4', 'ATTR_SANITARIE', 'ATTR. SANITARIE E/O SOCIO SANITARIE'),
        ('5', 'ATTR_CIMITERIALI', 'ATTREZZATURE CIMITERIALI'),
        ('6', 'ATTR_CULTURALI', 'ATTREZZATURE CULTURALI'),
        ('7', 'ATTR_SPORTIVE', 'ATTREZZATURE SPORTIVE E RICREATIVE'),
        ('8', 'BENE_RELIGIOSO', 'BENE RELIGIOSO DI PROPRIETA\' DI ENTE PUBBLICO'),
        ('9', 'BENI_DEMANIALI', 'BENI DEMANIALI'),
        ('10', 'BENI_ECCLESIASTICI', 'BENI ECCLESIASTICI'),
        ('11', 'CANONICA_ORATORIO', 'CANONICA/ORATORIO'),
        ('12', 'CHIESA', 'CHIESA'),
        ('13', 'EDILIZIA_SCOLASTICA', 'EDILIZIA SCOLASTICA'),
        ('14', 'EDILIZIA_SOCIALE', 'EDILIZIA SOCIALE'),
        ('15', 'EX_CHIESA', 'EX CHIESA/MONASTERO/ CONVENTO'),
        ('16', 'EX_SCUOLA', 'EX SCUOLA'),
        ('17', 'IMPIANTI_A_RETE', 'IMPIANTI A RETE'),
        ('18', 'MAGAZZINO', 'MAGAZZINO'),
        ('19', 'MONASTERO_CONVENTO_SINAGOGA', 'MONASTERO / CONVENTO / SINAGOGA'),
        ('20', 'MUNICIPI', 'MUNICIPI - UFFICI E ALTRI ENTI PUBBLICI'),
        ('21', 'OPERE_BONIFICA', 'OPERE DI BONIFICA E IRRIGAZIONE'),
        ('22', 'OPERE_BONIFICA_FC', 'OPERE DI BONIFICA E IRRIGAZIONE - FUORI CRATERE'),
        ('23', 'UNIVERSITA', 'UNIVERSITA'),
        ('24', 'ATTR_RICREATIVE', 'ATTREZZATURE RICREATIVE'),
        ('25', 'ATTR_SPORTIVE', 'ATTREZZATURE SPORTIVE'),
        ('26', 'MONASTERO_CONVENTO', 'MONASTERO / CONVENTO'),
        ('27', 'BENI_PRIVATI', 'BENI PRIVATI'),
    )

    CATEGORIA_IMMOBILE = Choices(
        ('1', 'BENI_DEMANIALI', 'Beni Demaniali e Beni ecclesiastici di prop. Pubbl.'),
        ('2', 'ATTR_INFRASTRUTTURE', 'ATTR. INFRASTRUTTURE E MOBILITA'),
        ('3', 'ATTR_INFRASTRUTTURE_FC', 'ATTR. INFRASTRUTTURE E MOBILITA\' - FUORI CRATERE'),
        ('4', 'ATTR_SANITARIE', 'ATTR. SANITARIE E/O SOCIO SANITARIE'),
        ('5', 'ATTR_CIMITERIALI', 'ATTREZZATURE CIMITERIALI'),
        ('6', 'ATTR_CULTURALI', 'ATTREZZATURE CULTURALI'),
        ('7', 'ATTR_SPORTIVE', 'ATTREZZATURE SPORTIVE E RICREATIVE'),
        ('8', 'BENE_RELIGIOSO', 'BENE RELIGIOSO DI PROPRIETA\' DI ENTE PUBBLICO'),
    )

    programma = models.ForeignKey('Programma', null=False, blank=False, default=0)
    # id_interv_a_progr = id fenice per l'intervento
    id_interv_a_progr = models.PositiveSmallIntegerField(null=False, blank=False)
    id_sogg_att = models.PositiveSmallIntegerField(null=False, blank=False)
    # id_propr_imm = id fenice per l'immobile
    id_propr_imm = models.PositiveSmallIntegerField(null=False, blank=False)
    n_ordine = models.CharField(max_length=20, null=False, blank=False)
    importo_generale = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    importo_a_programma = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    territorio = models.ForeignKey('territori.Territorio', null=True)
    tipo_immobile = models.CharField(max_length=2, choices=TIPO_IMMOBILE, blank=False, null=False, default='')
    categ_immobile = models.CharField(max_length=2, choices=CATEGORIA_IMMOBILE, blank=True, null=True, default='')
    slug = models.SlugField(max_length=60, blank=False, null=False, unique=True)

    def __unicode__(self):
        return u"{}".format(self.denominazione)

    class Meta:
        verbose_name_plural = u'Interventi a programma'


class Programma(models.Model):
    TIPO_PROGRAMMA = Choices()
    denominazione = models.TextField(max_length=50)
    id_progr = models.PositiveSmallIntegerField(null=True, blank=True)
    tipologia = models.CharField(max_length=2, choices=TIPO_PROGRAMMA, blank=False, null=False, default='')

    def __unicode__(self):
        return u"id:{} - denominazione:{}".format(self.id_progr, self.denominazione)

    class Meta:
        verbose_name_plural = u'Programmi'


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
    intervento_programma = models.ForeignKey('InterventoProgramma', null=False, blank=False)

    def __unicode__(self):
        return u"({}) {} - {}E".format(self.intervento_programma.pk, self.TIPO_COFINANZIAMENTO[self.tipologia],
                                       self.importo)

    class Meta:
        verbose_name_plural = u'Cofinanziamenti'


class Piano(models.Model):
    TIPO_PIANO = Choices(
        ('1', 'OPERE_PUBBLICHE', 'Piano opere pubbliche'),
        ('2', 'BENI_CULTURALI', 'Piano beni culturali'),
        ('3', 'EDILIZIA_SCOLASTICA', 'Piano edilizia scolastica ed universita'),
        ('4', 'MISTI', 'Piano UMI - misti'),
    )
    # id_piano = id fenice x il piano
    id_piano = models.PositiveSmallIntegerField(null=False, blank=False, default=0)
    tipologia = models.CharField(max_length=2, choices=TIPO_PIANO, blank=False, null=False, default='')

    def __unicode__(self):
        return u"({}) {}".format(self.id_piano, self.TIPO_PIANO[self.tipologia])

    class Meta:
        verbose_name_plural = u'Piani'


class InterventoPiano(models.Model):
    intervento_programma = models.ForeignKey('InterventoProgramma', null=False, blank=False)
    id_interv_a_piano = models.PositiveSmallIntegerField(null=False, blank=False)
    imp_a_piano = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    piano = models.ForeignKey('Piano', null=False, blank=False)

    def __unicode__(self):
        return u"{},{},{},{}".format(self.piano, self.intervento_programma.pk, self.id_interv_a_piano,
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

    intervento_piano = models.ForeignKey('InterventoPiano', null=False, blank=False)
    # id_interv = id fenice per l'intervento
    id_interv = models.PositiveSmallIntegerField(null=False, blank=False)
    is_variante = models.BooleanField(null=False, blank=False, default=False)
    imp_congr_spesa = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    tipologia = models.CharField(max_length=2, choices=TIPO_INTERVENTO, null=False, blank=False, default='')
    stato = models.CharField(max_length=3, choices=STATO_INTERVENTO, null=False, blank=False, default='')
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)

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
    TIPO_EVENTO = Choices(
         ('1', 'STIPULA_CONTRATTO', 'Stipula contratto'),
        ('2', 'INIZIO_LAVORI', 'Inizio lavori'),
        ('3', 'FINE_LAVORI', 'Fine lavori come da Capitolato'),
        ('4', 'VERBALE_CONSEGNA', 'Verbale di consegna lavori'),
    )
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
    TIPO_QUADRO_ECONOMICO = Choices(
        ('1', 'SPESA_COMPLESSIVA', 'Quadro sommario della spesa complessiva'),
        ('2', 'COFINANZIAMENTO_RIMBORSO', 'Quadro sommario del cofinanziamento da Rimborso assicurativo'),
        ('3', 'COFINANZIAMENTO_DONAZIONI', 'Quadro sommario del cofinanziamento da Donazioni'),
        ('4', 'COFINANZIAMENTO_OPERE', 'Quadro sommario del cofinanziamento da Opere provvisionali'),
        ('5', 'COFINANZIAMENTO_MESSE_SICUREZZA', 'Quadro sommario del cofinanziamento da Messe in sicurezza'),
        ('6', 'COFINANZIAMENTO_EDIFICI_SCOLASTICI',
         'Quadro sommario del cofinanziamento da Ricostruzione edifici scolastici'),
        ('7', 'COFINANZIAMENTO_FONDI_PROPRI', 'Quadro sommario del cofinanziamento da Fondi propri (e altro)'),
        ('8', 'SOMMARIO_GENERALE', 'Quadro sommario generale riepilogativo'),
        ('9', 'QTE_COMMISSARIO', 'Q.T.E. relativo al finanziamento del Commissario'),
        ('10', 'QTE_ASSICURATIVO', 'Q.T.E. riferito al cofinanziamento da Rimborso assicurativo'),
        ('11', 'QTE_DONAZIONI', 'Q.T.E. riferito al cofinanziamento da Donazioni'),
        ('12', 'QTE_OPERE', 'Q.T.E. riferito al cofinanziamento da Opere provvisionali'),
        ('13', 'QTE_MESSE_SICUREZZA', 'Q.T.E. riferito al cofinanziamento da Messe in sicurezza'),
        ('14', 'QTE_EDIFICI_SCOLASTICI', 'Q.T.E. riferito al cofinanziamento da Ricostruzione edifici scolastici'),
        ('15', 'QTE_FONDI_PROPRI', 'Q.T.E. riferito al cofinanziamento da Fondi propri (e altro)'),
        ('16', 'QTE_GENERALE', 'Q.T.E. generale riepilogativo'),
        ('17', 'QTE_RIMODULATO_COMMISSARIO', 'Q.T.E. rimodulato relativo al finanziamento del Commissario'),
    )
    tipologia = models.CharField(max_length=2, choices=TIPO_QUADRO_ECONOMICO, blank=False, null=False, default='')
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)

    class Meta:
        abstract = True


class QuadroEconomicoProgetto(QuadroEconomico):
    progetto = models.ForeignKey('Progetto', null=False, blank=False)

    class Meta:
        verbose_name_plural = u'Quadro Economico Progetto'

    def __unicode__(self):
        return "({}) {} - {} E".format(self.progetto.pk, self.TIPO_QUADRO_ECONOMICO[self.tipologia], self.importo)


class QuadroEconomicoIntervento(QuadroEconomico):
    intervento = models.ForeignKey('Intervento', null=False, blank=False)

    class Meta:
        verbose_name_plural = u'Quadro Economico Intervento'

    def __unicode__(self):
        return "({}) {} - {} E".format(self.intervento.pk, self.TIPO_QUADRO_ECONOMICO[self.tipologia], self.importo)


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
        return u"{}".format(self.denominazione)

    #    ritorna l'importo lavori in formato italiano
    def get_importo_ita(self):
        return moneyfmt(self.importo, 2, "", ".", ",")

    class Meta:
        verbose_name_plural = u'Donazioni'
