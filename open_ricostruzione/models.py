from decimal import Decimal
from model_utils import Choices
import time
from django.db import models
from django.conf import settings
from open_ricostruzione.utils.moneydate import moneyfmt, add_months
from territori.models import Territorio


class InterventiAProgramma(models.Model):
    territorio = models.ForeignKey('territori.Territorio', null=True)
    importo_previsto = models.TextField(max_length=4096)
    denominazione = models.TextField(max_length=4096)
    slug = models.SlugField(max_length=60)

    def __unicode__(self):
        return u"{}".format(self.denominazione)

    class Meta:
        verbose_name_plural = u'Interventi a programma'


class Donazione(models.Model):
    TIPO_DONAZIONE = Choices(
        (u'1', u'Diretta', u'Diretta'),
        (u'2', u'Regione', u'Regione'),
    )

    TIPO_CEDENTE = Choices(
        (u'0', u'privato', u'privato'),
    )

    territorio = models.ForeignKey('territori.Territorio')
    denominazione = models.CharField(max_length=256)
    informazioni = models.TextField(max_length=800, blank=True, null=True, default=None)
    tipologia_cedente = models.CharField(max_length=2, choices=TIPO_CEDENTE, blank=False, null=False, default='')
    tipologia_donazione = models.CharField(max_length=2, choices=TIPO_DONAZIONE, blank=False, null=False, default='')
    data = models.DateField(null=True, blank=True)
    importo = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, blank=False, null=False, )

    def __unicode__(self):
        return "{}".format(self.denominazione)

    #    ritorna l'importo lavori in formato italiano
    def get_importo_ita(self):
        return moneyfmt(self.importo, 2, "", ".", ",")

    class Meta:
        verbose_name_plural = u'Donazioni'
