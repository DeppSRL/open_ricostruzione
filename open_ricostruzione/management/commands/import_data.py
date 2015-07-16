# -*- coding: utf-8 -*-
from pprint import pprint
from django.core.management import call_command
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.db.transaction import set_autocommit, commit
from django.conf import settings
from open_ricostruzione.models import Donazione, DonazioneInterventoProgramma, InterventoProgramma, UltimoAggiornamento
from open_ricostruzione.utils import UnicodeDictReader
from territori.models import Territorio
from optparse import make_option
import logging
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Import interventi, tipologie and donazioni from files'

    option_list = BaseCommand.option_list + (
        make_option('--path',
                    dest='path',
                    default='',
                    help='Path to folder with tipologia and interventi (with trailing slash)'),
        make_option('--donazioni',
                    dest='donazioni',
                    default='',
                    help='Path to donazioni files'),
    )

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

        path = options['path']
        donazioni_file = options['donazioni']

        tipologia_filename ="FENICE_OR_DatiBase.json"
        interventi_filename ="FENICE_OR_Interventi.json"

        tipologie_file = u"{}{}".format(path, tipologia_filename )
        interventi_file = u"{}{}".format(path, interventi_filename )

        ##
        # Import tipologie
        ##

        self.logger.info(u"Import tipologie")
        call_command('import_tipologie', verbosity=1, file=tipologie_file, interactive=False)

        ##
        # Import interventi
        ##

        self.logger.info(u"Import interventi")
        call_command('import_interventi', verbosity=1, file=interventi_file, interactive=False)

        ##
        # Import donazioni
        ##

        self.logger.info(u"Import donazioni")
        call_command('import_donazioni', verbosity=1, file=donazioni_file, interactive=False)
        self.logger.info(u"Done")



