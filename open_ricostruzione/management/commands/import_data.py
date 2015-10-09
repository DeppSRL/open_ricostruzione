# -*- coding: utf-8 -*-
import json
from pprint import pprint
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from open_ricostruzione.models import Donazione, DonazioneInterventoProgramma, InterventoProgramma
from optparse import make_option
import logging
from datetime import datetime


class Command(BaseCommand):
    help = 'Import interventi, tipologie and donazioni from files'

    option_list = BaseCommand.option_list + (
        make_option('--path',
                    dest='path',
                    default='',
                    help='Path to folder with tipologia and interventi (with trailing slash)'),
        make_option('--force',
                    dest='force',
                    action='store_true',
                    default=False,
                    help='Force import, ignore tipologie differences'),
    )

    logger = logging.getLogger('csvimport')
    today_str = datetime.strftime(datetime.today(), "%Y-%m-%d-%H%M")
    dump_donazioni_intprog_file = "{}/import_{}_temp.json".format(settings.LOG_PATH, today_str)
    error_logfile = "{}/import_{}_err.json".format(settings.LOG_PATH, today_str)

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
        for dip_dict in list(self.donazioni_intervento_programma):
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
            # if the donazione intervento was restored, remove it from the list,
            # so in the list we will have all the donazioni intervento that it was not possibile to re-associate
            self.donazioni_intervento_programma.remove(dip_dict)

    def handle(self, *args, **options):

        verbosity = options['verbosity']
        force = options['force']
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
        # 6. update data for user download
        ##

        path = options['path']

        tipologia_filename ="FENICE_OR_DatiBase.json"
        interventi_filename ="FENICE_OR_Interventi.json"

        tipologie_file_input = u"{}{}".format(path, tipologia_filename )
        interventi_file_input = u"{}{}".format(path, interventi_filename )

        ##
        # dump donazioni/intervento
        self.dump_donazioni_intervento()
        ##
        ##
        # Import tipologie
        ##

        self.logger.info(u"Import tipologie")
        call_command('import_tipologie', verbosity=1, file=tipologie_file_input, force=force, interactive=False)

        ##
        # Import interventi
        ##

        self.logger.info(u"Import interventi")
        call_command('import_interventi', verbosity=1, file=interventi_file_input, interactive=False)

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

        # update data for user download
        import shutil
        self.logger.info("Copy input file to folder {} for user download".format(settings.OPENDATA_ROOT))
        tipologie_file_scarico = u"{}/{}".format(settings.OPENDATA_ROOT, tipologia_filename )
        interventi_file_scarico = u"{}/{}".format(settings.OPENDATA_ROOT, interventi_filename )

        self.logger.info("scr:{},dest:{}".format(tipologie_file_input,tipologie_file_scarico))
        self.logger.info("scr:{},dest:{}".format(interventi_file_input,interventi_file_scarico))
        shutil.copyfile(tipologie_file_input, tipologie_file_scarico)
        shutil.copyfile(interventi_file_input, interventi_file_scarico)

        self.logger.info("Done")