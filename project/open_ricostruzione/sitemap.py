from django.conf import settings
from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.core.urlresolvers import reverse

from .models import InterventoProgramma, Impresa, SoggettoAttuatore, TipoImmobile
from territori.models import Territorio


class LocalitaSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    """Reverse static views for XML sitemap."""

    def items(self):
        return Territorio.get_territori_cratere().values('slug')

    def location(self, item):
        return reverse('localita', kwargs={'slug': item['slug']}, )


class InterventoProgrammaSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return InterventoProgramma.objects.all().values('slug')

    def location(self, item):
        return reverse('intervento-programma', kwargs={'slug': item['slug']}, )


class ImpresaSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Impresa.objects.all().values('slug')

    def location(self, item):
        return reverse('impresa', kwargs={'slug': item['slug']}, )


class SoggettoAttuatoreSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return SoggettoAttuatore.objects.all().values('slug')

    def location(self, item):
        return reverse('sogg-attuatore', kwargs={'slug': item['slug']}, )


class TipoImmobileSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return TipoImmobile.objects.all().values('slug')

    def location(self, item):
        return reverse('tipo-immobile', kwargs={'slug': item['slug']}, )

class DonazioniSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['']

    def location(self, item):
        return reverse('lista-donazioni', kwargs={}, )

class HomeSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['']

    def location(self, item):
        return reverse('home', kwargs={}, )


sitemaps = {
    'intervento-programma': InterventoProgrammaSitemap,
    'localita': LocalitaSitemap,
    'tipo-immobile': TipoImmobileSitemap,
    'soggetto-attuatore': SoggettoAttuatoreSitemap,
    'impresa': ImpresaSitemap,
    'lista-donazioni': DonazioniSitemap,
    'home': HomeSitemap,
}
