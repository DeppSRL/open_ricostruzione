# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import logging
from territori.models import Territorio


class Command(BaseCommand):
    help = 'Fix territori ISTAT code: adds zero padding when needed'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):

        territori = list(Territorio.objects.filter(tipologia="C",).order_by('-cluster','-denominazione'))

        self.logger.info("Start update")
        for t in territori:
            self.logger.info(u"Update {}".format(t.denominazione))
            if len(t.istat_id) == 5:
                t.istat_id = t.istat_id.zfill(6)
                t.save()
        self.logger.info("Done updating")

