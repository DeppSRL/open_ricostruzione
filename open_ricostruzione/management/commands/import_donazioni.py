# -*- coding: utf-8 -*-
import csv
from pprint import pprint
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import xlrd
from django.conf import settings
from open_ricostruzione.models import Donazione, UltimoAggiornamento
from open_ricostruzione.utils import UnicodeDictReader
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
    logger = logging.getLogger('csvimport')
    # define date format
    date_formats = ['%Y-%M-%d', '%d/%M/%Y', '%Y-%M-%d']
    tipologia_cedente_map = {
        '': Donazione.TIPO_CEDENTE.ALTRO,
        'ALTRO': Donazione.TIPO_CEDENTE.ALTRO,
        'DONAZIONI ESTERO': Donazione.TIPO_CEDENTE.ALTRO,
        'ASSOCIAZIONE': Donazione.TIPO_CEDENTE.ASSOCIAZIONI,
        'ALTRI ENTI PUBBLICI': Donazione.TIPO_CEDENTE.ENTI_PUBBLICI,
        'ALTRO ENTE PUBBLICO': Donazione.TIPO_CEDENTE.ENTI_PUBBLICI,
        'COMUNE': Donazione.TIPO_CEDENTE.COMUNI,
        'CITTADINO/PUBBLICO': Donazione.TIPO_CEDENTE.CITTADINI,
        'COMUNI': Donazione.TIPO_CEDENTE.COMUNI,
        'SRL': Donazione.TIPO_CEDENTE.AZIENDE,
        'SPS': Donazione.TIPO_CEDENTE.AZIENDE,
        'CITTADINO/PRIVATO': Donazione.TIPO_CEDENTE.CITTADINI,
        'SPA': Donazione.TIPO_CEDENTE.AZIENDE,
        'REGIONE': Donazione.TIPO_CEDENTE.REGIONI,
        'PRIVATO': Donazione.TIPO_CEDENTE.CITTADINI,
        'ALTRE IMPR./SOC./COOP./SAS': Donazione.TIPO_CEDENTE.AZIENDE,
        'PROVINCE': Donazione.TIPO_CEDENTE.PROVINCE,
    }

    # COLUMNS
    #    {'Comune Ricevent': u'Baricella',
    # 'Data Comunicazione (3)': u'06/07/2012',
    # 'Denominazione Cedente (2)': u'PAM PANORAMA S.P.A.',
    # 'Importo': u'\xe2\x82\xac 54.759,00',
    # 'Tipologia (1=diretta,2=tramite regione)': u'2',
    # 'Tipologia del Cedente (1)': u'SPA',
    # 'Ulteriori informazioni': u''}

    def __init__(self, row):

        tipologia_cedente_string = row['Tipologia del Cedente (1)'].strip()
        self.tipologia_cedente = self.tipologia_cedente_map[tipologia_cedente_string]
        self.denominazione = row['Denominazione Cedente (2)'].strip()
        self.territorio = row.get('Comune Ricevent', None)
        if self.territorio is None:
            self.logger.error("Territorio data not found! Quit")
            exit()
        else:
            self.territorio = self.territorio.strip()

        # date conversion
        data = ''
        if row['Data Comunicazione (3)'] != '':
            date_imported = False
            for date_format in self.date_formats:
                try:
                    data = datetime.strptime(row['Data Comunicazione (3)'], date_format)
                except (TypeError, ValueError):
                    continue
                else:
                    date_imported = True
                    break

            if date_imported is False:
                # try to import only month and day
                try:
                    data = datetime.strptime("{}{}".format(row['Data Comunicazione (3)'][:-2], "28"),
                                             self.date_formats[2])
                except ValueError:
                    self.logger.error(u"Invalid date value:{}".format(row['Data Comunicazione (3)']))

        else:
            data = None

        self.data = data
        self.importo = row['Importo'].strip().replace(u'\xe2\x82\xac', '').replace(' ', '').replace('.', '').replace(
            ',', '.')
        self.importo = Decimal(self.importo)
        self.info = row['Ulteriori informazioni'].strip()
        self.tipologia_donazione = str(int(row['Tipologia (1=diretta,2=tramite regione)']))


class Command(BaseCommand):
    help = 'Import donazioni data from XLS file'

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
    default_date = datetime.strptime("2012-09-01", "%Y-%M-%d")

    def print_wrong_line(self, row, row_counter):
        self.logger.error("Row {}:{}".format(row_counter, row))

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
        udr = None
        territori_not_found = {}
        wrong_dates = {}
        wrong_date_counter = 0
        missing_date_counter = 0
        # read file
        try:
            udr = UnicodeDictReader(f=open(self.input_file), encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)

        if self.delete:
            self.logger.info("Deleting all previous records...")
            Donazione.objects.all().delete()
            self.logger.info("Done")

        donation_counter = 0
        donazioni_list = []
        row_counter = -1
        for row in udr:
            row_counter += 1
            rowdata = RowData(row)
            self.logger.info(u"Import donazione (Line {}) {}".format(row_counter, rowdata.denominazione))

            if type(rowdata.data) == str:
                wrong_date_counter += 1

                # adds wrong date to dict
                if rowdata.data not in wrong_dates:
                    wrong_dates[rowdata.data] = 1
                else:
                    wrong_dates[rowdata.data] += 1

                rowdata.data = None
            elif rowdata.data is None:
                missing_date_counter += 1
                rowdata.data = None

            territorio = None
            try:
                territorio = Territorio.objects.get(denominazione=rowdata.territorio, tipologia="C")
            except ObjectDoesNotExist:
                # try with the Comuni in cratere starting with territorio name

                try:
                    territorio = Territorio.objects.filter(istat_id__in=settings.COMUNI_CRATERE).get(
                        denominazione__startswith=rowdata.territorio)
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

            if rowdata.tipologia_donazione != '1' and rowdata.tipologia_donazione != '2':
                self.logger.error(u"Tipologia donazione value is not accepted:{}".format(rowdata.tipologia_donazione))
                self.print_wrong_line(rowdata, row_counter)
                continue

            don_dict = {
                'territorio': territorio,
                'informazioni': rowdata.info,
                'denominazione': rowdata.denominazione,
                'tipologia_cedente': rowdata.tipologia_cedente,
                'tipologia_donazione': rowdata.tipologia_donazione,
                'data': rowdata.data,
                'importo': rowdata.importo,

            }
            if self.bulk_create:
                donazioni_list.append(Donazione(**don_dict))
            else:
                d = Donazione(**don_dict)
                d.save()

            donation_counter += 1

        if self.bulk_create:
            # save all donazioni in a bulk create
            Donazione.objects.bulk_create(donazioni_list)
        self.logger.info("Found {} wrong dates".format(wrong_date_counter))
        if wrong_date_counter > 0:
            self.logger.info("********** Wrong dates found ***********")
            for key, value in wrong_dates.iteritems():
                self.logger.info("{}:{}".format(key, value))

        self.logger.info("Found {} missing dates".format(missing_date_counter))

        if len(territori_not_found.keys()):
            self.logger.info("********** Territori not found ***********")
            for t, counter in territori_not_found.iteritems():
                self.logger.info("{}:{}".format(t, counter))

        self.logger.info("Imported {} donazioni".format(donation_counter))

        UltimoAggiornamento.objects.update_or_create(
            tipologia=UltimoAggiornamento.TIPOLOGIA.DONAZIONI,
            defaults={
                'data': datetime.today(),
            }
        )
        self.logger.info("Set Ultimo aggiornamento to today")
