# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand
from django.db.transaction import set_autocommit, commit
from django.template.defaultfilters import slugify
import pprint
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from open_ricostruzione.models import InterventoProgramma, Cofinanziamento, Programma, InterventoPiano, \
    Piano, Intervento, QuadroEconomicoIntervento, QuadroEconomicoProgetto, Progetto, Liquidazione, EventoContrattuale, \
    Impresa, DonazioneInterventoProgramma, Donazione, SoggettoAttuatore, TipoImmobile, Variante, UltimoAggiornamento
from territori.models import Territorio
from optparse import make_option
import logging
from datetime import datetime


class Command(BaseCommand):
    help = 'Import interventi data from JSON file'

    option_list = BaseCommand.option_list + (

        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
    )

    logger = logging.getLogger('csvimport')
    input_file = None
    encoding = 'latin-1'
    # istat_code_vari_territori = if an Intervento has this code in istat_code
    # => intervento su vari territori bool is set to true
    istat_code_vari_territori = '999999'
    date_format = '%d/%M/%Y'
    error_logfile = None
    temp_logfile = None
    donazioni_intervento_programma = None
    tipo_imm_not_found = []
    not_found_territori = {}

    def dump_don_json(self, logfile_name):
        with open(logfile_name, 'w') as outfile:
            json.dump(self.donazioni_intervento_programma, outfile, indent=4, cls=DjangoJSONEncoder)
        return

    def store_don_progr(self):
        ##
        # extract all donazioni intervento programma and stores the in memory
        ##

        self.donazioni_intervento_programma = list(
            DonazioneInterventoProgramma. \
                objects.all().order_by('intervento_programma__programma__id'). \
                values(
                'importo',
                'donazione__pk',
                'donazione__denominazione',
                'intervento_programma__programma__id',
                'intervento_programma__id_fenice',
                'intervento_programma__soggetto_attuatore__id_fenice',
                'intervento_programma__id_propr_imm',
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

    def associate_don_progr(self):
        ##
        # associates back intervento programma and donazioni to Intervento programma
        ##

        for idx, dip_dict in enumerate(self.donazioni_intervento_programma):
            iap = None
            try:
                iap = InterventoProgramma.objects.get(
                    id_fenice=dip_dict['intervento_programma__id_fenice'])
            except ObjectDoesNotExist:
                self.logger.error(
                    u"Cannot find Intervento a programma id_fenice:{} to associate with Donazione {}({})".format(
                        dip_dict['intervento_programma__id_fenice'], dip_dict['donazione__denominazione'],
                        dip_dict['donazione__pk']))
                continue
            else:
                dip = DonazioneInterventoProgramma()
                dip.donazione = Donazione.objects.get(pk=dip_dict['donazione__pk'])
                dip.importo = dip_dict['importo']
                dip.intervento_programma = iap
                dip.save()
                self.donazioni_intervento_programma.pop(idx)

    def translate_tipo_imm(self, id_tipo_imm):
        ##
        # translate tipo immobile fenice to open ricostruzione categorization.
        # if mapping is not present for the id_tipo_imm value prints error
        ##
        tipo_immobile_map = {
            '1': TipoImmobile.TIPOLOGIA.ALTRO,
            '2': TipoImmobile.TIPOLOGIA.INFRASTRUTTURE_BONIFICHE,
            '3': TipoImmobile.TIPOLOGIA.INFRASTRUTTURE_BONIFICHE,
            '4': TipoImmobile.TIPOLOGIA.OSPEDALI,
            '5': TipoImmobile.TIPOLOGIA.CIMITERI,
            '6': TipoImmobile.TIPOLOGIA.EDIFICI_STORICI,
            '7': TipoImmobile.TIPOLOGIA.IMPIANTI_SPORTIVI,
            '8': TipoImmobile.TIPOLOGIA.CHIESE,
            '9': TipoImmobile.TIPOLOGIA.ALTRO,
            '10': TipoImmobile.TIPOLOGIA.CHIESE,
            '11': TipoImmobile.TIPOLOGIA.CHIESE,
            '12': TipoImmobile.TIPOLOGIA.CHIESE,
            '13': TipoImmobile.TIPOLOGIA.SCUOLE,
            '14': TipoImmobile.TIPOLOGIA.IMPIANTI_SPORTIVI,
            '15': TipoImmobile.TIPOLOGIA.EDIFICI_STORICI,
            '16': TipoImmobile.TIPOLOGIA.ALTRO,
            '17': TipoImmobile.TIPOLOGIA.INFRASTRUTTURE_BONIFICHE,
            '18': TipoImmobile.TIPOLOGIA.ALTRO,
            '19': TipoImmobile.TIPOLOGIA.CHIESE,
            '20': TipoImmobile.TIPOLOGIA.EDIFICI_PUBBLICI,
            '21': TipoImmobile.TIPOLOGIA.INFRASTRUTTURE_BONIFICHE,
            '22': TipoImmobile.TIPOLOGIA.INFRASTRUTTURE_BONIFICHE,
            '23': TipoImmobile.TIPOLOGIA.SCUOLE,
            '24': TipoImmobile.TIPOLOGIA.IMPIANTI_SPORTIVI,
            '25': TipoImmobile.TIPOLOGIA.IMPIANTI_SPORTIVI,
            '26': TipoImmobile.TIPOLOGIA.CHIESE,
            '27': TipoImmobile.TIPOLOGIA.ALTRO,
        }

        try:
            tipo_immobile = TipoImmobile.objects.get(tipologia=tipo_immobile_map[str(id_tipo_imm)])
        except ObjectDoesNotExist:
            self.logger.critical(
                u"Cannot find mapping for id_tipo_imm '{}', mapping must be updated!".format(id_tipo_imm))
            if id_tipo_imm not in self.tipo_imm_not_found:
                self.tipo_imm_not_found.append(id_tipo_imm)
            return None

        else:
            return tipo_immobile

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
        today_str = datetime.strftime(datetime.today(), "%Y-%m-%d-%H%M")
        self.error_logfile = "{}/log/import_{}_err.json".format(settings.PROJECT_ROOT, today_str)
        self.temp_logfile = "{}/log/import_{}_temp.json".format(settings.PROJECT_ROOT, today_str)
        self.logger.info('Input file:{}'.format(self.input_file))
        data = None
        interventi_counter = 0
        vari_territori_counter = 0

        # read file
        try:
            json_file = open(self.input_file)
            data = json.load(json_file, encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file '{}'".format(self.input_file))
            exit(1)

        ##
        # dumps all DonazioneProgramma that link Donazione to InterventoProgramma so this obj are not
        # lost when the script will delete all InterventoProgramma objs.
        ##

        self.logger.info("Checking Donazioni Programma before import...")
        self.store_don_progr()
        if len(self.donazioni_intervento_programma) > 0:
            self.dump_don_json(self.temp_logfile)
            self.logger.info("Saved {} Donazioni Programma".format(len(self.donazioni_intervento_programma)))
            self.logger.info("Dumped ALL Donazioni Programma in temp file:{}".format(self.temp_logfile))
        else:
            self.logger.info("No Donazioni Programma found")

        self.logger.info("Deleting all previous InterventoProgramma and Impresa...")
        InterventoProgramma.objects.all().delete()
        Impresa.objects.all().delete()
        self.logger.info("Done")

        set_autocommit(False)
        for intervento_a_programma in data['interventi_a_programma']:

            interventi_counter += 1
            istat_comune = intervento_a_programma['comune']['cod_istat_com']
            territorio = None
            vari_territori = False

            # checks if istat_id == vari_territori, else find the territorio in the db
            if istat_comune == self.istat_code_vari_territori:
                self.logger.debug(u"Territorio found: VARI TERRITORI")
                vari_territori = True
                vari_territori_counter += 1
            else:
                try:
                    territorio = Territorio.objects.get(istat_id=istat_comune)
                except ObjectDoesNotExist:
                    self.logger.error("Territorio does not exist:{}".format(istat_comune))
                    if istat_comune not in self.not_found_territori:
                        self.not_found_territori[istat_comune] = 1
                    else:
                        self.not_found_territori[istat_comune] += 1

                    continue
                else:
                    self.logger.debug(u"Territorio found:{}".format(territorio.denominazione))

                    got_gps_data = False
                    if territorio.gps_lon is None:
                        territorio.gps_lon = intervento_a_programma['comune']['long']
                        got_gps_data = True

                    if territorio.gps_lat is None:
                        territorio.gps_lat = intervento_a_programma['comune']['lat']
                        got_gps_data = True

                    if got_gps_data:
                        territorio.save()

            int_programma = InterventoProgramma()
            # gets Programma
            programma, is_created = Programma.objects.get_or_create(
                id_fenice=intervento_a_programma['id_progr'],
            )
            if is_created:
                self.logger.warning("Created new Programma with id:{}".format(programma.id_fenice))

            # gets Soggetto Attuatore
            soggetto_att, is_created = SoggettoAttuatore.objects.get_or_create(
                id_fenice=intervento_a_programma['id_sogg_att'],
            )

            if is_created:
                self.logger.warning("Created new Soggetto Attuatore with id:{}".format(soggetto_att.id_fenice))

            int_programma.programma = programma
            int_programma.id_fenice = intervento_a_programma['id_interv_a_progr']
            int_programma.n_ordine = intervento_a_programma['n_ordine'].strip()
            int_programma.importo_generale = Decimal(intervento_a_programma['imp_gen'])
            int_programma.importo_a_programma = Decimal(intervento_a_programma['imp_a_progr'])
            int_programma.denominazione = intervento_a_programma['denominazione'].strip()
            int_programma.soggetto_attuatore = soggetto_att
            int_programma.territorio = territorio
            int_programma.vari_territori = vari_territori
            int_programma.id_categ_imm = intervento_a_programma['id_categ_imm']
            int_programma.id_propr_imm = intervento_a_programma['id_propr_imm']
            int_programma.slug = slugify(
                u"{}-{}".format(int_programma.denominazione[:45], str(int_programma.id_fenice)))
            int_programma.tipo_immobile_fenice = intervento_a_programma['id_tipo_imm']
            int_programma.tipo_immobile = self.translate_tipo_imm(intervento_a_programma['id_tipo_imm'])
            int_programma.save()
            self.logger.info(u"Import Interv.Programma:{}".format(int_programma.slug))

            # save cofinanziamenti
            for cofinanziamento in list(
                    filter(lambda x: x['importo'] > 0, intervento_a_programma['cofinanziamenti'])):
                cof = Cofinanziamento()
                cof.intervento_programma = int_programma
                cof.tipologia = cofinanziamento['id_tipo_cofin']
                cof.importo = cofinanziamento['importo']
                cof.save()

            # save interventi a piano
            for intervento_a_piano in intervento_a_programma['interventi_a_piano']:
                int_piano = InterventoPiano()
                int_piano.intervento_programma = int_programma
                int_piano.id_fenice = intervento_a_piano['id_interv_a_piano']
                int_piano.imp_a_piano = intervento_a_piano['imp_a_piano']
                # gets or create a Piano
                piano, is_created = Piano.objects.get_or_create(
                    id_fenice=intervento_a_piano['piano']['id_piano'],
                    tipologia=intervento_a_piano['piano']['id_tipo_piano']
                )
                int_piano.piano = piano
                int_piano.save()

                # save interventi
                for intervento in intervento_a_piano['interventi']:
                    intr = Intervento()
                    intr.intervento_piano = int_piano
                    intr.id_fenice = intervento['id_interv']
                    intr.is_variante = intervento['variante']

                    intr.imp_congr_spesa = Decimal(0)
                    if intervento['imp_congr_spesa']:
                        intr.imp_congr_spesa = Decimal(intervento['imp_congr_spesa'])

                    intr.denominazione = intervento['denominazione']
                    intr.tipologia = intervento['id_tipo_interv']
                    intr.stato = intervento['id_stato_interv']
                    intr.gps_lat = intervento['lat']
                    intr.gps_long = intervento['long']
                    intr.save()

                    # save quadro economico for Intervento
                    for qe_intervento in intervento['qe']:
                        QuadroEconomicoIntervento(**{
                            'id_fenice': qe_intervento['id_qe'],
                            'intervento': intr,
                            'tipologia': qe_intervento['id_tipo_qe'],
                            'importo': Decimal(qe_intervento['imp_qe']),
                        }).save()

                    #     import progetti
                    for progetto in intervento['progetti']:

                        data_deposito = None
                        data_inizio = None
                        data_fine = None
                        if progetto['iter'].get('data_dep', None):
                            data_deposito = datetime.strptime(progetto['iter']['data_dep'], self.date_format)
                        if progetto['iter'].get('data_inizio', None):
                            data_inizio = datetime.strptime(progetto['iter']['data_inizio'], self.date_format)
                        if progetto['iter'].get('data_fine', None):
                            data_fine = datetime.strptime(progetto['iter']['data_fine'], self.date_format)

                        prog = Progetto(**{
                            'id_fenice': progetto['id_prog'],
                            'intervento': intr,
                            'tipologia': progetto['id_tipo_prog'],
                            'stato': progetto['id_stato_prog'],
                            'data_deposito': data_deposito,
                            'data_inizio': data_inizio,
                            'data_fine': data_fine,
                        })
                        prog.save()
                        # save quadro economico for Progetto
                        for qe_progetto in progetto['qe']:
                            qep = QuadroEconomicoProgetto(**{
                                'id_fenice': qe_progetto['id_qe'],
                                'progetto': prog,
                                'tipologia': qe_progetto['id_tipo_qe'],
                                'importo': Decimal(qe_progetto['imp_qe']),
                            }).save()

                    #  import liquidazioni
                    for liquidazione in intervento['liquidazioni']:
                        Liquidazione(**{
                            'intervento': intr,
                            'tipologia': liquidazione['id_tipo_liq'],
                            'data': datetime.strptime(liquidazione['data_ord'], self.date_format),
                            'importo': Decimal(liquidazione['imp_ord'])
                        }).save()

                    #  Eventi contr.
                    for evento_contr in intervento['eventi_contrattuali']:
                        EventoContrattuale(**{
                            'intervento': intr,
                            'tipologia': evento_contr['id_tipo_evento_contr'],
                            'data': datetime.strptime(evento_contr['data'], self.date_format),
                        }).save()

                    #     imprese
                    for impresa in intervento['imprese']:
                        impr, _ = Impresa.objects.get_or_create(
                            partita_iva=impresa['p_iva'],
                            defaults={
                                'ragione_sociale': impresa['rag_soc']
                            }
                        )
                        intr.imprese.add(impr)


                    # varianti
                    # todo: importare eventuale qe
                    for variante in intervento['varianti']:
                        Variante(**{
                            'tipologia': variante['id_tipo_var'],
                            'stato': variante['id_stato_var'],
                            'progetto': variante['id_prog'],
                            'data_deposito': datetime.strptime(variante['iter']['data_dep'], self.date_format),
                            'data_fine': datetime.strptime(variante['iter']['data_fine'], self.date_format),
                        }).save()

        commit()

        self.logger.info("Imported {} interventi, {} of which were on ALTRI TERRITORI".format(interventi_counter,
                                                                                              vari_territori_counter))
        UltimoAggiornamento.objects.update_or_create(
            tipologia=UltimoAggiornamento.TIPOLOGIA.INTERVENTI,
            defaults={
                'data': datetime.today(),
            }
        )
        self.logger.info("Set Ultimo aggiornamento to today")

        # prints out not-found Territori
        if len(self.not_found_territori.keys()):
            for t, counter in self.not_found_territori.iteritems():
                self.logger.error(u"Cannot find territorio with istat_id:'{}' {} times".format(t, counter))

        self.logger.info("Recovering Donazioni Programma if present...")
        total_donazioni_intervento = len(self.donazioni_intervento_programma)
        self.associate_don_progr()
        not_associated_donazioni_intervento = len(self.donazioni_intervento_programma)
        associated_donazioni_intervento = total_donazioni_intervento - not_associated_donazioni_intervento
        if associated_donazioni_intervento > 0:
            self.logger.info("Correctly associated {} Donazioni Programma".format(associated_donazioni_intervento, ))
        if not_associated_donazioni_intervento > 0:
            self.logger.error(u"Could NOT ASSOCIATE {} Donazioni Programma. Dumped ONLY ERROR DATA in file {}".
            format(not_associated_donazioni_intervento, self.error_logfile))
            self.dump_don_json(self.error_logfile)

        if len(self.tipo_imm_not_found) > 0:
            for id_not_found in self.tipo_imm_not_found:
                self.logger.error(u"Cannot map id_tipo_imm:'{}', update mapping!".format(id_not_found))
        self.logger.info("Done")
        commit()
