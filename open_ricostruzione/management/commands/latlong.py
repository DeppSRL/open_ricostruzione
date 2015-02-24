import os
import requests

from open_ricostruzione.models import Territorio
from django.core.management.base import NoArgsCommand, make_option
from django.conf import settings

class Command(NoArgsCommand):
    """
    Script che importa latitudine e longitudine
    per tutti i comuni dell'Emilia a partire dalle API di Openpolis
    questo file serve solo come reference dei comandi,
    lo script dava errore per cui l'import l'ho eseguito nella shell di Python
    """

    help = "Import lat and lon values into Comuni"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
    )

    def handle_noargs(self, **options):
      r = requests.get(
        '%s/territori/v2/territori/?limit=0&format=json&location_type__name=Comune&regional_id=8' % settings.OP_API['base_url'],
        auth=(settings.OP_API['username'], settings.OP_API['password'])
      )

      if r.status_code ==200:
        json= r.json()['objects']
        for c in json:
          comune=Territorio.objects.get(cod_comune="0"+str(c['city_id']))
          comune.gps_lat=float(c['gps_lat'])
          comune.gps_lon=float(c['gps_lon'])
          comune.save()
          if options['verbose']:
            print "Comune: %s (%s, %s)" % (comune.denominazione, comune.gps_lat, comune.gps_lon)


      print "Import latlon terminato"

