from django.db import models
from django.db.models import Sum, Count, Q
from django.conf import settings


class ProgrammatiQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('importo_generale'),
            "count": Count('importo_generale')
        }
        agg = self.aggregate(**aggregate_dict)
        if agg['sum'] is None:
            agg['sum'] = 0
        return agg


class ProgrammatiManager(models.Manager):
    def get_queryset(self):
        return ProgrammatiQuerySet(self.model, using=self._db)


class PianificatiQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__imp_consolidato'),
            "count": Count('interventopiano__imp_consolidato')
        }
        agg = self.aggregate(**aggregate_dict)
        if agg['sum'] is None:
            agg['sum'] = 0
        return agg


class PianificatiManager(models.Manager):
    def get_queryset(self):
        return PianificatiQuerySet(self.model, using=self._db).filter(interventopiano__isnull=False)


class AttuazioneQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__intervento__imp_consolidato'),
            "count": Count('interventopiano__intervento__imp_consolidato')
        }
        agg = self.aggregate(**aggregate_dict)
        if agg['sum'] is None:
            agg['sum'] = 0
        return agg


class AttuazioneManager(models.Manager):
    def get_queryset(self):
        return AttuazioneQuerySet(self.model, using=self._db).filter(in_attuazione=True)


class ProgettazioneManager(models.Manager):
    def get_queryset(self):
        return AttuazioneQuerySet(self.model, using=self._db). \
            filter(in_attuazione=True,
                   stato_attuazione=self.model.STATO_ATTUAZIONE.PROGETTAZIONE)


class InCorsoManager(models.Manager):
    def get_queryset(self):
        return AttuazioneQuerySet(self.model, using=self._db).\
            filter(in_attuazione=True,stato_attuazione=self.model.STATO_ATTUAZIONE.IN_CORSO)


class ConclusiManager(models.Manager):
    def get_queryset(self):
        return AttuazioneQuerySet(self.model, using=self._db).filter(in_attuazione=True,
                                                                   stato_attuazione=self.model.STATO_ATTUAZIONE.CONCLUSO)

# VARIANTI


class VariantiQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('qe__importo'),
            "count": Count('pk')
        }
        agg = self.aggregate(**aggregate_dict)
        if agg['sum'] is None:
            agg['sum'] = 0
        return agg


class VariantiManager(models.Manager):
    def get_queryset(self):
        return VariantiQuerySet(self.model, using=self._db)