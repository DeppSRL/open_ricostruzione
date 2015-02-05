# -*- coding: utf-8 -*-
import csv
from django.core.management.base import BaseCommand, CommandError
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import set_autocommit, commit
from open_ricostruzione import utils
from open_ricostruzione.models import Donazione, Territorio
from optparse import make_option
import logging
from datetime import datetime
from django.utils import timezone


class Command(BaseCommand):
    help = 'Import donazioni data from XLS file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to xls file'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    default=False,
                    help='Delete Existing Records'),

    )

    input_file = ''
    delete = ''
    encoding = 'utf8'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):

        self.input_file = options['file']
        self.delete = options['delete']
        self.logger.info('Input file:{}'.format(self.input_file))

        # read file
        try:
            self.unicode_reader = \
                utils.UnicodeDictReader(open(self.input_file, 'r'), encoding=self.encoding, dialect="excel")
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)
        except csv.Error, e:
            self.logger.error("Error while reading %s: %s\n" % (self.input_file, e.message))

        if self.delete:
            self.logger.info("Deleting all previous records...")
            Donazione.objects.all().delete()
            self.logger.info("Done")

        # todo: define date format!!
        date_format = ''

        donazioni_list = []
        for row in self.unicode_reader:

            # COLUMNS
            #
            # Tipologia del Cedente (1)
            # Denominazione Cedente (2)
            # Comune Ricevente
            # Data Comunicazione (3)
            # Importo
            # Ulteriori informazioni
            # Tipologia (1=diretta,2=tramite regione)

            territorio = None
            try:
                territorio = Territorio.objects.get(denominazione=row['Comune Ricevente'])
            except ObjectDoesNotExist:
                self.logger.error(u"Could not find Territorio with denominazione:{}")
                exit()

            data = datetime.strptime(row['Data Comunicazione (3)'], date_format)

            tipologia_donazione = row['Tipologia (1=diretta,2=tramite regione)']

            if tipologia_donazione != '1' and tipologia_donazione != '2':
                self.logger.error(u"Tipologia donazione value is not accepted:{}".format(tipologia_donazione))
                continue

            # todo: add tipologia cedente
            tipologia_cedente = None

            don_dict = {
                'territorio': territorio,
                'informazioni': row['Ulteriori informazioni'],
                'denominazione': row['Denominazione Cedente (2)'],
                'tipologia_cedente': tipologia_cedente,
                'tipologia_donazione': tipologia_donazione,
                'data': data,
                'importo': Decimal(row['Importo'].replace(',', '.').replace("€", '')),

            }

            donazioni_list.append(Donazione(**don_dict))

        # save all donazioni in a bulk create
        Donazione.objects.bulk_create(donazioni_list)