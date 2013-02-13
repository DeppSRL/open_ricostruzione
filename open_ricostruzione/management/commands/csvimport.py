# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand, CommandError
from decimal import Decimal
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist
from open_ricostruzione import utils
from open_ricostruzione.models import *
from optparse import make_option
import csv
import logging
from datetime import datetime
from django.utils import timezone
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
            help='Type of import: proj|subproj|loc|don|donproj|iban'),
        make_option('--update',
                    dest='update',
                    default=False,
                    help='Update Existing Records: True|False'),
        make_option('--delete',
            dest='delete',
            default=False,
            help='Delete Existing Records: True|False'),
        )

    csv_file = ''
    encoding = 'utf8'
#    encoding='latin1'
    logger = logging.getLogger('csvimport')
    unicode_reader = None


    def handle(self, *args, **options):

        self.csv_file = options['csvfile']
        self.logger.info('CSV FILE "%s"\n' % self.csv_file )

        # read first csv file
        try:
            self.unicode_reader =\
                            utils.UnicodeDictReader(open(self.csv_file, 'r'), encoding=self.encoding, dialect="excel")
        except IOError:
            self.logger.error("It was impossible to open file %s\n" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s\n" % (self.csv_file, e.message))


        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
            UltimoAggiornamento.objects.all().update(data_progetti=timezone.now())
        elif options['type'] == 'subproj':
            self.handle_subproj(*args, **options)
            UltimoAggiornamento.objects.all().update(data_progetti=timezone.now())
        elif options['type'] == 'don':
            self.handle_donation(*args, **options)
            UltimoAggiornamento.objects.all().update(data_donazioni=timezone.now())
        elif options['type'] == 'donproj':
            self.handle_donationproj(*args, **options)
            UltimoAggiornamento.objects.all().update(data_donazioni=timezone.now())
        elif options['type'] == 'loc':
            self.handle_localita(*args, **options)
        elif options['type'] == 'iban':
            self.handle_iban(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, subproj, loc and don." % options['type'])
            exit(1)

    def handle_proj(self, *args, **options):
        c = 0

        if options['delete'].upper()=="TRUE":
            self.logger.info("Deleting Progetto table...")
            Progetto.objects.all().delete()


        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:

        #               Totale:
        #               progetto, tipologia, istat, denominazione, epoca,
        #               ubicazione, cenni storici, stato attuale, interventi previsti,
        #               tempistica prevista, importo previsto, riepilogo importi, ulteriori informazioni,
        #               data inserimento, utente, confermato, multiplo,


            updated = False

            territorio = Territorio.objects.get(cod_comune=r['istat'])

            try:
                tipologia = TipologiaProgetto.objects.get(codice=r['tipologia'])
            except ObjectDoesNotExist:
                tipologia = TipologiaProgetto.objects.get(denominazione="Altro")

            self.logger.info("%s: Analizzando record: %s" % ( r['istat'],r['id_progetto']))
            importo_previsto=r['importo_previsto'].replace('$','')
            riepilogo_importi=r['riepilogo_importi'].replace(',','.')

            progetto, created = Progetto.objects.get_or_create(
                id_progetto = r['id_progetto'],
                id_padre__isnull = True,

                defaults={
                    'id_progetto': r['id_progetto'],
                    'territorio': territorio,
                    'denominazione': strip_tags(r['denominazione']),
                    'importo_previsto': importo_previsto,
                    'riepilogo_importi': Decimal(riepilogo_importi),
                    'tipologia': tipologia,
                    'tempi_di_realizzazione' : r['tempistica_prevista'],
                    'stato_attuale': r['stato_attuale'],
                    'interventi_previsti':r['interventi_previsti'],
                    'epoca':r['epoca'],
                    'cenni_storici':r['cenni_storici'],
                    'ulteriori_info':r['ulteriori_informazioni'],
                    'slug': slugify(r['denominazione'][:50]+r['id_progetto']),
                    }
            )

            if options['update'].upper()=="TRUE":
                progetto.territorio=territorio
                progetto.importo_previsto=importo_previsto
                progetto.riepilogo_importi= Decimal(riepilogo_importi)
                progetto.tipologia = tipologia
                progetto.tempi_di_realizzazione = r['tempistica_prevista']
                progetto.stato_attuale = r['stato_attuale']
                progetto.interventi_previsti = r['interventi_previsti']
                progetto.epoca = r['epoca']
                progetto.cenni_storici = r['cenni_storici']
                progetto.ulteriori_info = r['ulteriori_informazioni']
                progetto.ubicazione = r['ubicazione']

                updated=True
                progetto.save()

            if created:
                self.logger.info("%s: progetto inserito: %s" % ( c, progetto))
            else:
                if updated:
                    self.logger.debug("%s: progetto trovato e aggiornato: %s" % (c, progetto))
                else:
                    self.logger.debug("%s: progetto trovato e non aggiornato: %s" % (c, progetto))

            c += 1

    def handle_subproj(self, *args, **options):
        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)

        for r in self.unicode_reader:
            updated=False

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

            try:
                tipologia = TipologiaProgetto.objects.get(codice=r['tipologia'])
            except ObjectDoesNotExist:
                tipologia = TipologiaProgetto.objects.get(denominazione="Altro")

            progetto, created = Progetto.objects.get_or_create(
                id_progetto = r['id_figlio'],
                id_padre = r['id_padre'],

                defaults={
                    'id_progetto': r['id_figlio'],
                    'id_padre': r['id_padre'],
                    'parent': padre,
                    'denominazione': strip_tags(r['denominazione']),
                    'importo_previsto': r['importo_previsto'],
                    'riepilogo_importi': Decimal(r['riepilogo_importi']),
                    'tipologia': tipologia,
                    'ubicazione': r['ubicazione'],
                    'tempi_di_realizzazione': r['tempistica_prevista'],
                    'stato_attuale':r['stato_attuale'],
                    'interventi_previsti':r['interventi_previsti'],
                    'epoca':r['epoca'],
                    'cenni_storici':r['cenni_storici'],
                    'ulteriori_info':r['ulteriori_informazioni'],
                    'slug':slugify(strip_tags(r['denominazione'])[:50]+r['id_figlio']),
                    }
            )

            if options['update'].upper()=="TRUE":

                progetto.tipologia = tipologia
                progetto.ubicazione = r['ubicazione']
                progetto.tempi_di_realizzazione = r['tempistica_prevista']
                progetto.stato_attuale = r['stato_attuale']
                progetto.interventi_previsti = r['interventi_previsti']
                progetto.epoca = r['epoca']
                progetto.cenni_storici = r['cenni_storici']
                progetto.ulteriori_info = r['ulteriori_informazioni']
                updated=True
                progetto.save()

            if created:
                self.logger.info("%s: progetto inserito: %s" % ( c, progetto))
            else:
                if updated:
                    self.logger.debug("%s: progetto trovato e aggiornato: %s" % (c, progetto))
                else:
                    self.logger.debug("%s: progetto trovato e non aggiornato: %s" % (c, progetto))

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
            territorio, created = Territorio.objects.get_or_create(
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
                self.logger.info("%s: localita' inserita: %s" % ( c, territorio))
            else:
                self.logger.debug("%s: localita' trovata e non duplicata: %s" % (c, territorio))

            c += 1




    def handle_donation(self, *args, **options):
        c = 0

        if options['delete'].upper()=="TRUE":
            self.logger.info("Deleting Donazione table...")
            Donazione.objects.all().delete()

        self.logger.info("Inizio import da %s" % self.csv_file)

    #    campi da importare:
    #    id_donazione = models.CharField(max_length=6)
    #    territorio = models.ForeignKey('Territorio')
    #    denominazione = models.TextField(max_length=1000)
    #    tipologia = models.SmallIntegerField()
    #    data = models.DateField()
    #    avvenuto = models.BooleanField()
    #    importo = models.FloatField()
    #    confermato = models.BooleanField()
    #    modalita_r = models.TextField(max_length=20,null=True, blank=True)
    #    info = models.TextField(max_length=1000,null=True, blank=True)

    #    campi CSV:
    #    "id_flusso";"istat";"tipologia_c";"denominazione";"istat_c";"data_c";"modalita_c";"avvenuto";
    #   "indicazione";"importo";"modalita_r";"modalita_v";"info";"data_inserimento";"confermato";"utente"

        for r in self.unicode_reader:
            created = False
            donazione = None
            updated = False

            territorio = Territorio.objects.get(cod_comune=r['istat'])

        #se non c'e' la data usa il ts di inserimento della donazione

            if r['data_c']and r['data_c']!="0000-00-00":
                data = datetime.strptime(r['data_c'], "%Y-%m-%d")
            else:
                data = datetime.fromtimestamp(float(r['data_inserimento']))

            r['importo'] = r['importo'].replace(',','.')

            #se la tipologia e' srl, spa o Altre aziende inserisce come tipologia Aziende,
            # viceversa la tipologia riportata
            aziende=TipologiaCedente.objects.get(denominazione="Aziende")

            if r['tipologia_c'] == 4 or r['tipologia_c'] == 5 or r['tipologia_c'] == 11:
                tipologia_cedente = aziende
            else:
                try:
                    tipologia_cedente = TipologiaCedente.objects.get(codice = r['tipologia_c'])
                except ObjectDoesNotExist:
                    tipologia_cedente = TipologiaCedente.objects.get(denominazione="Altro")

            donazione, created = Donazione.objects.get_or_create(
                id_donazione = r['id_flusso'],

                defaults={
                    'id_donazione': r['id_flusso'],
                    'territorio': territorio,
                    'denominazione': r['denominazione'],
                    'tipologia': tipologia_cedente,
                    'data': data,
                    'avvenuto': r['avvenuto'],
                    'importo': Decimal(r['importo']),
                    'confermato': r['confermato'],
                    'info': r['info'],
                    'modalita_r':r['modalita_r'],
                    }
            )

            if created == False and donazione and options['update'].upper()=="TRUE":
                donazione.territorio = territorio
                donazione.denominazione = r['denominazione']
                donazione.tipologia = tipologia_cedente
                donazione.data = data
                donazione.avvenuto = r['avvenuto']
                donazione.importo = Decimal(r['importo'])
                donazione.confermato = r['confermato']
                donazione.info = r['info']
                donazione.modalita_r=r['modalita_r']
                updated=True
                donazione.save()

            if created:
                self.logger.info("%s: donazione inserita: %s" % ( c, donazione))
            else:
                if donazione:
                    if options['update'].upper()=="TRUE" and updated:
                        self.logger.debug("%s: donazione aggiornata: %s" % (c, donazione))
                    else:
                        self.logger.debug("%s: donazione trovata e non aggiornata: %s" % (c, donazione))
                else:
                    self.logger.debug("%s: donazione non trovata: %s" % (c, r['id_flusso']))

            c += 1

#    import relationship between donation for projects
    def handle_donationproj(self, *args, **options):
        c = 0
        self.logger.info("Inizio import da %s" % self.csv_file)

        #    campi da importare:
        #   "id";"id_flusso";"id_progetto";"id_figlio"

        for r in self.unicode_reader:
            donazione = Donazione.objects.get(id_donazione=r['id_flusso'])
            if donazione:
                if options['update'].upper()=="TRUE":
                    if r['id_figlio'] == "NULL" or not r['id_figlio']:
                        donazione.progetto=\
                            Progetto.objects.\
                            get(id_progetto=r['id_progetto'],parent__isnull=True, id_padre__isnull=True)
                    else:
                        donazione.progetto=\
                            Progetto.objects.\
                            get(id_padre=r['id_progetto'], id_progetto=r['id_figlio'])

                    donazione.save()

                    self.logger.info("%s: donazione aggiornata: %s" % ( c, donazione))
                else:
                    self.logger.info("%s: donazione non aggiornata: %s" % ( c, donazione))
            else:
                self.logger.debug("%s: donazione non trovata: %s" % (c, r['id_progetto']))

            c += 1


#    import Territorio IBAN
    def handle_iban(self, *args, **options):
        c = 0

        self.logger.info("Inizio import da %s" % self.csv_file)

        #   campi da importare:
        #   "id_iban";"istat";"descrizione";"riferimento";"informazioni";"data"

        for r in self.unicode_reader:
            comune=Territorio.objects.get(cod_comune=r['istat'],tipo_territorio="C")
            if comune:
                if options['update'].upper()=="TRUE":
                    comune.iban = r['riferimento']
                    if "postale" in r['descrizione']:
                        comune.tipologia_cc="P"
                    elif "bancario" in r['descrizione']:
                        comune.tipologia_cc="B"

                    comune.save()
                    self.logger.info("%s: dati Comune aggiornati: %s" % ( c, comune))

                else:
                    self.logger.info("%s: dati Comune non aggiornati: %s" % ( c, comune))
            else:
                self.logger.debug("%s: Comune non trovato: %s" % (c, comune))

            c += 1