# -*- coding: utf-8 -*-
from pprint import pprint
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from open_ricostruzione.models import Donazione, DonazioneInterventoProgramma
from open_ricostruzione.utils import UnicodeDictWriter
from optparse import make_option
import logging
import csv
from datetime import datetime


class Command(BaseCommand):
    help = 'Export donazioni data to XLS file for POLEIS work'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),

    )

    output_file = ''
    encoding = "UTF-8"
    logger = logging.getLogger('csvimport')

    def write_donazione(self, donazione, n_ordine):
        denominazione_cedente=''
        try:
            denominazione_cedente = donazione.denominazione.replace('"',"'").replace("&","").decode('utf-8')
        except UnicodeEncodeError:
            pass
        date_format = '%d/%m/%Y'


        D = {
                'id': str(donazione.pk),
                'Tipologia del Cedente (1)': Donazione.TIPO_CEDENTE[donazione.tipologia_cedente],
                'Denominazione Cedente (2)': denominazione_cedente,
                'Comune Ricevente': u"{}".format(donazione.territorio.denominazione),
                'Data Comunicazione (3)': datetime.strftime(donazione.data, date_format),
                'Importo': str(donazione.importo).replace(".",","),
                'Tipologia (1=diretta,2=tramite regione)': donazione.tipologia_donazione,
                'n_ordine': n_ordine
            }
        self.udw.writerow(D)

    def create_excel_file(self, csv_filename):
        import csv
        from xlsxwriter.workbook import Workbook


        workbook = Workbook(csv_filename.replace(".csv",".xlsx"))
        worksheet_link = workbook.add_worksheet("LINK_DONAZIONI_PROGETTI")
        worksheet_nuove = workbook.add_worksheet("NUOVE DONAZIONI")
        with open(csv_filename, 'rb') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet_link.write(r, c, col)
                    # writes the 1st row also in the second worsheet
                    if r == 0:
                        worksheet_nuove.write(r, c, col)


        workbook.close()

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
        fieldnames = ['id', 'Tipologia del Cedente (1)', 'Denominazione Cedente (2)', 'Comune Ricevente',
                      'Data Comunicazione (3)', 'Importo', 'Tipologia (1=diretta,2=tramite regione)', 'n_ordine']
        self.udw = UnicodeDictWriter(f, fieldnames=fieldnames, dialect=csv.excel, encoding=self.encoding)
        self.udw.writer.writeheader()
        self.logger.info('Open output file:{}'.format(self.output_file))
        donazioni = Donazione.objects.all().order_by('territorio', 'denominazione','importo')
        for donazione in donazioni:

            n_ordine = ''
            self.logger.debug(u"Donazione:{} ".format(donazione.pk, ))
            count_dip = DonazioneInterventoProgramma.objects.filter(donazione=donazione).count()
            if count_dip == 1:
                dip = DonazioneInterventoProgramma.objects.get(donazione=donazione)
                n_ordine = dip.intervento_programma.n_ordine
                self.write_donazione(donazione, n_ordine)
            elif count_dip == 0:
                self.write_donazione(donazione, n_ordine)
            elif count_dip > 1:
                dip_list = DonazioneInterventoProgramma.objects.filter(donazione=donazione)
                self.logger.error(u"Donazione:{} has {} DonazioneInterventoProgramma, this should NOT HAPPEN and will generate double lines in CSV".format(donazione.pk, len(dip_list)))
                for single_dip in dip_list:
                    self.write_donazione(donazione, single_dip.intervento_programma.n_ordine)

        f.close()
        self.create_excel_file(csv_filename=self.output_file)
        self.logger.info('Finished writing {} donazioni'.format(donazioni.count()))
