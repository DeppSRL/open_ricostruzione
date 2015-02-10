# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand, CommandError
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
import xlrd
from open_ricostruzione.models import Donazione, InterventoAProgramma
from territori.models import Territorio
from optparse import make_option
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Import progetti data from JSON file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    default=False,
                    help='Delete Existing Records'),

    )

    input_file = ''
    delete = ''
    encoding = 'latin-1'
    logger = logging.getLogger('csvimport')
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
        not_found_istat=[]
        # read file
        try:
            json_file = open(self.input_file)
            data = json.load(json_file, encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)

        if self.delete:
            self.logger.info("Deleting all previous records...")
            InterventoAProgramma.objects.all().delete()
            self.logger.info("Done")

        for intervento_a_programma in data['interventi_a_programma']:
            istat_comune = intervento_a_programma['comune']['cod_istat_com']
            try:
                territorio = Territorio.objects.get(istat_id=istat_comune)
            except ObjectDoesNotExist:
                self.logger.error("Territorio does not exist:{}".format(istat_comune))
                if istat_comune not in not_found_istat:
                    not_found_istat.append(istat_comune)
                continue
            else:
                self.logger.debug(u"Territorio found:{}".format(territorio.denominazione))

                got_gps_data = False
                if territorio.gps_lon is None:
                    territorio.gps_lon = intervento_a_programma['comune']['long']
                    got_gps_data = True

                if territorio.gps_lat is None:
                    territorio.gps_lat = intervento_a_programma['comune']['lat']
                    got_gps_data = True

                if got_gps_data:
                    territorio.save()

                iap = InterventoAProgramma()
                iap.denominazione = intervento_a_programma['denominazione']
                iap.save()