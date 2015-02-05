# -*- coding: utf-8 -*-
import csv
from django.core.management.base import BaseCommand, CommandError
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import set_autocommit, commit
import xlrd
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
    encoding = 'latin-1'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):

        self.input_file = options['file']
        self.delete = options['delete']
        self.logger.info('Input file:{}'.format(self.input_file))
        book = None
        # read file
        try:
            book = xlrd.open_workbook(self.input_file)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)
        except csv.Error, e:
            self.logger.error("Error while reading %s: %s\n" % (self.input_file, e.message))

        if self.delete:
            self.logger.info("Deleting all previous records...")
            Donazione.objects.all().delete()
            self.logger.info("Done")

        # define date format
        date_format = '%d/%M/%Y'
        worksheet = book.sheet_by_index(0)

        donazioni_list = []
        for row_counter in range(worksheet.nrows):
            row = []
            if row_counter == 0:
                # header row
                continue
            for col_counter in range(worksheet.ncols):
                row.append(worksheet.cell_value(row_counter,col_counter))

            # COLUMNS
            #
            # 1: Tipologia del Cedente (1)
            # 2: Denominazione Cedente (2)
            # 3: Comune Ricevente
            # 4: Data Comunicazione (3)
            # 5: Importo
            # 6: Ulteriori informazioni
            # 7: Tipologia (1=diretta,2=tramite regione)

            territorio = None
            try:
                territorio = Territorio.objects.get(denominazione=row[3])
            except ObjectDoesNotExist:
                self.logger.error(u"Could not find Territorio with denominazione:{}".format(row[3]))
                exit()

            data = datetime.strptime(row[4], date_format)

            tipologia_donazione = row[7]

            if tipologia_donazione != '1' and tipologia_donazione != '2':
                self.logger.error(u"Tipologia donazione value is not accepted:{}".format(tipologia_donazione))
                continue

            # todo: add tipologia cedente
            tipologia_cedente = None

            don_dict = {
                'territorio': territorio,
                'informazioni': row[6],
                'denominazione': row[2],
                'tipologia_cedente': tipologia_cedente,
                'tipologia_donazione': tipologia_donazione,
                'data': data,
                'importo': Decimal(row[5].replace(',', '.').replace("€", '')),

            }

            donazioni_list.append(Donazione(**don_dict))

        # save all donazioni in a bulk create
        Donazione.objects.bulk_create(donazioni_list)