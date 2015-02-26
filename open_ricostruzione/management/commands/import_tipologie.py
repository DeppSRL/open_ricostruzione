import json
import logging
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from open_ricostruzione.models import Programma, Piano, RUP, ProprietarioImmobile, SoggettoAttuatore, \
    InterventoProgramma, Progetto, Intervento, Cofinanziamento, EventoContrattuale, Liquidazione, QuadroEconomico


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

    def check_tipologia(self, t):
        n_tipi_piano_json = len(self.codifiche[t[0]])
        n_tipi_piano_model = len(t[1])
        if n_tipi_piano_json != n_tipi_piano_model:
            self.logger.error("Found {} '{}' in Json file, {} '{}' present in DB Model".format(
                n_tipi_piano_json, t[0], n_tipi_piano_model, t[0],
            ))
            exit()

    def check_tipologie(self):
        tipologie_map=(
            # note: categorie_immobile is optional
            ('categorie_immobile', InterventoProgramma.CATEGORIA_IMMOBILE ),
            ('stati_intervento', Intervento.STATO_INTERVENTO),
            ('stati_progetto', Progetto.STATO_PROGETTO),
            ('tipi_cofinanziamento', Cofinanziamento.TIPO_COFINANZIAMENTO),
            ('tipi_evento_contrattuale', EventoContrattuale.TIPO_EVENTO),
            ('tipi_intervento', Intervento.TIPO_INTERVENTO),
            ('tipi_immobile', InterventoProgramma.TIPO_IMMOBILE),
            ('tipi_liquidazione', Liquidazione.TIPO_LIQUIDAZIONE),
            ('tipi_piano', Piano.TIPO_PIANO),
            ('tipi_progetto', Progetto.TIPO_PROGETTO),
            ('tipi_qe', QuadroEconomico.TIPO_QUADRO_ECONOMICO),
        )

        for t in tipologie_map:
            self.check_tipologia(t)

    def import_piani(self):
        for piano_json in self.codifiche['piani']:
            programma_piano = None
            try:
                programma_piano = Programma.objects.get(id_progr=piano_json['id_progr'])
            except ObjectDoesNotExist:
                self.logger.error("Programma not found for Piano with id:{}".format(piano_json['id']))
                exit()

            Piano.objects.update_or_create(
                id_piano=piano_json['id'],
                programma=programma_piano,
                tipologia=piano_json['id_tipo_piano'],
                defaults={
                    'denominazione': piano_json['nome']
                }
            )

    def import_programmi(self):
        for programma_json in self.codifiche['programmi']:
            Programma.objects.update_or_create(
                id_progr=programma_json['id'],
                defaults={
                    'denominazione': programma_json['nome']
                }
            )

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

        self.codifiche = data['codifiche']
        self.anagrafiche = data['anagrafiche']

        # Check tipologie
        self.logger.info("Checking tipologie...")
        self.check_tipologie()
        self.logger.info("Tipologie OK")

        ##
        # Import PROGRAMMI
        ##
        self.logger.info("Import programmi...")
        self.import_programmi()
        self.logger.info("Programmi imported")

        ##
        # Import PIANI
        ##
        self.logger.info("Import piani...")
        self.import_piani()
        self.logger.info("Piani imported")

        ##
        # Import ANAGRAFICHE
        ##

        self.logger.info("Import Anagrafiche: proprietari immobile, sogg.attuatori, rup...")
        for p_immobile_json in self.anagrafiche['proprietari_immobile']:
            ProprietarioImmobile.objects.update_or_create(
                id_fenice=p_immobile_json['id'],
                denominazione=p_immobile_json['nome'],
            )

        for s_attuatori_json in self.anagrafiche['soggetti_attuatori']:
            SoggettoAttuatore.objects.update_or_create(
                id_fenice=s_attuatori_json['id'],
                denominazione=s_attuatori_json['nome'],
            )

        for rup_json in self.anagrafiche['rup']:
            RUP.objects.update_or_create(
                id_fenice=rup_json['id'],
                nome=rup_json['nome'],
                cognome=rup_json['cognome'],
                cf=rup_json['cf'],
            )

        self.logger.info("Done")
