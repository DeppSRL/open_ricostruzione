# -*- coding: utf-8 -*-
import csv
from pprint import pprint
from django.core.management.base import BaseCommand, CommandError
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import xlrd
from django.conf import settings
from open_ricostruzione.models import Donazione
from territori.models import Territorio
from optparse import make_option
import logging
from datetime import datetime


class RowData(object):
    tipologia_cedente = None
    denominazione = None
    territorio = None
    data = None
    importo = None
    info = None
    tipologia_donazione = None
    # COLUMNS
    # 0: tipologia cedente
    # 1: denominazione cedente
    # 2: comune
    # 3: data
    # 4: importo
    # 5: ulteriori info
    # 6: tipologia (1=diretta, 2=dalla regione)

    def __init__(self, row):
        self.tipologia_cedente = row[0].strip()
        self.denominazione = row[1].strip()
        self.territorio = row[2].strip()
        # todo add data import
        # if row[3] != '':
        #     try:
        #         data = datetime.strptime(row[3], date_format)
        #     except (TypeError, ValueError):
        #         self.logger.error(u"Invalid date value:{}".format(row[3]))
        #
        #         continue
        self.data = row[3]
        self.importo = row[4]
        self.info = row[5].strip()
        self.tipologia_donazione = str(int(row[6]))


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
                    default=True,
                    help='Delete Existing Records'),
        make_option('--no-bulk',
                    dest='no_bulk',
                    action='store_true',
                    default=True,
                    help='Avoid saving donazione in a bulk create'),

    )

    input_file = ''
    delete = ''
    encoding = 'latin-1'
    logger = logging.getLogger('csvimport')
    bulk_create = True
    unicode_reader = None

    def print_wrong_line(self, row, row_counter):
        self.logger.error("Row {}:{}".format(row_counter, row))

    # converts worksheet to a list of RowData obj
    def worksheet_2_list(self, worksheet):
        rowlist = []
        for row_counter in range(worksheet.nrows):
            row = []
            if row_counter == 0:
                # header row
                continue
            for col_counter in range(worksheet.ncols):
                row.append(worksheet.cell_value(row_counter, col_counter))
            rowlist.append(RowData(row))
        return rowlist

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
        # if no bulk is TRUE -> bulk create is FALSE
        self.bulk_create = not options['no_bulk']
        self.logger.info('Input file:{}'.format(self.input_file))
        book = None
        tipologia_cedente_dict = {}
        territori_not_found= {}
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

        # todo: define date format
        date_format = '%Y-%M-%d'
        worksheet = book.sheet_by_index(0)
        row_list = self.worksheet_2_list(worksheet)
        donation_counter = 0
        donazioni_list = []
        for row_counter, rowdata in enumerate(row_list):
            self.logger.info(u"Import donazione:{}".format(rowdata.denominazione))

            if rowdata.tipologia_cedente not in tipologia_cedente_dict:
                tipologia_cedente_dict[rowdata.tipologia_cedente] = 1
            else:
                tipologia_cedente_dict[rowdata.tipologia_cedente] += 1

            territorio = None
            try:
                territorio = Territorio.objects.get(denominazione=rowdata.territorio, tipologia="C")
            except ObjectDoesNotExist:
                # try with the Comuni in cratere starting with territorio name

                try:
                    territorio = Territorio.objects.filter(istat_id__in=settings.COMUNI_CRATERE).get(denominazione__startswith=rowdata.territorio)
                except ObjectDoesNotExist:
                    self.logger.error(u"Could not find Territorio with denominazione:{}".format(rowdata.territorio))
                    self.print_wrong_line(rowdata, row_counter)

                    if rowdata.territorio not in territori_not_found:
                        territori_not_found[rowdata.territorio] = 1
                    else:
                        territori_not_found[rowdata.territorio] += 1

                    continue
            except MultipleObjectsReturned:
                self.logger.error(u"Multiple obj found for Territorio with denominazione:{}".format(rowdata.territorio))
                exit()

            data = None

            if rowdata.tipologia_donazione != '1' and rowdata.tipologia_donazione != '2':
                self.logger.error(u"Tipologia donazione value is not accepted:{}".format(rowdata.tipologia_donazione))
                self.print_wrong_line(rowdata, row_counter)
                continue

            # todo: add tipologia cedente
            tipologia_cedente = ''

            don_dict = {
                'territorio': territorio,
                'informazioni': rowdata.info,
                'denominazione': rowdata.denominazione,
                'tipologia_cedente': tipologia_cedente,
                'tipologia_donazione': rowdata.tipologia_donazione,
                'data': data,
                'importo': Decimal(rowdata.importo),

            }
            if self.bulk_create:
                donazioni_list.append(Donazione(**don_dict))
            else:
                d = Donazione(**don_dict)
                d.save()

            donation_counter+=1

        if self.bulk_create:
            # save all donazioni in a bulk create
            Donazione.objects.bulk_create(donazioni_list)

        # tipologia cedente found output
        self.logger.info("********** Found following tipologia cedente ***********")
        for tc, counter in tipologia_cedente_dict.iteritems():
            self.logger.info("{}:{}".format(tc, counter))

        if len(territori_not_found.keys()):
            self.logger.info("********** Territori not found ***********")
            for t, counter in territori_not_found.iteritems():
                self.logger.info("{}:{}".format(t, counter))


        self.logger.info("Imported {} donazioni".format(donation_counter))