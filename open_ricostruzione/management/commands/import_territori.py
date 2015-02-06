# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from open_ricostruzione import utils
from open_ricostruzione.models import *
from optparse import make_option
from open_ricostruzione.utils import ExcelSemicolon
import csv
import logging


class Command(BaseCommand):
    help = 'Import territori data from CSV'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Select csv file'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    default=False,
                    help='Delete Existing Records: True|False'),

    )

    file = ''
    encoding = 'utf8'
    # encoding='latin1'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):

        self.file = options['file']
        self.logger.info('CSV FILE "%s"\n' % self.file)

        # read first csv file
        try:
            self.unicode_reader = \
                utils.UnicodeDictReader(open(self.file, 'r'), encoding=self.encoding, dialect=ExcelSemicolon)
        except IOError:
            self.logger.error("It was impossible to open file %s\n" % self.file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s\n" % (self.file, e.message))

        self.handle_localita(*args, **options)

    def handle_localita(self, delete, *args, **options):

        if delete:
            self.logger.info("Erasing the precedently stored data...")
            Territorio.objects.all().delete()

        self.logger.info("Inizio import da file")
        territori_list = list()

        for r in self.unicode_reader:

            #  campi da importare:territorio, cod_reg,cod_prov, cod_com, denominazione, slug
            codice_istat = r['cod_com']
            if r['territorio'] == 'C':
                codice_istat = "0" + codice_istat

            territori_list.append(
                Territorio(**{
                    'cod_comune': codice_istat,
                    'denominazione': r['denominazione'],
                    'tipo_territorio': r['territorio'],
                    'cod_provincia': r['cod_prov'],
                    'slug': r['slug'],
                }))

        # save all territori in a bulk create
        self.logger.info("Creating territori")
        Territorio.objects.bulk_create(territori_list)
        self.logger.info("Done")