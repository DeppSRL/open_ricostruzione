from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.core.urlresolvers import reverse
from django.conf import settings
from territori.models import Territorio


class LocalitaSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    destination_view = ''

    """Reverse static views for XML sitemap."""


    def items(self):

        return Territorio.get_territori_cratere().values('slug')


    def location(self, item):
        return reverse('localita', kwargs={'slug':item['slug']}, )




sitemaps = {
    # 'intervento-programma': InterventoProgrammaSitemap,
    'localita': LocalitaSitemap,
    # 'tipo-immobile': TipoImmobileSitemap,
    # 'tipo-soggetto-attuatore': TipoSoggettoAttuatoreSitemap,
    # 'soggetto-attuatore': SoggettoAttuatoreSitemap,
    # 'impresa': ImpresaSitemap,
    }