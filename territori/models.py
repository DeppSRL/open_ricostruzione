# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings
from model_utils import Choices
from django.contrib.gis.db import models
from datetime import datetime
import struct

class TerritoriManager(models.GeoManager):
    def nazione(self):
        return Territorio.objects.get(territorio=Territorio.TERRITORIO.N)

    @property
    def regioni(self, with_nation=False):
        codes = [Territorio.TERRITORIO.R]
        if with_nation:
            codes.append(Territorio.TERRITORIO.N)
            codes.append(Territorio.TERRITORIO.E)
        return self.get_query_set().filter(territorio__in=codes)

    @property
    def provincie(self):
        return self.get_query_set().filter(territorio=Territorio.TERRITORIO.P)

    @property
    def province(self):
        return self.provincie()

    @property
    def comuni(self):
        return self.get_query_set().filter(territorio=Territorio.TERRITORIO.C)

    def get_from_istat_code(self, istat_code):
        """
        get single record from Territorio, starting from ISTAT code
        ISTAT code has the form RRRPPPCCC, where
         - RRR is the regional code, zero padded
         - PPP is the provincial code, zero padded
         - CCC is the municipal code, zero padded

        if a record in Territorio is not found, then the ObjectDoesNotExist exception is thrown
        """
        if istat_code is None:
            return None

        if len(istat_code) != 9:
            return None

        (cod_reg, cod_prov, cod_com) = struct.unpack('3s3s3s', istat_code)
        return self.get_query_set().get(cod_reg=int(cod_reg), cod_prov=int(cod_prov),
                                        cod_com=str(int(cod_prov)) + cod_com)

class Territorio(models.Model):
    TERRITORIO = Choices(
        (u'C', u'Comune'),
        (u'P', u'Provincia'),
        (u'R', u'Regione'),
        (u'N', u'Nazionale'),
        (u'E', u'Estero'),
        (u'L', u'Cluster'),
    )

    CLUSTER = Choices(
        (u'1', u"0_500", u'Fino a 500 abitanti'),
        (u'2', u"501_1000", u'Da 501 a 1.000 abitanti'),
        (u'3', u"1001_3000", u'Da 1.001 a 3.000 abitanti'),
        (u'4', u"3001_5000", u'Da 3.001 a 5.000 abitanti'),
        (u'5', u"5001_10000", u'Da 5.001 a 10.000 abitanti'),
        (u'6', u"10001_50000", u'Da 10.001 a 50.000 abitanti'),
        (u'7', u"50001_200000", u'Da 50.001 a 200.000 abitanti'),
        (u'8', u"200001_500000", u'Da 200.001 a 500.000 abitanti'),
        (u'9', u"500001_", u'Oltre i 500.000 abitanti'),
    )

    # codice Openpolis
    op_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)

    # codice Istat
    istat_id = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    prov = models.CharField(max_length=2, blank=True, null=True)
    regione = models.CharField(max_length=32, blank=True, null=True)
    denominazione = models.CharField(max_length=128, db_index=True)
    slug = models.SlugField(max_length=256, null=True, blank=True, db_index=True)
    tipologia = models.CharField(max_length=1, choices=TERRITORIO, db_index=True)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)
    cluster = models.CharField(max_length=1, choices=CLUSTER, db_index=True)
    objects = TerritoriManager()
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)


    @property
    def codice(self):
        if self.tipologia == u'C':
            return self.cod_com
        elif self.tipologia == u'P':
            return self.cod_prov
        else:
            return self.cod_reg

    def get_hierarchy(self):
        """
        returns the list of parent objects (me included)
        """
        if self.tipologia == self.TERRITORIO.R:
            return [self]
        elif self.tipologia == self.TERRITORIO.P:
            regione = Territorio.objects.regioni().get(cod_reg=self.cod_reg)
            return [regione, self]
        elif self.tipologia == self.TERRITORIO.C:
            regione = Territorio.objects.regioni().get(cod_reg=self.cod_reg)
            provincia = Territorio.objects.provincie().get(cod_prov=self.cod_prov)
            return [regione, provincia, self]
        elif self.tipologia == self.TERRITORIO.N:
            return [self]

    def get_breadcrumbs(self):
        return [(t.denominazione, t.get_absolute_url()) for t in self.get_hierarchy()]

    @property
    def nome(self):
        return u"%s" % self.denominazione

    @property
    def nome_con_provincia(self):
        if self.tipologia == self.TERRITORIO.P:
            return u"{0} (Provincia)".format(self.nome)
        else:
            return u"{0} ({1})".format(self.nome, self.prov)

    @staticmethod
    def get_province_cratere():
        return Territorio.objects.filter(tipologia=Territorio.TERRITORIO.P, denominazione__in=settings.PROVINCE_CRATERE)

    def __unicode__(self):
        return unicode(self.denominazione)

    class Meta:
        verbose_name = u'Località'
        verbose_name_plural = u'Località'
        ordering = ['denominazione']
