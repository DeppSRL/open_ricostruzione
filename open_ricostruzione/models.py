from django.db import models



class Comune(models.Model):
    tipo_territorio = models.CharField(max_length=2)
    cod_comune = models.CharField(max_length=10)
    cod_provincia = models.CharField(max_length=3)
    denominazione = models.CharField(max_length=255)
    iban = models.CharField(max_length=30, null=True, blank=True)
    slug = models.SlugField(max_length=60)

    def __unicode__(self):
        return u"%s (%s)" % (self.denominazione, self.cod_comune)

    class Meta:
        verbose_name_plural = u'Comuni'


class Progetto(models.Model):

#- ID progetto
#- Denominazione
#- Denominazione Comune
#- Codice Istat comune di appartenenza
#- Epoca
#- Ubicazione/Indirizzo
#- Cenni storici
#- Stato attuale
#- Interventi previsti
#- Tempistica prevista
#- Importo lavori previsto
#- Ulteriori informazioni
#- Riepilogo Importi
#- Stato avanzamento lavori (testo)
#- Tipologia

    id_progetto = models.CharField(max_length=6)
    id_padre = models.CharField(max_length=6, blank=True, null=True)
    tipologia = models.SmallIntegerField()
    comune = models.ForeignKey('Comune', null=True)
    importo_previsto = models.TextField(max_length=4096)
    riepilogo_importi = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    denominazione = models.TextField(max_length=4096)
    slug = models.SlugField(max_length=60)
    parent = models.ForeignKey('Progetto', null=True)

    def __unicode__(self):
        return u"%s (ID: %s, TIPOLOGIA:%s, PADRE: %s)" % (self.denominazione, self.id, self.tipologia, self.parent_id)

    class Meta:
        verbose_name_plural = u'Progetti'

class Donazione(models.Model):
    id_donazione = models.CharField(max_length=6)
    comune = models.ForeignKey('Comune')
    denominazione = models.TextField(max_length=1000)
    tipologia = models.SmallIntegerField()
    data = models.DateField()
    avvenuto = models.BooleanField()
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    confermato = models.BooleanField()

    def __unicode__(self):
        return u"%s (ID: %s, TIPOLOGIA:%s)" % (self.denominazione, self.id, self.tipologia)

    class Meta:
        verbose_name_plural = u'Donazioni'


