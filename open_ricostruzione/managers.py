from django.db import models
from django.db.models import Sum, Count


class ProgrammatiQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('importo_generale'),
            "count": Count('importo_generale')
        }
        return self.aggregate(**aggregate_dict)


class ProgrammatiManager(models.Manager):
    def get_queryset(self):
        return ProgrammatiQuerySet(self.model, using=self._db)


class PianificatiQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__imp_a_piano'),
            "count": Count('interventopiano__imp_a_piano')
        }
        return self.aggregate(**aggregate_dict)


class PianificatiManager(models.Manager):
    def get_queryset(self):
        return PianificatiQuerySet(self.model, using=self._db).filter(interventopiano__isnull=False)


class AttuazioneQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__intervento__imp_congr_spesa'),
            "count": Count('interventopiano__intervento__imp_congr_spesa')
        }
        return self.aggregate(**aggregate_dict)


class AttuazioneManager(models.Manager):
    def get_queryset(self):
        return AttuazioneQuerySet(self.model, using=self._db).filter(interventopiano__intervento__isnull=False)


class ProgettazioneQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__intervento__imp_congr_spesa'),
            "count": Count('interventopiano__intervento__imp_congr_spesa')
        }
        return self.aggregate(**aggregate_dict)


class ProgettazioneManager(models.Manager):
    def get_queryset(self):
        stati_prog = [u'1', u'2', u'3', u'4', u'5', u'7', ]
        return ProgettazioneQuerySet(self.model, using=self._db).filter(
            interventopiano__intervento__stato__in=stati_prog)


class InCorsoQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__intervento__quadroeconomicointervento__importo'),
            "count": Count('interventopiano__intervento__quadroeconomicointervento__importo')
        }
        return self.filter(interventopiano__intervento__quadroeconomicointervento__tipologia=u'16'). \
            aggregate(**aggregate_dict)


class InCorsoManager(models.Manager):
    def get_queryset(self):
        stati_incorso = [u'6', u'8', u'9', u'10', ]
        return InCorsoQuerySet(self.model, using=self._db).filter(interventopiano__intervento__stato__in=stati_incorso)


class ConclusiQuerySet(models.QuerySet):
    def with_count(self):
        aggregate_dict = {
            "sum": Sum('interventopiano__intervento__imp_congr_spesa'),
            "count": Count('interventopiano__intervento__imp_congr_spesa')
        }
        return self.aggregate(**aggregate_dict)


class ConclusiManager(models.Manager):
    def get_queryset(self):
        stati_concl = [u'11', ]
        return ConclusiQuerySet(self.model, using=self._db).filter(interventopiano__intervento__stato__in=stati_concl)