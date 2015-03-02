import logging
from django.core.management.base import NoArgsCommand
from django.utils.text import slugify
from open_ricostruzione.models import TipoImmobile


class Command(NoArgsCommand):
    help = 'Create basic tipo immobile from TIPOLOGIA Choice'
    logger = logging.getLogger('csvimport')

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

        self.logger.info("Start script")
        for t in TipoImmobile.TIPOLOGIA:
            d = {
                'tipologia': t[0],
                'slug': slugify(t[1])
            }

            ti, is_created = TipoImmobile.objects.get_or_create(
                tipologia=t[0],
                slug=slugify(t[1]),
                defaults={'descrizione': t[1]})
            if is_created:
                self.logger.info("Created TipoImmobile with slug:'{}'".format(d['slug']))
            else:
                self.logger.info("Found TipoImmobile with slug:'{}'".format(d['slug']))

        self.logger.info("Done")