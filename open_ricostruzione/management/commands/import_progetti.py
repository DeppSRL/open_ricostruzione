# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import set_autocommit, commit
from django.template.defaultfilters import slugify
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
import xlrd
from open_ricostruzione.models import InterventoProgramma, Cofinanziamento, Programma, InterventoPiano, \
    Piano, Intervento, QuadroEconomicoIntervento, QuadroEconomicoProgetto, Progetto, Liquidazione, EventoContrattuale, Impresa
from territori.models import Territorio
from optparse import make_option
import logging
from datetime import datetime


class Command(BaseCommand):
    help = 'Import progetti data from JSON file'

    option_list = BaseCommand.option_list + (
        make_option('--file',
                    dest='file',
                    default='',
                    help='Path to file'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    default=True,
                    help='Delete Existing Records'),

    )

    input_file = None
    delete = False
    encoding = 'latin-1'
    logger = logging.getLogger('csvimport')
    date_format = '%d/%M/%Y'
    unicode_reader = None

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
        self.logger.info('Input file:{}'.format(self.input_file))
        data = None
        not_found_istat = []
        # read file
        try:
            json_file = open(self.input_file)
            data = json.load(json_file, encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file {}".format(self.input_file))
            exit(1)

        if self.delete:
            self.logger.info("Deleting all previous records...")
            InterventoProgramma.objects.all().delete()
            self.logger.info("Done")

        set_autocommit(False)
        for intervento_a_programma in data['interventi_a_programma']:
            istat_comune = intervento_a_programma['comune']['cod_istat_com']
            try:
                territorio = Territorio.objects.get(istat_id=istat_comune)
            except ObjectDoesNotExist:
                self.logger.error("Territorio does not exist:{}".format(istat_comune))
                if istat_comune not in not_found_istat:
                    not_found_istat.append(istat_comune)
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
                programma, is_created = Programma.objects.get_or_create(
                    id_progr=intervento_a_programma['id_progr'],
                )
                int_programma.programma = programma
                int_programma.id_interv_a_progr = intervento_a_programma['id_interv_a_progr']
                int_programma.n_ordine = intervento_a_programma['n_ordine'].strip()
                int_programma.importo_generale = Decimal(intervento_a_programma['imp_gen'])
                int_programma.importo_a_programma = Decimal(intervento_a_programma['imp_a_progr'])
                int_programma.denominazione = intervento_a_programma['denominazione'].strip()
                int_programma.id_sogg_att = intervento_a_programma['id_sogg_att']
                int_programma.territorio = territorio
                int_programma.id_tipo_imm = intervento_a_programma['id_tipo_imm']
                int_programma.id_categ_imm = intervento_a_programma['id_categ_imm']
                int_programma.id_propr_imm = intervento_a_programma['id_propr_imm']
                int_programma.slug = slugify(
                    u"{}-{}".format(int_programma.denominazione[:45], str(int_programma.id_interv_a_progr)))
                int_programma.tipo_immobile = intervento_a_programma['id_tipo_imm']
                int_programma.save()
                self.logger.info(u"Import IAP:{}".format(int_programma.slug))

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
                    int_piano.id_interv_a_piano = intervento_a_piano['id_interv_a_piano']
                    int_piano.imp_a_piano = intervento_a_piano['imp_a_piano']
                    # gets or create a Piano
                    piano, is_created = Piano.objects.get_or_create(
                        id_piano=intervento_a_piano['piano']['id_piano'],
                        tipologia=intervento_a_piano['piano']['id_tipo_piano']
                    )
                    int_piano.piano = piano
                    int_piano.save()

                    # save interventi
                    for intervento in intervento_a_piano['interventi']:
                        intr = Intervento()
                        intr.intervento_piano = int_piano
                        intr.id_interv = intervento['id_interv']
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
                                'intervento': intr,
                                'tipologia': qe_intervento['id_tipo_qe'],
                                'importo': Decimal(qe_intervento['imp_qe']),
                            }).save()

                        #     import progetti
                        for progetto in intervento['progetti']:
                            prog = Progetto(**{
                                'intervento': intr,
                                'tipologia': progetto['id_tipo_prog'],
                                'stato_progetto': progetto['id_stato_prog'],
                                'data_deposito': datetime.strptime(progetto['data_dep'], self.date_format)
                            })
                            prog.save()
                            # save quadro economico for Progetto
                            for qe_progetto in progetto['qe']:
                                qep = QuadroEconomicoProgetto(**{
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
                            impr = Impresa(**{
                                'ragione_sociale': impresa['rag_soc'],
                                'partita_iva': impresa['p_iva']
                            })
                            impr.save()
                            intr.imprese.add(impr)
        commit()