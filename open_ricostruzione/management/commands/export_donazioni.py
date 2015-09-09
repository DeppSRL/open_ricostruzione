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
        date_format = '%d/%m/%Y'
        D = {
                'id': str(donazione.pk),
                'Tipologia del Cedente (1)': Donazione.TIPO_CEDENTE[donazione.tipologia_cedente],
                'Denominazione Cedente (2)': donazione.denominazione,
                'Comune Ricevente': donazione.territorio.denominazione,
                'Data Comunicazione (3)': datetime.strftime(donazione.data, date_format),
                'Importo': str(donazione.importo),
                'Tipologia (1=diretta,2=tramite regione)': donazione.tipologia_donazione,
                'n_ordine': n_ordine
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
        fieldnames = ['id', 'Tipologia del Cedente (1)', 'Denominazione Cedente (2)', 'Comune Ricevente',
                      'Data Comunicazione (3)', 'Importo', 'Tipologia (1=diretta,2=tramite regione)', 'n_ordine']
        self.udw = UnicodeDictWriter(f, fieldnames=fieldnames, dialect=csv.excel, encoding=self.encoding)
        self.udw.writer.writeheader()
        self.logger.info('Open output file:{}'.format(self.output_file))
        donazioni = Donazione.objects.all().order_by('territorio', 'denominazione',
                                                     'donazioneinterventoprogramma__intervento_programma__n_ordine',
                                                     'importo')
        for d in donazioni:

            n_ordine = ''
            self.logger.debug(u"Donazione:{} ".format(d.pk, ))
            try:
                dip = DonazioneInterventoProgramma.objects.get(donazione=d)
                n_ordine = dip.intervento_programma.n_ordine
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                dip_list = DonazioneInterventoProgramma.objects.filter(donazione=d)
                self.logger.error(u"Donazione:{} has {} DonazioneInterventoProgramma, this should NOT HAPPEN and will generate double lines in CSV".format(d.pk, len(dip_list)))
                for single_dip in dip_list:
                    self.write_donazione(d, single_dip.intervento_programma.n_ordine)
                continue

            self.write_donazione(d, n_ordine)

        self.logger.info('Finished writing {} donazioni'.format(donazioni.count()))
