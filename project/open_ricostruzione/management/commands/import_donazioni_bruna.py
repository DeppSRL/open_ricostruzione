# -*- coding: utf-8 -*-
import csv
import logging
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db.models import Q
from open_ricostruzione.utils import UnicodeDictReader
from optparse import make_option
from pprint import pprint

from open_ricostruzione.models import Donazione, DonazioneInterventoProgramma, InterventoProgramma, UltimoAggiornamento
from territori.models import Territorio


#############
## WARNING ##
#############
## this is a ONE TIME IMPORT, normal import is done by import_donazioni
##


class DateException(BaseException):
    pass


class RowData(object):
    tipologia_cedente = None
    denominazione = None
    territorio = None
    data = None
    importo = None
    info = None
    n_ordine = None
    tipologia_donazione = None
    logger = logging.getLogger('csvimport')
    # define date format
    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y-%d-%m']

    # COLUMNS
    # 'Tipologia del Cedente (1)': u'SPA',
    # 'Denominazione Cedente (2)': u'PAM PANORAMA S.P.A.',
    #  'Comune Ricevent': u'Baricella',
    # 'Data Comunicazione (3)': u'06/07/2012',
    # 'Importo': u'\xe2\x82\xac 54.759,00',
    # 'Ulteriori informazioni': u''
    # 'Tipologia (1=diretta,2=tramite regione)': u'2',
    # 'n_ordine': u'',

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

    annoying_chars = [
        u'\xc2\x82u',## u',u',        # High code comma
        u'\xc2\x84u',## u',,u',       # High code double comma
        u'\xc2\x85u',## u'...u',      # Tripple dot
        u'\xc2\x88u',## u'^u',        # High carat
        u'\xc2\x91u',## u'\x27u',     # Forward single quote
        u'\xc2\x92u',## u'\x27u',     # Reverse single quote
        u'\xc2\x93u',## u'\x22u',     # Forward double quote
        u'\xc2\x94u',## u'\x22u',     # Reverse double quote
        u'\xc2\x95u',## u' u',
        u'\xc2\x96u',## u'-u',        # High hyphen
        u'\xc2\x97u',## u'--u',       # Double hyphen
        u'\xc2\x99u',## u' u',
        u'\xc2\xa0u',## u' u',
        u'\xc2\xa6u',## u'|u',        # Split vertical bar
        u'\xc2\xabu',## u'<<u',       # Double less than
        u'\xc2\xbbu',## u'>>u',       # Double greater than
        u'\xc2\xbcu',## u'1/4u',      # one quarter
        u'\xc2\xbdu',## u'1/2u',      # one half
        u'\xc2\xbeu',## u'3/4u',      # three quarters
        u'\xca\xbfu',## u'\x27u',     # c-single quote
        u'\xcc\xa8u',## u'u',         # modifier - under curve
        u'\xcc\xb1u',## u'u'          # modifier - under line
        u'\xe2\x82\xac',##
        u'\x85',##
        u'\xc2\x99',##
        u'\xc2\x85',##
        u' ',##
        u'\u20ac',##
        u'',##
    ]

    def __init__(self, row):

        tipologia_cedente_string = row['Tipologia del Cedente (1)'].strip()
        self.tipologia_cedente = self.tipologia_cedente_map[tipologia_cedente_string]
        self.denominazione = row['Denominazione Cedente (2)'].strip()
        self.territorio = row.get('Comune Ricevent', None)
        self.info = row.get('Ulteriori informazioni','').strip()
        if self.territorio is None:
            self.logger.error(u"Territorio cell is empty in row {}".format(row))
            exit()
        else:
            self.territorio = self.territorio.strip()

        self.n_ordine = row.get('n_ordine', None)
        # date conversion
        data = -1
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
                # if the previous cycle failed,
                # try to import only month and day
                try:
                    data = datetime.strptime("{}{}".format(row['Data Comunicazione (3)'][:-2], "28"),
                                             self.date_formats[2])
                except ValueError:
                    pass

        self.data = data
        if row['Importo']:
            self.importo = row['Importo'].strip()

            for c in self.annoying_chars:
                self.importo = self.importo.replace(c, "")

            self.importo = self.importo.\
                replace('.','').\
                replace(',', '.')

            self.importo = Decimal(self.importo)
        else:
            self.importo = Decimal(0)

        try:
            self.tipologia_donazione = str(int(row['Tipologia (1=diretta,2=tramite regione)']))
        except ValueError:
            self.tipologia_donazione = None

    def __str__(self):
        return u"{},{},{},{},{},{},{},{}".format(self.tipologia_cedente, self.denominazione, self.territorio, self.data,
                                                 self.importo, self.info, self.tipologia_donazione, self.n_ordine)

    def __repr__(self):
        return self.__str__()


class Command(BaseCommand):
    help = 'Import donazioni data from CSV file used by Bruna Cavalera (POLEIS). WARNING: this is a ONE TIME IMPORT, normal import is done by import_donazioni'

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
    invalid_values_counter = 0
    default_date = datetime.strptime("2012-01-01", "%Y-%m-%d")


    def print_wrong_line(self, rowdata, row_counter):
        self.logger.error(u"Row {}:'{}'".format(row_counter, rowdata))

    def get_territorio(self, territorio_denominazione):
        territorio = None
        try:
            territorio = Territorio.objects.get(denominazione=territorio_denominazione, tipologia="C")
        except ObjectDoesNotExist:
            # try with the Comuni in cratere starting with territorio name

            try:
                territorio = Territorio.objects.filter(istat_id__in=settings.COMUNI_CRATERE,tipologia="C").get(
                    denominazione__startswith=territorio_denominazione)
            except ObjectDoesNotExist:
                self.logger.error(u"Could not find Territorio with denominazione:{}".format(territorio_denominazione))
                return None
        except MultipleObjectsReturned:
            self.logger.error(
                u"Multiple obj found for Territorio with denominazione:{}".format(territorio_denominazione))
            exit()

        return territorio

    def handle_error(self, rowdata, row_counter, error_msg, imported):
        self.logger.error("Line:{}, ".format(row_counter)+error_msg)
        # self.print_wrong_line(rowdata, row_counter)
        if imported is False:
            self.invalid_values_counter += 1

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
        territori_not_found = {}
        wrong_dates = {}
        wrong_date_counter = 0
        missing_date_counter = 0

        # read file
        try:
            udr = UnicodeDictReader(f=open(self.input_file),dialect=csv.excel, encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)

        self.logger.info("Deleting all previous records...")
        Donazione.objects.all().delete()
        DonazioneInterventoProgramma.objects.all().delete()
        self.logger.info("Done")

        row_counter = -1
        for row in udr:
            ip = None
            row_counter += 1
            rowdata = RowData(row)

            if rowdata.data == -1:
                self.handle_error(rowdata, row_counter, u"Invalid date value:{}, default date is used instead".format(row['Data Comunicazione (3)']), imported=True)
                rowdata.data = self.default_date

            self.logger.debug(u"Import donazione (Line {}) {}".format(row_counter, rowdata.denominazione))


            if rowdata.importo == Decimal(0):
                self.handle_error(rowdata, row_counter, "Donazione has importo=0, skip", imported=False)
                continue

            if rowdata.tipologia_donazione is None or (
                        rowdata.tipologia_donazione != '1' and rowdata.tipologia_donazione != '2'):
                self.handle_error(rowdata, row_counter, "Donazione has incorrect tipologia_donazione:'{}', skip".format(rowdata.tipologia_donazione), imported=False)
                continue

            if rowdata.data is None:
                missing_date_counter += 1
                self.handle_error(rowdata, row_counter, "Donazione has no date, skip", imported=False)
                continue

            territorio = self.get_territorio(rowdata.territorio)
            if territorio is None:
                self.handle_error(rowdata, row_counter, "Donazione has wrong territorio, skip", imported=False)

                if rowdata.territorio not in territori_not_found:
                    territori_not_found[rowdata.territorio] = 1
                else:
                    territori_not_found[rowdata.territorio] += 1

                continue

            if rowdata.n_ordine:
                n_ordine_zeropad = rowdata.n_ordine.zfill(6)
                try:
                    ip = InterventoProgramma.objects.get(Q(n_ordine=rowdata.n_ordine)|Q(n_ordine=n_ordine_zeropad))
                except ObjectDoesNotExist:

                    self.handle_error(rowdata, row_counter, u"Cannot find interv.programma for n_ordine:'{}'".format(n_ordine_zeropad), imported=True)
                    pass

                else:
                    self.logger.debug(u"Found intervento:{} associated with donazione".format(ip.slug))

            don_dict = {
                'territorio': territorio,
                'informazioni': rowdata.info,
                'denominazione': rowdata.denominazione,
                'tipologia_cedente': rowdata.tipologia_cedente,
                'tipologia_donazione': rowdata.tipologia_donazione,
                'data': rowdata.data,
                'importo': rowdata.importo,

            }

            donazione = Donazione(**don_dict)
            donazione.save()
            if ip is not None:
                # if the donazione is linked to an InterventoProgramma, creates
                # the DonazioneInterventoProgramma object
                dip = DonazioneInterventoProgramma()
                dip.intervento_programma = ip
                dip.donazione = donazione
                dip.save()



        if wrong_date_counter > 0:
            self.logger.error("********** Wrong dates ***********")
            self.logger.error("Found {} wrong dates".format(wrong_date_counter))
            for key, value in wrong_dates.iteritems():
                self.logger.error("{}:{}".format(key, value))

        if missing_date_counter > 0:
            self.logger.error("Found {} missing dates".format(missing_date_counter))

        if self.invalid_values_counter > 0:
            self.logger.error("********** Invalid data ***********")
            self.logger.error("Could not import {} donazioni for errors in the data".format(self.invalid_values_counter))

        if len(territori_not_found.keys()):
            self.logger.error("********** Territori not found ***********")
            for t, counter in territori_not_found.iteritems():
                self.logger.error("{}:{}".format(t, counter))

        self.logger.info("Imported {} donazioni".format(Donazione.objects.count()))

        UltimoAggiornamento.objects.update_or_create(
            tipologia=UltimoAggiornamento.TIPOLOGIA.DONAZIONI,
            defaults={
                'data': datetime.today(),
            }
        )
        self.logger.info("Set Ultimo aggiornamento to today")
