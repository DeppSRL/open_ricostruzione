# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand
from django.db.transaction import set_autocommit, commit
from django.template.defaultfilters import slugify
from pprint import pprint
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from open_ricostruzione.models import InterventoProgramma, Cofinanziamento, Programma, InterventoPiano, \
    Piano, Intervento, QuadroEconomicoIntervento, QuadroEconomicoProgetto, Progetto, Liquidazione, EventoContrattuale, \
    Impresa, SoggettoAttuatore, TipoImmobile, Variante, UltimoAggiornamento, ProprietarioImmobile
from territori.models import Territorio
from optparse import make_option
import logging
from datetime import datetime


class Command(BaseCommand):
    help = 'Import interventi data from JSON file: delete all data and import'

    option_list = BaseCommand.option_list + (

        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
    )

    logger = logging.getLogger('csvimport')
    input_file = None
    encoding = 'utf-8'
    # istat_code_vari_territori = if an Intervento has this code in istat_code
    # => intervento su vari territori bool is set to true
    istat_code_vari_territori = '999999'
    date_format = '%d/%m/%Y'
    tipo_imm_not_found = []
    not_found_territori = {}

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

    def get_intervento_stato(self, intervento_programma):
        # determines the general status and attuazione status for the interv_programma based on its relationships
        a_piano = False
        in_attuazione = False
        stato = InterventoProgramma.STATO.PROGRAMMA
        stato_attuazione = None

        interventi_piano = InterventoPiano.objects.filter(intervento_programma=intervento_programma)
        interventi = Intervento.objects.filter(intervento_piano__in=interventi_piano)

        if len(interventi_piano) > 0:
            a_piano = True
            stato = InterventoProgramma.STATO.PIANO

            if len(interventi) > 0:

                if len(interventi) > 1:
                    self.logger.warning("Intervento programma:'{}' have {} interventi, only the 1st is considered!".format(intervento_programma.slug, len(interventi)))

                in_attuazione = True
                stato = InterventoProgramma.STATO.ATTUAZIONE
                # todo: qua si considera lo stato del primo intervento, quando aggiorneremo la logica andra' cambiato questo passaggio
                intervento_stato = interventi.values_list('stato', flat=True)[0]
                if intervento_stato in settings.STATI_PROGETTAZIONE:
                    stato_attuazione = InterventoProgramma.STATO_ATTUAZIONE.PROGETTAZIONE
                elif intervento_stato in settings.STATI_IN_CORSO:
                    stato_attuazione = InterventoProgramma.STATO_ATTUAZIONE.IN_CORSO
                elif intervento_stato in settings.STATI_CONCLUSI:
                    stato_attuazione = InterventoProgramma.STATO_ATTUAZIONE.CONCLUSO
                else:
                    self.logger.error(u"Stato attuazione not accepted")

        return stato, a_piano, in_attuazione, stato_attuazione

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

        self.logger.info("Deleting all previous InterventoProgramma and Impresa...")
        InterventoProgramma.objects.all().delete()
        Impresa.objects.all().delete()
        Variante.objects.all().delete()
        self.logger.info("Done")
        set_autocommit(False)
        for intervento_a_progr_json in data['interventi_a_programma']:

            interventi_counter += 1
            istat_comune = intervento_a_progr_json['comune']['cod_istat_com']
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

                    got_gps_data = False
                    if territorio.gps_lon is None:
                        territorio.gps_lon = intervento_a_progr_json['comune']['long']
                        got_gps_data = True

                    if territorio.gps_lat is None:
                        territorio.gps_lat = intervento_a_progr_json['comune']['lat']
                        got_gps_data = True

                    if got_gps_data:
                        territorio.save()

            intervento_programma = InterventoProgramma()
            # gets Programma
            programma, is_created = Programma.objects.get_or_create(
                id_fenice=intervento_a_progr_json['id_progr'],
            )
            if is_created:
                self.logger.warning("Created new Programma with id:{}".format(programma.id_fenice))

            # gets Soggetto Attuatore
            soggetto_att, is_created = SoggettoAttuatore.objects.get_or_create(
                id_fenice=intervento_a_progr_json['id_sogg_att'],
            )

            if is_created:
                self.logger.warning("Created new Soggetto Attuatore with id:{}".format(soggetto_att.id_fenice))

            intervento_programma.programma = programma
            intervento_programma.id_fenice = intervento_a_progr_json['id_interv_a_progr']
            intervento_programma.n_ordine = intervento_a_progr_json['n_ordine'].strip()
            intervento_programma.importo_generale = Decimal(intervento_a_progr_json['imp_gen'])
            intervento_programma.importo_a_programma = Decimal(intervento_a_progr_json['imp_a_progr'])
            intervento_programma.denominazione = intervento_a_progr_json['denominazione'].strip()
            intervento_programma.soggetto_attuatore = soggetto_att
            intervento_programma.territorio = territorio
            intervento_programma.vari_territori = vari_territori
            intervento_programma.id_categ_imm = intervento_a_progr_json['id_categ_imm']
            try:
                propr_immobile = ProprietarioImmobile.objects.get(id_fenice=intervento_a_progr_json['id_propr_imm'] )
            except ObjectDoesNotExist:
                self.logger.error("Int.Programma with id_fenice:{}, cannot find propr.immobile for id:{}".format(intervento_programma.id_fenice, intervento_a_progr_json['id_propr_imm']))
            else:
                intervento_programma.propr_immobile = propr_immobile

            intervento_programma.slug = slugify(
                u"{}-{}".format(intervento_programma.denominazione[:45], str(intervento_programma.id_fenice)))
            intervento_programma.tipo_immobile_fenice = intervento_a_progr_json['id_tipo_imm']
            intervento_programma.tipo_immobile = self.translate_tipo_imm(intervento_a_progr_json['id_tipo_imm'])
            intervento_programma.save()
            self.logger.debug(u"Import Interv.Programma:{}".format(intervento_programma.slug))

            # calculate importo cofinanziamente as difference between imp. generale and imp.programma
            importo_cofinanziamenti = intervento_programma.importo_generale - intervento_programma.importo_a_programma

            # save cofinanziamenti
            for cofinanziamento in list(
                    filter(lambda x: x['importo'] > 0, intervento_a_progr_json['cofinanziamenti'])):
                cof = Cofinanziamento()
                cof.intervento_programma = intervento_programma
                cof.tipologia = cofinanziamento['id_tipo_cofin']
                cof.importo = cofinanziamento['importo']
                cof.save()

            # save interventi a piano
            for intervento_piano_json in intervento_a_progr_json['interventi_a_piano']:
                intervento_piano = InterventoPiano()
                intervento_piano.intervento_programma = intervento_programma
                intervento_piano.id_fenice = intervento_piano_json['id_interv_a_piano']
                intervento_piano.imp_a_piano = intervento_piano_json['imp_a_piano']
                # NOTE: this works only if there is only ONE intervento piano
                # and ONE intervento for intervento programma
                intervento_piano.imp_consolidato = Decimal(intervento_piano.imp_a_piano) + importo_cofinanziamenti
                # gets or create a Piano
                piano, is_created = Piano.objects.get_or_create(
                    id_fenice=intervento_piano_json['piano']['id_piano'],
                    tipologia=intervento_piano_json['piano']['id_tipo_piano']
                )
                intervento_piano.piano = piano
                intervento_piano.save()

                # save interventi
                for intervento_json in intervento_piano_json['interventi']:
                    intervento = Intervento()
                    intervento.intervento_piano = intervento_piano
                    intervento.id_fenice = intervento_json['id_interv']
                    intervento.is_variante = intervento_json['variante']

                    intervento.imp_congr_spesa = Decimal(0)
                    intervento.imp_consolidato = Decimal(0)
                    if intervento_json['imp_congr_spesa']:
                        intervento.imp_congr_spesa = Decimal(intervento_json['imp_congr_spesa'])
                        # NOTE: this works only if there is only ONE intervento piano
                        # and ONE intervento for intervento programma
                        intervento.imp_consolidato = intervento.imp_congr_spesa + importo_cofinanziamenti
                    else:
                        self.logger.warning(u"Intervento programma:'{}' in ATTUAZIONE but Intervento['imp_congr_spesa'] = NULL, use Importo a piano".format(intervento_programma.slug))
                        intervento.imp_consolidato = intervento_piano.imp_consolidato

                    intervento.denominazione = intervento_json['denominazione']
                    intervento.tipologia = intervento_json['id_tipo_interv']
                    intervento.stato = intervento_json['id_stato_interv']
                    intervento.gps_lat = intervento_json['lat']
                    intervento.gps_long = intervento_json['long']
                    intervento.save()

                    # save quadro economico for Intervento
                    for qe_intervento in intervento_json['qe']:
                        QuadroEconomicoIntervento.objects.create(**{
                            'id_fenice': qe_intervento['id_qe'],
                            'intervento': intervento,
                            'tipologia': qe_intervento['id_tipo_qe'],
                            'importo': Decimal(qe_intervento['imp_qe']),
                        })


                    #     import progetti
                    for progetto_json in intervento_json['progetti']:

                        data_deposito = None
                        data_inizio = None
                        data_fine = None
                        if progetto_json['iter'].get('data_dep', None):
                            data_deposito = datetime.strptime(progetto_json['iter']['data_dep'], self.date_format)
                        if progetto_json['iter'].get('data_inizio', None):
                            data_inizio = datetime.strptime(progetto_json['iter']['data_inizio'], self.date_format)
                        if progetto_json['iter'].get('data_fine', None):
                            data_fine = datetime.strptime(progetto_json['iter']['data_fine'], self.date_format)

                        progetto = Progetto(**{
                            'id_fenice': progetto_json['id_prog'],
                            'intervento': intervento,
                            'tipologia': progetto_json['id_tipo_prog'],
                            'stato': progetto_json['id_stato_prog'],
                            'data_deposito': data_deposito,
                            'data_inizio': data_inizio,
                            'data_fine': data_fine,
                        })
                        progetto.save()
                        # save quadro economico for Progetto
                        for qe_progetto_json in progetto_json['qe']:
                            qep = QuadroEconomicoProgetto(**{
                                'id_fenice': qe_progetto_json['id_qe'],
                                'progetto': progetto,
                                'tipologia': qe_progetto_json['id_tipo_qe'],
                                'importo': Decimal(qe_progetto_json['imp_qe']),
                            }).save()


                    #  import liquidazioni
                    for liquidazione in intervento_json['liquidazioni']:
                        data_ord = None
                        if liquidazione['data_ord']:
                            data_ord = datetime.strptime(liquidazione['data_ord'], self.date_format)
                        Liquidazione(**{
                            'intervento': intervento,
                            'tipologia': liquidazione['id_tipo_liq'].strip(),
                            'data': data_ord,
                            'importo': Decimal(liquidazione['imp_ord'])
                        }).save()

                    #  Eventi contr.
                    for evento_contr in intervento_json['eventi_contrattuali']:
                        EventoContrattuale(**{
                            'intervento': intervento,
                            'tipologia': evento_contr['id_tipo_evento_contr'],
                            'data': datetime.strptime(evento_contr['data'], self.date_format),
                        }).save()

                    # imprese
                    for impresa_json in intervento_json['imprese']:
                        impresa, _ = Impresa.objects.get_or_create(
                            partita_iva=impresa_json['p_iva'],
                            defaults={
                                'ragione_sociale': impresa_json['rag_soc'],
                                'slug': slugify(u"{}-{}".format(impresa_json['rag_soc'][:45], impresa_json['p_iva']))
                            }
                        )
                        intervento.imprese.add(impresa)

                    # varianti
                    for variante in intervento_json['varianti']:
                        progetto_variante = None
                        qev = None
                        if variante['id_prog']:
                            try:
                                progetto_variante = Progetto.objects.get(id_fenice=variante['id_prog'])
                            except ObjectDoesNotExist:
                                self.logger.error(
                                    "Intervento with id_fenice:{}, Variante: id_prog:{} does not exist in db".format(
                                        intervento.id_fenice, variante['id_prog']))

                        # import Quadro economico
                        if variante['id_qe']:
                            try:
                                qev = QuadroEconomicoIntervento.objects.get(id_fenice=variante['id_qe'])

                                variante_data_deposito = None
                                if variante['iter']['data_dep']:
                                    variante_data_deposito = datetime.strptime(variante['iter']['data_dep'], self.date_format)

                                variante_data_fine = None
                                if variante['iter']['data_fine']:
                                    variante_data_fine = datetime.strptime(variante['iter']['data_fine'], self.date_format)

                                Variante(**{
                                    'qe': qev,
                                    'tipologia': variante['id_tipo_var'],
                                    'stato': variante['id_stato_var'],
                                    'intervento': intervento,
                                    'progetto': progetto_variante,
                                    'data_deposito': variante_data_deposito,
                                    'data_fine': variante_data_fine
                                }).save()


                            except ObjectDoesNotExist:
                                self.logger.warning(
                                    "Intervento with id_fenice:{}, Variante: id_qe:{} does not exist in db, cannot import QE for Variante".format(
                                        intervento.id_fenice, variante['id_qe']))

            # set state and attuazione state for the considered intervento_programma
            intervento_programma.stato, intervento_programma.a_piano, intervento_programma.in_attuazione, intervento_programma.stato_attuazione = \
                self.get_intervento_stato(intervento_programma)
            intervento_programma.save()

        commit()
        set_autocommit(True)
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

        if len(self.tipo_imm_not_found) > 0:
            for id_not_found in self.tipo_imm_not_found:
                self.logger.error(u"Cannot map id_tipo_imm:'{}', update mapping!".format(id_not_found))
        self.logger.info("Done")
