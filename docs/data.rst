
Data management
===============

In Open Ricostruzione there are two sources of data:

- Interventi a programma
- Donazioni


Interventi a programma
----------------------

To load new Interventi a programma data just launch

.. code-block:: bash

  python manage.py import_data --path=/PATH/TO/DATA/ -v2

**Note:** the folder MUST contain 2 files, one for tipologie (FENICE_OR_DatiBase.json) and one for interventi data (FENICE_OR_Interventi.json).

This script calls the following management tasks:

- import_tipologie
- import_interventi
- import_latlong

Import tipologie
----------------

Imports all types for different kind of data: there are types for Piano, Programma, Soggetto Attuatore and so on.
These values are stored in the DB to facilitate the following imports and web platform activites.
If some category doesn't match with the values previously set in the web application an error message is printed.

**NOTE:** is very common the the source of data changes over time, and so categories change. This sometimes require for a change in the models.py file where some category are set. For example: TIPO_IMMOBILE_FENICE is defined in the InterventoProgramma object. For this typology the value "1" means "ALTRO", if this changes then the value must be changed in the file.



Import interventi
-----------------

This is the main data import. The import file contains all the details of the single projects that Open Ricostruzione should map.

This script saves the three fundamental objs of the web platform: Intervento a programma, intervento a piano and Intervento.
These three objs define the single intervention.

Connected to these objects there are many others that define the payments, the documentation and the Impresa doing the work.

All these are defined in the Interventi file and imported with this fairly simple script.

import_latlong
--------------

Being that in the Interventi file there is no LAT / LONG for the project then this script reads a CSV file (normally is fixtures/interv_prog_lat_long.csv) where there are lat long values associated with the ID FENICE of the Intervento a programma.

If the script enconters any error, an error msg is printed out.


Donazioni
---------

To load new Interventi a programma data just launch

.. code-block:: bash

  python manage.py import_donazioni -v1 --file=/PATH/TO/DONAZIONI/FILE.CSV
  
**WARNING** This mng task deletes ALL DATA about Donazioni and Donazioni Programma, so be careful.


Donazioni are quite simple objects, but some of them are linked to Intervento a programma so when a Donazione is linked to an Intervento a link is created.
  
Exports
=======

There a couple of mng task to export Interventi Programma and Donazioni so that they can be used externally.

