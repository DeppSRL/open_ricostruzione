import json
import logging
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from open_ricostruzione.models import TipoImmobile

# TO BE USED THEN TIPO IMMOBILE WILL HAVE A TEXT DESCRIPTION


class Command(BaseCommand):
    help = 'Import tipo immobile from json file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
    )

    input_file = None
    logger = logging.getLogger('csvimport')
    encoding = 'latin-1'

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


        self.logger.info("Done")