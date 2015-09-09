# -*- coding: utf-8 -*-
from pprint import pprint
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
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
        date_format = '%d/%m/%Y'

        f = open(self.output_file, "w")
        fieldnames = ['id', 'Tipologia del Cedente (1)', 'Denominazione Cedente (2)', 'Comune Ricevente',
                      'Data Comunicazione (3)', 'Importo', 'Tipologia (1=diretta,2=tramite regione)', 'n_ordine']
        udw = UnicodeDictWriter(f, fieldnames=fieldnames, dialect=csv.excel, encoding=self.encoding)
        udw.writer.writeheader()
        self.logger.info('Open output file:{}'.format(self.output_file))
        donazioni = Donazione.objects.all().order_by('territorio', 'denominazione',
                                                     'donazioneinterventoprogramma__intervento_programma__n_ordine',
                                                     'importo')
        for d in donazioni:

            n_ordine = ''
            try:
                dip = DonazioneInterventoProgramma.objects.get(donazione=d)
            except ObjectDoesNotExist:
                pass
            else:
                n_ordine = dip.intervento_programma.n_ordine

            data = datetime.strftime(d.data, date_format)

            D = {
                'id': str(d.pk),
                'Tipologia del Cedente (1)': Donazione.TIPO_CEDENTE[d.tipologia_cedente],
                'Denominazione Cedente (2)': d.denominazione,
                'Comune Ricevente': d.territorio.denominazione,
                'Data Comunicazione (3)': data,
                'Importo': str(d.importo),
                'Tipologia (1=diretta,2=tramite regione)': d.tipologia_donazione,
                'n_ordine': n_ordine
            }
            udw.writerow(D)

        self.logger.info('Finished writing {} donazioni'.format(donazioni.count()))
