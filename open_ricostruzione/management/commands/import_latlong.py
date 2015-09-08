# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from open_ricostruzione.models import InterventoProgramma
from open_ricostruzione.utils import UnicodeDictReader
from optparse import make_option
import logging
import csv


class Command(BaseCommand):
    help = 'Import interv.programma lat/long data from CSV file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),

    )

    input_file = ''
    delete = ''
    # encoding = 'UTF-8'
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
        self.logger.info('Input file:{}'.format(self.input_file))
        udr = None

        # read file
        try:
            udr = UnicodeDictReader(f=open(self.input_file),dialect=csv.excel, encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)

        self.logger.info("Done")
        row_counter=0
        for row in udr:
            ip = None
            row_counter+=1
            idfenice = row['PROG']
            lat = row['lat']
            long = row['long']

            self.logger.debug(u"Import latlong (Line {}) pk:{}, lat:{}, long:{} ".format(row_counter, idfenice, lat, long ))
            try:
                ip = InterventoProgramma.objects.get(id_fenice=idfenice)
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                self.logger.error("Line {} - id fenice:{} does not exist in db, skip".format(row_counter,idfenice))
                continue

            else:
                ip.lat = float(lat)
                ip.long = float(long)
                ip.save()