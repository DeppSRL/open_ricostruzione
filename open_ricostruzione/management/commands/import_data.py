# -*- coding: utf-8 -*-
import json
from pprint import pprint
from django.core.management import call_command
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.serializers.json import DjangoJSONEncoder
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
    )

    logger = logging.getLogger('csvimport')
    today_str = datetime.strftime(datetime.today(), "%Y-%m-%d-%H%M")
    dump_donazioni_intprog_file = "{}/log/import_{}_temp.json".format(settings.PROJECT_ROOT, today_str)
    error_logfile = "{}/log/import_{}_err.json".format(settings.PROJECT_ROOT, today_str)

    def dump_donazioni_intervento(self):
        ##
        # dumps all DonazioneProgramma that link Donazione to InterventoProgramma so this obj are not
        # lost when the script will delete all InterventoProgramma objs.
        ##

        self.logger.info("Checking Donazioni Programma before import...")

        ##
        # stores all donazioni intervento programma in memory
        ##

        self.donazioni_intervento_programma = list(
            DonazioneInterventoProgramma. \
                objects.all().order_by('intervento_programma__programma__id'). \
                values(
                'donazione__importo',
                'donazione__pk',
                'donazione__denominazione',
                'intervento_programma__programma__id',
                'intervento_programma__id_fenice',
                'intervento_programma__soggetto_attuatore__id_fenice',
                'intervento_programma__propr_immobile__id_fenice',
                'intervento_programma__n_ordine',
                'intervento_programma__importo_generale',
                'intervento_programma__importo_a_programma',
                'intervento_programma__denominazione',
                'intervento_programma__territorio__slug',
                'intervento_programma__tipo_immobile',
                'intervento_programma__tipo_immobile_fenice',
                'intervento_programma__slug',
            )
        )

        if len(self.donazioni_intervento_programma) > 0:
            # dump json file
            with open(self.dump_donazioni_intprog_file, 'w') as outfile:
                json.dump(self.donazioni_intervento_programma, outfile, indent=4, cls=DjangoJSONEncoder)

            self.logger.info("Saved {} Donazioni Programma".format(len(self.donazioni_intervento_programma)))
            self.logger.info("Dumped ALL Donazioni Programma in temp file:{}".format(self.dump_donazioni_intprog_file))
        else:
            self.logger.info("No Donazioni Programma found")

    def associate_don_progr(self):
        ##
        # associates back intervento programma and donazioni to Intervento programma
        ##
        ids_to_pop = []
        for idx, dip_dict in enumerate(self.donazioni_intervento_programma):
            iap = None
            dip = None
            try:
                iap = InterventoProgramma.objects.get(
                    id_fenice=dip_dict['intervento_programma__id_fenice'])
            except ObjectDoesNotExist:
                self.logger.error(
                    u"Cannot find Intervento a programma id_fenice:'{}' to associate with Donazione:'{}' id:{}".format(
                        dip_dict['intervento_programma__id_fenice'], dip_dict['donazione__denominazione'],
                        dip_dict['donazione__pk']))
                continue

            try:
                dip = DonazioneInterventoProgramma.objects.get(donazione__pk=dip_dict['donazione__pk'])
            except ObjectDoesNotExist:
                self.logger.error(
                    u"Cannot find Donazione Intervento a programma donazione__pk:{} to associate with Intervento id_fenice:{}".format(
                        dip_dict['donazione__pk'],
                        dip_dict['intervento_programma__id_fenice'],
                        )
                    )
                continue

            dip.intervento_programma = iap
            dip.save()
            ids_to_pop.append(idx)

        #     actually removes donazioni intervento from list
        for id in ids_to_pop:
            self.donazioni_intervento_programma.pop(id)


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

        ##
        # Import data with donazioni already in db
        # 1. dump file donazioni a interventi a progetto
        # 2. delete dati (interventi a prog, sogg.attuatori, anagrafiche, ecc)
        # 3. call import_tipologie
        # 4. call import_interventi
        # 5. re-associate interventi and donazioni based on the dump file
        ##

        path = options['path']

        tipologia_filename ="FENICE_OR_DatiBase.json"
        interventi_filename ="FENICE_OR_Interventi.json"

        tipologie_file = u"{}{}".format(path, tipologia_filename )
        interventi_file = u"{}{}".format(path, interventi_filename )

        ##
        # dump donazioni/intervento
        self.dump_donazioni_intervento()
        ##
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
        # re-associate interventi and donazioni based on the dump file
        ##
        if len(self.donazioni_intervento_programma)>0:
            self.logger.info("Recovering Donazioni Programma")

            total_donazioni_intervento = len(self.donazioni_intervento_programma)
            self.associate_don_progr()
            not_associated_donazioni_intervento = len(self.donazioni_intervento_programma)
            associated_donazioni_intervento = total_donazioni_intervento - not_associated_donazioni_intervento
            if associated_donazioni_intervento > 0:
                self.logger.info("Correctly associated {} Donazioni Programma".format(associated_donazioni_intervento, ))
            if not_associated_donazioni_intervento > 0:
                self.logger.error(u"Could NOT ASSOCIATE {} Donazioni Programma. Dumped ONLY ERROR DATA in file {}".
                    format(not_associated_donazioni_intervento, self.error_logfile))
                # dump json error file
                with open(self.error_logfile, 'w') as outfile:
                    json.dump(self.donazioni_intervento_programma, outfile, indent=4, cls=DjangoJSONEncoder)

        self.logger.info("Done")
