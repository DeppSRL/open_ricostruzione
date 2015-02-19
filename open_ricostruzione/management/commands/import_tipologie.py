import json
import logging
from optparse import make_option
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Import tipologie and anagrafica from JSON file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    default=True,
                    help='Delete Existing Records'),

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
        self.delete = options['delete']
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

        if self.delete:
            self.logger.info("Deleting all previous records...")
            # InterventoProgramma.objects.all().delete()
            self.logger.info("Done")
