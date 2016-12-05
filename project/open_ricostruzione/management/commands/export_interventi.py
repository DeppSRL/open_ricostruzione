# -*- coding: utf-8 -*-
import csv
import logging
from django.core.management.base import BaseCommand
from open_ricostruzione.utils import UnicodeDictWriter
from optparse import make_option
from pprint import pprint

from open_ricostruzione.models import InterventoProgramma


class Command(BaseCommand):
    help = 'Export interventi programma data to CSV file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),

    )

    output_file = ''
    encoding = "UTF-8"
    logger = logging.getLogger('csvimport')

    def write_donazione(self, intervento):

        gps_lat = str(intervento.gps_lat)
        gps_lon = str(intervento.gps_lon)
        if intervento.gps_lat is None:
            gps_lat = ''
        if intervento.gps_lon is None:
            gps_lon = ''

        D = {
                'id_fenice': str(intervento.id_fenice),
                'denominazione': intervento.denominazione,
                'lat': gps_lat,
                'long': gps_lon,
            }
        self.udw.writerow(D)


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

        self.output_file = options['file']

        f = open(self.output_file, "w")
        fieldnames = ['id_fenice','denominazione', 'lat', 'long']
        self.udw = UnicodeDictWriter(f, fieldnames=fieldnames, dialect=csv.excel, encoding=self.encoding)
        self.udw.writer.writeheader()
        self.logger.info('Open output file:{}'.format(self.output_file))
        interventi_programma = InterventoProgramma.objects.all().order_by('id_fenice')
        for intervento in interventi_programma:
            self.write_donazione(intervento)

        f.close()
        self.logger.info('Finished writing {} interv.programma'.format(interventi_programma.count()))
