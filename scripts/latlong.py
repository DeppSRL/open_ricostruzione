#Script che importa latitudine e longitudine
#per tutti i comuni dell'Emilia a partire dalle API di Openpolis
#questo file serve solo come reference dei comandi,
#lo script dava errore per cui l'import l'ho eseguito nella shell di Python

from open_ricostruzione.models import Territorio
import requests

r = requests.get(
    'http://api2.openpolis.it/territori/v2/territori/?limit=0&format=json&location_type__name=Comune&regional_id=8',
    auth=('user', 'pass')
    )

if r.status_code ==200:
    json= r.json()['objects']
    for c in json:
        comune=Territorio.objects.get(cod_comune="0"+str(c['city_id']))
        comune.gps_lat=c['gps_lat']
        comune.gps_lon=c['gps_lon']
        comune.save()


print "Import latlon terminato"

