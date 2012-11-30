from django.db import models



class Territorio(models.Model):

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

    def get_comuni_with_progetti(self):
        return Territorio.objects.filter(tipo_territorio="C", cod_provincia = self.cod_provincia).\
                filter(progetto__isnull = False).\
                order_by("denominazione").distinct()

    def get_provincia(self):
        if self.tipo_territorio != "P":
            return Territorio.objects.get(tipo_territorio="P", cod_provincia = self.cod_provincia)
        else:
            return None

class TipologiaProgetto(models.Model):
    codice = models.SmallIntegerField(null=True, blank=True)
    denominazione = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s - %s" % (self.codice, self.denominazione)

    class Meta:
        verbose_name_plural = u'Tipologia Progetti'

class Progetto(models.Model):

    id_progetto = models.CharField(max_length=6)
    id_padre = models.CharField(max_length=6, blank=True, null=True)
    tipologia = models.SmallIntegerField()
    territorio = models.ForeignKey('Territorio', null=True)
    importo_previsto = models.TextField(max_length=4096)
    riepilogo_importi = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    denominazione = models.TextField(max_length=4096)
    slug = models.SlugField(max_length=60)
    parent = models.ForeignKey('Progetto', null=True)
    ubicazione = models.CharField(max_length=500)
    tempi_di_realizzazione = models.TextField()
    stato_attuale = models.TextField()
    interventi_previsti = models.TextField()
    epoca = models.TextField()
    cenni_storici = models.TextField()
    ulteriori_info = models.TextField()

    def __unicode__(self):
        return u"%s (ID: %s, TIPOLOGIA:%s, PADRE: %s)" % (self.denominazione, self.id_progetto, self.tipologia, self.parent_id)

    class Meta:
        verbose_name_plural = u'Progetti'


class TipologiaCedente(models.Model):
    codice = models.SmallIntegerField(null=True, blank=True)
    denominazione = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s - %s" % (self.codice, self.denominazione)

    class Meta:
        verbose_name_plural = u'Tipologia Cedenti'


class Donazione(models.Model):

    id_donazione = models.CharField(max_length=6)
    territorio = models.ForeignKey('Territorio')
    denominazione = models.TextField(max_length=1000)
    tipologia = models.ForeignKey('TipologiaCedente')
    data = models.DateField()
    avvenuto = models.BooleanField()
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, null=True, blank=True)
    confermato = models.BooleanField()

    def __unicode__(self):
        return u"%s (ID: %s, Data:%s)" % (self.denominazione, self.id, self.data)

    class Meta:
        verbose_name_plural = u'Donazioni'

