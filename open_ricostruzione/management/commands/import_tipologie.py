import json
import logging
from optparse import make_option
from django.core.management import BaseCommand
from open_ricostruzione.models import Programma, Piano, RUP, ProprietarioImmobile, SoggettoAttuatore


class Command(BaseCommand):
    help = 'Import tipologie and anagrafica from JSON file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
    )

    input_file = None
    delete = False
    encoding = 'latin-1'
    logger = logging.getLogger('csvimport')
    date_format = '%d/%M/%Y'
    unicode_reader = None

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

        codifiche = data['codifiche']
        ##
        # Import PROGRAMMI
        ##

        for programma_json in codifiche['programmi']:
            Programma.objects.update_or_create(
                id_progr=programma_json['id'], defaults={'denominazione': programma_json['nome']})


        # Check tipo piano
        n_tipi_piano_json = len(codifiche['tipi_piano'])
        n_tipi_piano_model = len(Piano.TIPO_PIANO)
        if n_tipi_piano_json != n_tipi_piano_model:
            self.logger.error("Found {} tipi piano in Json file, {} tipi piano present in DB Model".format(
                n_tipi_piano_json, n_tipi_piano_model
            ))
            exit()

        self.logger.info("Done")
