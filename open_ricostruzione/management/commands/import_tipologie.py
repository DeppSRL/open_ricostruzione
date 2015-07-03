import csv
import json
import logging
from optparse import make_option
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.db import IntegrityError
from django.utils.text import slugify
from open_ricostruzione.models import Programma, Piano, RUP, ProprietarioImmobile, SoggettoAttuatore, \
    InterventoProgramma, Progetto, Intervento, Cofinanziamento, EventoContrattuale, Liquidazione, QuadroEconomico, Variante


class Command(BaseCommand):
    help = 'Import tipologie and anagrafica from JSON file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
    )

    input_file = None
    encoding = 'latin-1'
    logger = logging.getLogger('csvimport')
    codifiche = None
    anagrafiche = None
    sogg_att_map = {}

    def check_tipologia(self, t):
        ##
        # controlla che il numero di elementi presenti in una tipologia T sia uguale
        # al n. di tuple nell'oggetto Choice presente nel modello.
        # Se non e' cosi: logga errore e stoppa lo script
        ##
        check_passed = True
        if t[0] is not 'tipi_liquidazione':
            codifiche_file = set(unicode(d['id']) for d in self.codifiche[t[0]])
        else:
            codifiche_file = set(unicode(d) for d in self.codifiche[t[0]].keys())

        codifiche_db = set(t[1]._db_values)
        n_tipi_piano_json = len(codifiche_file)
        n_tipi_piano_model = len(t[1])
        # gets data file ids and compares them with ids in the db
        diff_file = set(codifiche_db)-set(codifiche_file)
        diff_db = set(codifiche_file)-set(codifiche_db)
        if len(diff_file):
            diff_file_str = ",".join(str(e) for e in diff_file)
            self.logger.error("{} Id:{} in DB SETTINGS but not in FILE".format(t[0].upper(),diff_file_str))
            check_passed = False
        if len(diff_db):
            diff_db_str = ",".join(str(e) for e in diff_db)
            self.logger.error("{} Id:{} in FILE but not in DB SETTINGS ".format(t[0].upper(), diff_db_str))
            check_passed = False
        if n_tipi_piano_json != n_tipi_piano_model:
            self.logger.error("Found {} '{}' in Json file, {} '{}' present in DB Model".format(
                n_tipi_piano_json, t[0], n_tipi_piano_model, t[0],
            ))
            check_passed = False
        return check_passed

    def check_tipologie(self):
        tipologie_map = (
            # note: categorie_immobile is optional
            ('categorie_immobile', InterventoProgramma.CATEGORIA_IMMOBILE ),
            ('stati_intervento', Intervento.STATO_INTERVENTO),
            ('stati_progetto', Progetto.STATO_PROGETTO),
            ('tipi_cofinanziamento', Cofinanziamento.TIPO_COFINANZIAMENTO),
            ('tipi_evento_contrattuale', EventoContrattuale.TIPO_EVENTO),
            ('tipi_intervento', Intervento.TIPO_INTERVENTO),
            ('tipi_immobile', InterventoProgramma.TIPO_IMMOBILE_FENICE),
            ('tipi_liquidazione', Liquidazione.TIPO_LIQUIDAZIONE),
            ('tipi_piano', Piano.TIPO_PIANO),
            ('tipi_progetto', Progetto.TIPO_PROGETTO),
            ('tipi_qe', QuadroEconomico.TIPO_QUADRO_ECONOMICO),
            # varianti
            ('tipi_variante', Variante.TIPO_VARIANTE),
            ('stati_variante', Variante.STATO_VARIANTE),
        )

        stop_import = False
        for t in tipologie_map:

            if not self.check_tipologia(t):
                stop_import = True

        if stop_import:
            self.logger.critical("Stopping import because tipologie check failed")
            exit()

    def import_piani(self):
        for piano_json in self.codifiche['piani']:
            programma_piano = None
            try:
                programma_piano = Programma.objects.get(id_fenice=piano_json['id_progr'])
            except ObjectDoesNotExist:
                self.logger.error("Programma not found for Piano with id:{}".format(piano_json['id']))
                exit()

            Piano.objects.update_or_create(
                id_fenice=piano_json['id'],
                programma=programma_piano,
                tipologia=piano_json['id_tipo_piano'],
                defaults={
                    'denominazione': piano_json['nome']
                }
            )

    def import_programmi(self):
        for programma_json in self.codifiche['programmi']:
            Programma.objects.update_or_create(
                id_fenice=programma_json['id'],
                defaults={
                    'denominazione': programma_json['nome']
                }
            )

    def load_sogg_attuatore_mapping(self):
        ##
        # creates a dict in self.sogg_att_map with keys: id_fenice for sogg.att
        # and as value the corresponding ORIC categorization id
        ##

        with open(settings.SOGG_ATTUATORE_MAP_FILE_PATH, mode='r') as infile:
            reader = csv.reader(infile, dialect='excel-tab')
            next(reader, None)  # skip the headers
            for row in reader:
                self.sogg_att_map[int(row[0])] = row[3]


    def handle(self, *args, **options):

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        self.input_file = options['file']
        self.logger.info('Input file:{}'.format(self.input_file))
        data = None
        not_found_istat = []
        # read file
        try:
            json_file = open(self.input_file)
            data = json.load(json_file, encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)

        # delete old data
        SoggettoAttuatore.objects.all().delete()
        RUP.objects.all().delete()
        ProprietarioImmobile.objects.all().delete()

        self.codifiche = data['codifiche']
        self.anagrafiche = data['anagrafiche']

        # load sogg.attuatore mapping from csv file in memory
        self.load_sogg_attuatore_mapping()

        # Check tipologie
        self.logger.info("Checking tipologie...")
        self.check_tipologie()
        self.logger.info("Tipologie OK")

        # Import PROGRAMMI
        self.logger.info("Import programmi...")
        self.import_programmi()
        self.logger.info("Programmi imported")

        # Import PIANI
        self.logger.info("Import piani...")
        self.import_piani()
        self.logger.info("Piani imported")

        # Import ANAGRAFICHE
        self.logger.info("Import proprietari immobile")
        for p_immobile_json in self.anagrafiche['proprietari_immobile']:
            ProprietarioImmobile.objects.update_or_create(
                id_fenice=p_immobile_json['id'],
                denominazione=p_immobile_json['nome'],
            )

        self.logger.info("Import sogg.attuatori")

        for s_attuatori_json in self.anagrafiche['soggetti_attuatori']:

            tipologia = self.sogg_att_map.get(s_attuatori_json['id'], u'')
            sa_slug = slugify(s_attuatori_json['nome'])
            sa_slug_alternative = u"{}_2".format(sa_slug)
            if tipologia == u'':
                self.logger.error(u"Soggetto attuatore: cannot find tipologia ORIC for id_fenice:'{}', denominazione:'{}'".
                    format(s_attuatori_json['id'], s_attuatori_json['nome'],))
            try:

                SoggettoAttuatore.objects.update_or_create(
                    id_fenice=s_attuatori_json['id'],
                    denominazione=s_attuatori_json['nome'],
                    tipologia=tipologia,
                    defaults={
                        'slug': sa_slug
                    }
                )
            except IntegrityError:
                self.logger.warning(
                    "This slug:{} was already present in DB, try saving object with slug:{}".format(sa_slug,
                                                                                                    sa_slug_alternative))
                SoggettoAttuatore.objects.update_or_create(
                    id_fenice=s_attuatori_json['id'],
                    denominazione=s_attuatori_json['nome'],
                    tipologia=tipologia,
                    defaults={
                        'slug': sa_slug_alternative
                    }
                )

        self.logger.info("Import RUP")
        for rup_json in self.anagrafiche['rup']:
            try:
                RUP.objects.update_or_create(
                    id_fenice=rup_json['id'],
                    cf=rup_json['cf'],
                    defaults={
                        'nome':rup_json['nome'],
                        'cognome':rup_json['cognome'],
                        }
                )
            except IntegrityError:
                self.logger.error("Could not import RUP with CF:'{}', id_fenice:'{}', integrity error.".format(rup_json['cf'], rup_json['id']))

        self.logger.info("Done")