# -*- coding: utf-8 -*-
from model_utils import Choices
from django.db import models
from django.db.models import Q
from aggregate_if import Count, Sum
from managers import ProgrammatiManager, PianificatiManager, AttuazioneManager, ProgettazioneManager, InCorsoManager, ConclusiManager, VariantiManager
from open_ricostruzione.utils.moneydate import moneyfmt


class Impresa(models.Model):
    ragione_sociale = models.CharField(max_length=200, null=False, blank=False)
    partita_iva = models.CharField(max_length=30, null=False, blank=False, unique=True)
    slug = models.SlugField(max_length=60, blank=False, null=False, unique=True)

    class Meta:
        verbose_name_plural = u'Imprese'

    def __unicode__(self):
        return u"{},{}".format(self.ragione_sociale, self.partita_iva)


class InterventoProgramma(models.Model):
    TIPO_IMMOBILE_FENICE = Choices(
        (u'1', u'ALTRO', u'ALTRO'),
        (u'2', u'ATTR_INFRASTRUTTURE', u'ATTR. INFRASTRUTTURE E MOBILITA'),
        (u'3', u'ATTR_INFRASTRUTTURE_FC', u'ATTR. INFRASTRUTTURE E MOBILITA\' - FUORI CRATERE'),
        (u'4', u'ATTR_SANITARIE', u'ATTR. SANITARIE E/O SOCIO SANITARIE'),
        (u'5', u'ATTR_CIMITERIALI', u'ATTREZZATURE CIMITERIALI'),
        (u'6', u'ATTR_CULTURALI', u'ATTREZZATURE CULTURALI'),
        (u'7', u'ATTR_SPORTIVE', u'ATTREZZATURE SPORTIVE E RICREATIVE'),
        (u'8', u'BENE_RELIGIOSO', u'BENE RELIGIOSO DI PROPRIETA\' DI ENTE PUBBLICO'),
        (u'9', u'BENI_DEMANIALI', u'BENI DEMANIALI'),
        (u'10', u'BENI_ECCLESIASTICI', u'BENI ECCLESIASTICI'),
        (u'11', u'CANONICA_ORATORIO', u'CANONICA/ORATORIO'),
        (u'12', u'CHIESA', u'CHIESA'),
        (u'13', u'EDILIZIA_SCOLASTICA', u'EDILIZIA SCOLASTICA'),
        (u'14', u'EDILIZIA_SOCIALE', u'EDILIZIA SOCIALE'),
        (u'15', u'EX_CHIESA', u'EX CHIESA/MONASTERO/ CONVENTO'),
        (u'16', u'EX_SCUOLA', u'EX SCUOLA'),
        (u'17', u'IMPIANTI_A_RETE', u'IMPIANTI A RETE'),
        (u'18', u'MAGAZZINO', u'MAGAZZINO'),
        (u'19', u'MONASTERO_CONVENTO_SINAGOGA', u'MONASTERO / CONVENTO / SINAGOGA'),
        (u'20', u'MUNICIPI', u'MUNICIPI - UFFICI E ALTRI ENTI PUBBLICI'),
        (u'21', u'OPERE_BONIFICA', u'OPERE DI BONIFICA E IRRIGAZIONE'),
        (u'22', u'OPERE_BONIFICA_FC', u'OPERE DI BONIFICA E IRRIGAZIONE - FUORI CRATERE'),
        (u'23', u'UNIVERSITA', u'UNIVERSITA'),
        (u'24', u'ATTR_RICREATIVE', u'ATTREZZATURE RICREATIVE'),
        (u'25', u'ATTR_SPORTIVE', u'ATTREZZATURE SPORTIVE'),
        (u'26', u'MONASTERO_CONVENTO', u'MONASTERO / CONVENTO'),
        (u'27', u'BENI_PRIVATI', u'BENI PRIVATI'),
    )

    CATEGORIA_IMMOBILE = Choices(
        (u'1', u'BENI_DEMANIALI', u'Beni Demaniali e Beni ecclesiastici di prop. Pubbl.'),
        (u'2', u'COMUNI_PROVINCE', u'Comuni e Province'),
        (u'3', u'ENTI_RELIGIOSI', u'Enti religiosi'),
        (u'4', u'MONASTERI_CONVENTI', u'Monasteri, Conventi ed ex'),
        (u'5', u'OPERE_BONIFICA', u'Opere di bonifica ed irrigazione'),
        (u'6', u'STRUTTURE_SANITARIE', u'Strutture Sanitarie'),
        (u'7', u'STRUTTURE_SCOLASTICHE', u'Strutture Scolastiche ed Universita'),
    )

    STATO = Choices(
        (u'piano', u'PIANO', u'A piano'),
        (u'attuazione', u'ATTUAZIONE', u'Attuazione'),
    )

    STATO_ATTUAZIONE = Choices(
        (u'progettazione', u'PROGETTAZIONE', u'Progettazione'),
        (u'in_corso', u'IN_CORSO', u'In corso'),
        (u'concluso', u'CONCLUSO', u'Concluso'),
    )

    programma = models.ForeignKey('Programma', null=False, blank=False, default=0)
    # id fenice = id_interv_a_progr
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, unique=True)
    soggetto_attuatore = models.ForeignKey('SoggettoAttuatore', null=True, blank=False, default=None)
    # id_propr_imm = id fenice per l'immobile
    id_propr_imm = models.PositiveSmallIntegerField(null=False, blank=False)
    n_ordine = models.CharField(max_length=20, null=False, blank=False)
    importo_generale = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    importo_a_programma = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    territorio = models.ForeignKey('territori.Territorio', null=True)
    vari_territori = models.BooleanField(default=False, null=False, blank=False)
    tipo_immobile_fenice = models.CharField(max_length=2, choices=TIPO_IMMOBILE_FENICE, blank=False, null=False,
                                            default='')
    tipo_immobile = models.ForeignKey('TipoImmobile', null=True, )
    categ_immobile = models.CharField(max_length=2, choices=CATEGORIA_IMMOBILE, blank=True, null=True, default='')
    slug = models.SlugField(max_length=60, blank=False, null=False, unique=True)

    stato = models.CharField(max_length=11, choices=STATO, blank=True, null=True, default='')
    stato_attuazione = models.CharField(max_length=13, choices=STATO_ATTUAZIONE, blank=True, null=True, default='')

    objects = ProgrammatiManager()
    programmati = ProgrammatiManager()
    pianificati = PianificatiManager()
    attuazione = AttuazioneManager()
    progettazione = ProgettazioneManager()
    in_corso = InCorsoManager()
    conclusi = ConclusiManager()


    @staticmethod
    def get_sogg_attuatore_aggregates(**kwargs):
        data = []

        for tipologia_id, tipologia_shortname in SoggettoAttuatore.TIPOLOGIA:
            tipologia_name = SoggettoAttuatore.TIPOLOGIA.__getitem__(tipologia_id)
            # count and sum for programmazione
            d = {'name': tipologia_name,
                 'attuazione': InterventoProgramma.programmati.filter(soggetto_attuatore__tipologia=tipologia_id,
                                                                     **kwargs).with_count(),
                }

            if d['attuazione']['count'] == 0:
                continue
            data.append(d)
        return data

    @staticmethod
    def get_tipo_immobile_aggregates(**kwargs):
        data = []

        for tipo_imm in TipoImmobile.objects.all().order_by('slug'):
            d = {
                'name': tipo_imm.denominazione,
                'slug': tipo_imm.slug,
                'programmazione': InterventoProgramma.programmati.filter(tipo_immobile__tipologia=tipo_imm.tipologia,
                                                                         **kwargs).with_count(),
                'pianificazione': InterventoProgramma.pianificati.filter(tipo_immobile__tipologia=tipo_imm.tipologia,
                                                                         **kwargs).with_count(),
                'attuazione': InterventoProgramma.attuazione.filter(tipo_immobile__tipologia=tipo_imm.tipologia,
                                                                    **kwargs).with_count(),
            }
            data.append(d)

        return data

    def __unicode__(self):
        return u"{} - {}".format(self.denominazione, self.territorio)

    class Meta:
        verbose_name_plural = u'Interventi a programma'


class TipoImmobile(models.Model):
    TIPOLOGIA = Choices(
        (u'1', u'ALTRO', u'Altro'),
        (u'2', u'INFRASTRUTTURE_BONIFICHE', u'Infrastrutture e bonifiche'),
        (u'3', u'OSPEDALI', u'Ospedali'),
        (u'4', u'CIMITERI', u'Cimiteri'),
        (u'5', u'EDIFICI_STORICI', u'Edifici storici e culturali'),
        (u'6', u'IMPIANTI_SPORTIVI', u'Impianti sportivi e ricreativi'),
        (u'7', u'CHIESE', u'Chiese e beni religiosi'),
        (u'8', u'SCUOLE', u'Scuole e Università'),
        (u'9', u'EDIFICI_PUBBLICI', u'Edifici pubblici'),
    )
    tipologia = models.CharField(max_length=3, choices=TIPOLOGIA, blank=False, null=False, default=u'')
    slug = models.SlugField(max_length=50, blank=False, null=False, default='')
    denominazione = models.TextField(max_length=120, blank=True, null=True, default=u'')
    descrizione = models.TextField(max_length=800, blank=True, null=True, default=None)

    @staticmethod
    def get_tipologie():
        return list(TipoImmobile.objects.all().values('denominazione', 'slug'))

    def __unicode__(self):
        return u"{} ({})".format(TipoImmobile.TIPOLOGIA[self.tipologia], self.slug, )

    class Meta:
        verbose_name_plural = u'Tipo Immobile'


class Programma(models.Model):
    denominazione = models.TextField(max_length=120)
    id_fenice = models.PositiveSmallIntegerField(null=True, blank=True, unique=True)

    def __unicode__(self):
        return u"{}({})".format(self.denominazione, self.id_fenice, )

    class Meta:
        verbose_name_plural = u'Programmi'


class Cofinanziamento(models.Model):
    TIPO_COFINANZIAMENTO = Choices(
        (u'1', u'ASSICURAZIONE', u'Assicurazione'),
        (u'2', u'DONAZIONI', u'Donazioni'),
        (u'3', u'OPERE_PROVVISIONALI', u'Opere provvisionali'),
        (u'4', u'MESSA_IN_SICUREZZA', u'Messa in sicurezza'),
        (u'5', u'FONDI_PROPRI', u'Fondi propri'),
        (u'6', u'EDILIZIA_SCOLASTICA', u'Edilizia scolastica'),
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
        (u'1', u'OPERE_PUBBLICHE', u'Piano opere pubbliche'),
        (u'2', u'BENI_CULTURALI', u'Piano beni culturali'),
        (u'3', u'EDILIZIA_SCOLASTICA', u'Piano edilizia scolastica ed universita'),
        (u'4', u'MISTI', u'Piano UMI - misti'),
    )
    # id fenice x il piano
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, default=0, unique=True)
    tipologia = models.CharField(max_length=2, choices=TIPO_PIANO, blank=False, null=False, default='')
    programma = models.ForeignKey('Programma', null=False, blank=False)
    denominazione = models.TextField(max_length=120, default=u'')

    def __unicode__(self):
        return u"({}) {}".format(self.id_fenice, self.TIPO_PIANO[self.tipologia])

    class Meta:
        verbose_name_plural = u'Piani'


class InterventoPiano(models.Model):
    intervento_programma = models.ForeignKey('InterventoProgramma', null=False, blank=False)
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, unique=True)
    imp_a_piano = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    piano = models.ForeignKey('Piano', null=True, blank=True, default=None)

    def __unicode__(self):
        return u"{},{},{},{}".format(self.piano, self.intervento_programma.pk, self.id_fenice,
                                     self.imp_a_piano)

    class Meta:
        verbose_name_plural = u'Interventi a piano'


class Intervento(models.Model):
    TIPO_INTERVENTO = Choices(
        (u'1', u'RIPARAZIONE_RAFFORZAMENTO', u'Riparazione con rafforzamento locale'),
        (u'2', u'RIPRISTINO', u'Ripristino con miglioramento sismico'),
        (u'3', u'DEMOLIZIONE', u'Demolizione e ricostruzione e/o nuova costruzione'),
        (u'4', u'NON_STRUTTURALE', u'Intervento non strutturale'),
    )

    STATO_INTERVENTO = Choices(
        (u'1', u'A_PIANO', u'A piano'),
        (u'2', u'BOZZA', u'In bozza'),
        (u'3', u'PRESENTATO', u'Presentato'),
        (u'4', u'AMMESSO', u'Ammesso'),
        (u'5', u'RESPINTO', u'Respinto'),
        (u'6', u'FONDI_ASSEGNATI', u'Fondi assegnati'),
        (u'7', u'RINUNCIATO', u'Rinunciato'),
        (u'8', u'2_ACCONTO', u'2 acconto'),
        (u'9', u'3_ACCONTO', u'3 acconto'),
        (u'10', u'SALDO', u'Saldo'),
        (u'11', u'CHIUSO', u'Chiuso'),
        (u'12', u'SOSTITUITO', u'Sostituito da variante'),
    )

    intervento_piano = models.ForeignKey('InterventoPiano', null=False, blank=False)
    # id fenice per l'intervento
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, unique=True)
    is_variante = models.BooleanField(null=False, blank=False, default=False)
    imp_congr_spesa = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    denominazione = models.TextField(max_length=400)
    tipologia = models.CharField(max_length=2, choices=TIPO_INTERVENTO, null=False, blank=False, default='')
    stato = models.CharField(max_length=3, choices=STATO_INTERVENTO, null=False, blank=False, default='')
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
    imprese = models.ManyToManyField(Impresa)

    class Meta:
        verbose_name_plural = u'Interventi'

    def __unicode__(self):
        return u"{},{},{}".format(self.intervento_piano_id, self.denominazione, self.stato)


class Liquidazione(models.Model):
    TIPO_LIQUIDAZIONE = Choices(
        (u'1000', u'PRIMO_ACCONTO', u'Primo acconto'),
        (u'1100', u'BOZZA', u'In bozza'),
        (u'1110', u'PRESENTATO', u'Presentato'),
        (u'1111', u'AMMESSO', u'Ammesso'),
        (u'0100', u'RESPINTO', u'Respinto'),
        (u'0010', u'FONDI_ASSEGNATI', u'Fondi assegnati'),
        (u'0001', u'RINUNCIATO', u'Rinunciato'),
        (u'0110', u'2_ACCONTO', u'2 acconto'),
        (u'0111', u'3_ACCONTO', u'3 acconto'),
        (u'0011', u'SALDO', u'Saldo'),
    )

    intervento = models.ForeignKey(u'Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=5, choices=TIPO_LIQUIDAZIONE, null=False, blank=False, default='')
    data = models.DateField(blank=False, null=False)
    importo = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)

    class Meta:
        verbose_name_plural = u'Liquidazioni'

    def __unicode__(self):
        return u"{},{} {}E".format(self.intervento_id, self.data, self.importo)


class EventoContrattuale(models.Model):
    TIPO_EVENTO = Choices(
        (u'1', u'STIPULA_CONTRATTO', u'Stipula contratto'),
        (u'2', u'INIZIO_LAVORI', u'Inizio lavori'),
        (u'3', u'FINE_LAVORI', u'Fine lavori come da Capitolato'),
        (u'4', u'VERBALE_CONSEGNA', u'Verbale di consegna lavori'),
    )
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    tipologia = models.CharField(max_length=2, choices=TIPO_EVENTO, null=False, blank=False, default='')
    data = models.DateField(blank=False, null=False)

    class Meta:
        verbose_name_plural = u'Eventi contrattuali'

    def __unicode__(self):
        return u"{},{},{}".format(self.intervento_id, self.TIPO_EVENTO[self.tipologia], self.data)


class QuadroEconomico(models.Model):
    TIPO_QUADRO_ECONOMICO = Choices(
        (u'1', u'SPESA_COMPLESSIVA', u'Quadro sommario della spesa complessiva'),
        (u'2', u'COFINANZIAMENTO_RIMBORSO', u'Quadro sommario del cofinanziamento da Rimborso assicurativo'),
        (u'3', u'COFINANZIAMENTO_DONAZIONI', u'Quadro sommario del cofinanziamento da Donazioni'),
        (u'4', u'COFINANZIAMENTO_OPERE', u'Quadro sommario del cofinanziamento da Opere provvisionali'),
        (u'5', u'COFINANZIAMENTO_MESSE_SICUREZZA', u'Quadro sommario del cofinanziamento da Messe in sicurezza'),
        (u'6', u'COFINANZIAMENTO_EDIFICI_SCOLASTICI',
         u'Quadro sommario del cofinanziamento da Ricostruzione edifici scolastici'),
        (u'7', u'COFINANZIAMENTO_FONDI_PROPRI', u'Quadro sommario del cofinanziamento da Fondi propri (e altro)'),
        (u'8', u'SOMMARIO_GENERALE', u'Quadro sommario generale riepilogativo'),
        (u'9', u'QTE_COMMISSARIO', u'Q.T.E. relativo al finanziamento del Commissario'),
        (u'10', u'QTE_ASSICURATIVO', u'Q.T.E. riferito al cofinanziamento da Rimborso assicurativo'),
        (u'11', u'QTE_DONAZIONI', u'Q.T.E. riferito al cofinanziamento da Donazioni'),
        (u'12', u'QTE_OPERE', u'Q.T.E. riferito al cofinanziamento da Opere provvisionali'),
        (u'13', u'QTE_MESSE_SICUREZZA', u'Q.T.E. riferito al cofinanziamento da Messe in sicurezza'),
        (u'14', u'QTE_EDIFICI_SCOLASTICI', u'Q.T.E. riferito al cofinanziamento da Ricostruzione edifici scolastici'),
        (u'15', u'QTE_FONDI_PROPRI', u'Q.T.E. riferito al cofinanziamento da Fondi propri (e altro)'),
        (u'16', u'QTE_GENERALE', u'Q.T.E. generale riepilogativo'),
        (u'17', u'QTE_RIMODULATO_COMMISSARIO', u'Q.T.E. rimodulato relativo al finanziamento del Commissario'),
        (u'18', u'QTE_FINANZIAMENTO_COMMISSARIO', u'Q.T.E. relativo al finanziamento assegnato dal Commissario'),
        (u'19', u'QTE_VARIANTE_SENZA_MODIFICA', u'Q.T.E. di variante senza modifica dei lavori'),
        (u'20', u'QTE_VARIANTE_CON_MODIFICA', u'Q.T.E. di variante con modifica dei lavori'),
        (u'21', u'QTE_FINALE', u'Q.T.E. finale'),
    )
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, default=0, unique=True)
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
        (u'1', u'PROGETTO_PRELIMINARE', u'Progetto preliminare'),
        (u'2', u'PROGETTO_DEFINITIVO', u'Progetto definitivo'),
        (u'3', u'PROGETTO_ESECUTIVO', u'Progetto esecutivo'),
        (u'4', u'PERIZIA_SISMICA', u'Perizia sismica'),
        (u'5', u'PERIZIA_DEMOLIZIONE_RIPRISTINO', u'Perizia demolizione con progetto di ripristino'),
        (u'6', u'PERIZIA_DEMOLIZIONE_CONVENZIONALE', u'Perizia demolizione con calcolo convenzionale'),
        (u'7', u'CALCOLO_CONVENZIONALE', u'Calcolo convenzionale'),
        (u'8', u'VARIANTE', u'Variante con modifica dei lavori'),
    )

    STATO_PROGETTO = Choices(
        (u'1', u'BOZZA', u'In bozza'),
        (u'2', u'PRESENTATO', u'Presentato'),
        (u'3', u'PRESO_IN_CARICO', u'Preso in carico'),
        (u'4', u'ISTRUTTORIA', u'In istruttoria'),
        (u'5', u'RESPINTO', u'Respinto'),
        (u'6', u'AMMESSO', u'Ammesso'),
    )
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, default=0, unique=True)
    intervento = models.ForeignKey('Intervento', null=True, blank=True, default=None)
    tipologia = models.CharField(max_length=2, choices=TIPO_PROGETTO, blank=False, null=False, default='')
    stato = models.CharField(max_length=2, choices=STATO_PROGETTO, blank=False, null=False, default='')
    data_deposito = models.DateField(blank=True, null=True)
    data_inizio = models.DateField(blank=True, null=True)
    data_fine = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u"{} - {}".format(self.intervento.intervento_piano.intervento_programma.denominazione, self.tipologia)

    class Meta:
        verbose_name_plural = u'Progetti'


class Variante(models.Model):
    TIPO_VARIANTE = Choices(
        (u'1', u'SENZA_MODIFICA', u'Variante senza modifica dei lavori'),
        (u'2', u'CON_MODIFICA', u'Variante con modifica dei lavori'),
    )

    STATO_VARIANTE = Choices(
        (u'1', u'PRESENTATA', u'Presentata'),
        (u'2', u'PRESA_IN_CARICO', u'Presa in carico'),
        (u'3', u'AMMESSA', u'Ammessa'),
        (u'4', u'RESPINTA', u'Respinta'),
    )
    qe = models.ForeignKey('QuadroEconomicoIntervento', blank=True, null=True )
    tipologia = models.CharField(max_length=2, choices=TIPO_VARIANTE, blank=False, null=False, default='')
    stato = models.CharField(max_length=2, choices=STATO_VARIANTE, blank=False, null=False, default='')
    progetto = models.ForeignKey('Progetto', null=True, blank=True)
    intervento = models.ForeignKey('Intervento', null=False, blank=False)
    data_deposito = models.DateField(blank=True, null=True)
    data_fine = models.DateField(blank=True, null=True)

    objects = VariantiManager()

    def __unicode__(self):
        return u"{} - {}".format(self.progetto, self.tipologia)

    class Meta:
        verbose_name_plural = u'Varianti'


##
# Donazioni
##


class Donazione(models.Model):
    TIPO_DONAZIONE = Choices(
        (u'1', u'Diretta', u'Diretta'),
        (u'2', u'Regione', u'Regione'),
    )

    TIPO_CEDENTE = Choices(
        (u'0', u'ALTRO', u'ALTRO'),
        (u'1', u'ASSOCIAZIONI', u'ASSOCIAZIONI'),
        (u'2', u'ENTI_PUBBLICI', u'ENTI PUBBLICI'),
        (u'3', u'COMUNI', u'COMUNI'),
        (u'4', u'CITTADINI', u'CITTADINI'),
        (u'5', u'AZIENDE', u'AZIENDE'),
        (u'6', u'REGIONI', u'REGIONI'),
        (u'7', u'PROVINCE', u'PROVINCE'),
    )

    territorio = models.ForeignKey('territori.Territorio')
    denominazione = models.CharField(max_length=256)
    informazioni = models.TextField(max_length=800, blank=True, null=True, default=None)
    tipologia_cedente = models.CharField(max_length=2, choices=TIPO_CEDENTE, blank=False, null=False, default='')
    tipologia_donazione = models.CharField(max_length=2, choices=TIPO_DONAZIONE, blank=False, null=False, default='')
    data = models.DateField(null=True, blank=True)
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, blank=False, null=False, )
    interventi_programma = models.ManyToManyField(InterventoProgramma, through='DonazioneInterventoProgramma')

    @staticmethod
    def get_aggregates(tipologia=None, **kwargs):

        if not tipologia:
            aggregation_struct = {
                'sum': Sum('importo'),
                'count': Count('importo')
            }
        else:
            tipologia_id, tipologia_shortname = tipologia
            aggregation_struct = {
                'sum': Sum('importo', only=Q(tipologia_cedente=tipologia_id)),
                'count': Count('importo', only=Q(tipologia_cedente=tipologia_id))
            }

        return Donazione.objects.filter(**kwargs).aggregate(**aggregation_struct)

    def __unicode__(self):
        return u"{} - {}".format(self.denominazione, self.territorio)

    #    ritorna l'importo lavori in formato italiano
    def get_importo_ita(self):
        return moneyfmt(self.importo, 2, "", ".", ",")

    class Meta:
        verbose_name_plural = u'Donazioni'


class DonazioneInterventoProgramma(models.Model):
    donazione = models.ForeignKey('Donazione', blank=False, null=False)
    intervento_programma = models.ForeignKey('InterventoProgramma', blank=False, null=False)


    @staticmethod
    def get_aggregates(tipologia=None, **kwargs):

        importo_field = 'donazione__importo'
        if not tipologia:
            aggregation_struct = {
                'sum': Sum(importo_field),
                'count': Count(importo_field)
            }
        else:
            tipologia_id, tipologia_shortname = tipologia
            aggregation_struct = {
                'sum': Sum(importo_field, only=Q(donazione__tipologia_cedente=tipologia_id)),
                'count': Count(importo_field, only=Q(donazione__tipologia_cedente=tipologia_id))
            }

        return DonazioneInterventoProgramma.objects.filter(**kwargs).aggregate(**aggregation_struct)

    class Meta:
        verbose_name_plural = u'Donazioni a Interventi a programma'

    def __unicode__(self):
        return u"{} - {}: {}E".format(self.donazione, self.intervento_programma, self.donazione.importo)


##
# ANAGRAFICHE
##

class Anagrafica(models.Model):
    id_fenice = models.PositiveSmallIntegerField(null=False, blank=False, unique=True)

    class Meta:
        abstract = True


class SoggettoAttuatore(Anagrafica):
    TIPOLOGIA = Choices(
        (u'1', u'ALTRO', u'Altro'),
        (u'2', u'AZIENDE', u'Aziende'),
        (u'3', u'CHIESA', u'Chiesa'),
        (u'4', u'COMMISSARIO_DELEGATO', u'Commissario delegato'),
        (u'5', u'COMUNE', u'Comune'),
        (u'6', u'CONSORZIO_BONIFICA', u'Consorzio di Bonifica'),
        (u'7', u'ENTI_AGENZIE', u'Enti e Agenzie'),
        (u'8', u'FONDAZIONI', u'Fondazioni'),
        (u'9', u'MINISTERI', u'Ministeri'),
        (u'10', u'PRIVATI', u'Privati'),
        (u'11', u'PROVINCE', u'Province'),
        (u'12', u'PROV_INTERREGIONALE', u'Provveditorato Interregionale OO.PP'),
        (u'13', u'REGIONE', u'Regione'),
        (u'14', u'STRUTTURE_SS', u'Strutture socio-sanitarie'),
        (u'15', u'UNIVERSITA', u'Università'),
    )

    tipologia = models.CharField(max_length=3, choices=TIPOLOGIA, blank=False, null=False, default=u'')
    denominazione = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, blank=False, null=False, unique=True)
    descrizione = models.TextField(max_length=800, blank=True, null=True, default=None)

    @staticmethod
    def get_tipologie():
        return list(SoggettoAttuatore.TIPOLOGIA._triples)

    class Meta:
        verbose_name_plural = u'Soggetti attuatori'

    def __unicode__(self):
        return u"({}) {}".format(self.id_fenice, self.denominazione)


class ProprietarioImmobile(Anagrafica):
    denominazione = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = u'Proprietari immobile'


    def __unicode__(self):
        return u"({}) {}".format(self.id_fenice, self.denominazione)


class RUP(Anagrafica):
    nome = models.CharField(max_length=256)
    cognome = models.CharField(max_length=256)
    cf = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = u'RUP'

    def __unicode__(self):
        return u"({}) {} {} [{}]".format(self.id_fenice, self.nome, self.cognome, self.cf)


##
# Ultimo aggiornamento keeps track of when the data was updated
##

class UltimoAggiornamento(models.Model):
    TIPOLOGIA = Choices(
        (u'1', u'INTERVENTI', u'Interventi'),
        (u'2', u'DONAZIONI', u'Donazioni'),
    )
    data = models.DateField(null=False, blank=False, auto_now=True)
    tipologia = models.CharField(max_length=2, choices=TIPOLOGIA, blank=False, null=False, default=u'')

    class Meta:
        verbose_name_plural = u'Ultimo Aggiornamento'

    def __unicode__(self):
        return u"({}) {}".format(self.TIPOLOGIA[self.tipologia], self.data)

