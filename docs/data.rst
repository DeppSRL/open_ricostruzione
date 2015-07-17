
Data management
===============

In Open Ricostruzione there are two sources of data:

- Interventi a programma
- Donazioni




To load new Interventi a programma data just launch

.. code-block:: bash

  python manage.py import_data --path=/PATH/TO/DATA/ -v2

**Note:** the folder MUST contain 2 files, one for tipologie and one for interventi data.

To load new Interventi a programma data just launch

.. code-block:: bash

  python manage.py import_donazioni -v1 --file=/PATH/TO/DONAZIONI/FILE.CSV
  
  

