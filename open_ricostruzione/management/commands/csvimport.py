# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand, CommandError
from decimal import Decimal
from django.template.defaultfilters import slugify

from open_ricostruzione import utils
from open_ricostruzione.models import *
from optparse import make_option
import csv
import logging
import time
from datetime import datetime
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Command(BaseCommand):

    help = 'Import data from CSV'

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
            dest='csvfile',
            default='./progetti.csv',
            help='Select csv file'),
        make_option('--type',
            dest='type',
            default=None,
            help='Type of import: proj|subproj|loc|don'),
        )
    csv_file = ''
    encoding = 'utf8'
    logger = logging.getLogger('csvimport')
    unicode_reader = None


    def handle(self, *args, **options):

        self.csv_file = options['csvfile']
        self.logger.info('CSV FILE "%s"\n' % self.csv_file )

        # read first csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), encoding=self.encoding, dialect='excel_semicolon')
        except IOError:
            self.logger.error("It was impossible to open file %s\n" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s\n" % (self.csv_file, e.message))


        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
        elif options['type'] == 'subproj':
            self.handle_subproj(*args, **options)
        elif options['type'] == 'don':
            self.handle_donation(*args, **options)
        elif options['type'] == 'loc':
            self.handle_localita(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, subproj, loc and don." % options['type'])
            exit(1)

    def handle_proj(self, *args, **options):
        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:

        #               Totale:
        #               progetto, tipologia, istat, denominazione, epoca,
        #               ubicazione, cenni storici, stato attuale, interventi previsti,
        #               tempistica prevista, importo previsto, riepilogo importi, ulteriori informazioni,
        #               data inserimento, utente, confermato, multiplo,

            created = False
            comune = Comune.objects.get(cod_comune=r['istat'])
            self.logger.info("%s: Analizzando record: %s" % ( r['istat'],r['id_progetto']))
            importo_previsto=r['importo_previsto'].replace('$','')
            riepilogo_importi=r['riepilogo_importi'].replace(',','.')
            progetto, created = Progetto.objects.get_or_create(
                id_progetto = r['id_progetto'],
                id_padre__isnull = True,

                defaults={
                    'id_progetto': r['id_progetto'],
                    'tipologia': r['tipologia'],
                    'comune': comune,
                    'denominazione': strip_tags(r['denominazione']),
                    'importo_previsto': importo_previsto,
                    'riepilogo_importi': Decimal(riepilogo_importi),
                    }
            )

            if created:
                self.logger.info("%s: progetto inserito: %s" % ( c, progetto))
            else:
                self.logger.debug("%s: progetto trovato e non duplicato: %s" % (c, progetto))

#           aggiunge ubicazione, tempi di realizzazione, stato attuale, tempistica, interventi previsti
            progetto.ubicazione = r['ubicazione']
            progetto.ubicazione = r['tempistica_prevista']
            progetto.ubicazione = r['ubicazione']
            progetto.ubicazione = r['ubicazione']
            progetto.ubicazione = r['ubicazione']

#           aggiunge lo slug
            myslug = progetto.denominazione[:50] + progetto.id_progetto
            progetto.slug = slugify(myslug)
            progetto.save()

            c += 1

    def handle_subproj(self, *args, **options):
        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:

        #Totale:
        #id_figlio	id_padre	tipologia	denominazione	epoca	ubicazione	cenni_storici	stato_attuale	interventi_previsti	tempistica_prevista	importo_previsto	riepilogo_importi	ulteriori_informazioni	data_inserimento	utente	confermato
        #Attualmente importo: id_figlio	id_padre	tipologia	denominazione, stato_attuale	interventi_previsti	tempistica_prevista, importo_previsto	riepilogo_importi,

            created = False

            self.logger.info("Analizzando record:id_padre %s id_figlio %s" % ( r['id_padre'],r['id_figlio']))
            r['importo_previsto']=r['importo_previsto'].replace('$','')
            r['riepilogo_importi']=r['riepilogo_importi'].replace(',','.')
            try:
                padre = Progetto.objects.get(id_progetto=r['id_padre'])
            except ObjectDoesNotExist:
                self.logger.info("Record padre con id: %s non esiste" % ( r['id_padre']))
                continue

            progetto, created = Progetto.objects.get_or_create(
                id_progetto = r['id_figlio'],
                id_padre = r['id_padre'],

                defaults={
                    'id_progetto': r['id_figlio'],
                    'id_padre': r['id_padre'],
                    'parent': padre,
                    'tipologia': r['tipologia'],
                    'denominazione': strip_tags(r['denominazione']),
                    'importo_previsto': r['importo_previsto'],
                    'riepilogo_importi': Decimal(r['riepilogo_importi']),
                    }
            )

            if created:
                self.logger.info("%s: progetto inserito: %s" % ( c, progetto))
            else:
                self.logger.debug("%s: progetto trovato e non duplicato: %s" % (c, progetto))

            myslug = progetto.denominazione[:50] + progetto.id_progetto
            progetto.slug = slugify(myslug)
            progetto.save()

            c += 1



    def handle_localita(self, *args, **options):
        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:

#           campi da importare:territorio, cod_reg,cod_prov, cod_com, denominazione, slug
            codice_istat = r['cod_com']
            if r['territorio'] == 'C':
                codice_istat = "0" + codice_istat

            created = False
            comune, created = Comune.objects.get_or_create(
                cod_comune = codice_istat,
                denominazione = r['denominazione'],
                defaults={
                    'tipo_territorio': r['territorio'],
                    'cod_provincia': r['cod_prov'],
                    'cod_comune': codice_istat,
                    'denominazione': r['denominazione'],
                    'slug': r['slug'],
                }
            )

            if created:
                self.logger.info("%s: localita' inserita: %s" % ( c, comune))
            else:
                self.logger.debug("%s: localita' trovata e non duplicata: %s" % (c, comune))

            c += 1




    def handle_donation(self, *args, **options):
        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)

    #    campi da importare:
    #    id_donazione = models.CharField(max_length=6)
    #    comune = models.ForeignKey('Comune')
    #    denominazione = models.TextField(max_length=1000)
    #    tipologia = models.SmallIntegerField()
    #    data = models.DateField()
    #    avvenuto = models.BooleanField()
    #    importo = models.FloatField()
    #    confermato = models.BooleanField()

        for r in self.unicode_reader:
            created = False

            comune = Comune.objects.get(cod_comune=r['istat'])
            data = datetime.strptime(r['data_c'], "%d/%m/%Y")
            r['importo'] = r['importo'].replace(',','.')

            donazione, created = Donazione.objects.get_or_create(
                id_donazione = r['id_flusso'],

                defaults={
                    'id_donazione': r['id_flusso'],
                    'comune': comune,
                    'denominazione': r['denominazione'],
                    'tipologia': r['tipologia_c'],
                    'data': data,
                    'avvenuto': r['avvenuto'],
                    'importo': Decimal(r['importo']),
                    'confermato': r['confermato'],
                    }
            )

            if created:
                self.logger.info("%s: donazione inserita: %s" % ( c, donazione))
            else:
                self.logger.debug("%s: donazione trovata e non duplicata: %s" % (c, donazione))

            c += 1
