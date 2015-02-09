# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Territorio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cod_finloc', models.CharField(db_index=True, max_length=128, unique=True, null=True, blank=True)),
                ('op_id', models.CharField(db_index=True, max_length=128, null=True, blank=True)),
                ('istat_id', models.CharField(db_index=True, max_length=20, null=True, blank=True)),
                ('prov', models.CharField(max_length=2, null=True, blank=True)),
                ('regione', models.CharField(max_length=32, null=True, blank=True)),
                ('denominazione', models.CharField(max_length=128, db_index=True)),
                ('slug', models.SlugField(max_length=256, null=True, blank=True)),
                ('territorio', models.CharField(db_index=True, max_length=1, choices=[('C', 'Comune'), ('P', 'Provincia'), ('R', 'Regione'), ('N', 'Nazionale'), ('E', 'Estero'), ('L', 'Cluster')])),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
                ('cluster', models.CharField(db_index=True, max_length=1, choices=[('1', 'Fino a 500 abitanti'), ('2', 'Da 501 a 1.000 abitanti'), ('3', 'Da 1.001 a 3.000 abitanti'), ('4', 'Da 3.001 a 5.000 abitanti'), ('5', 'Da 5.001 a 10.000 abitanti'), ('6', 'Da 10.001 a 50.000 abitanti'), ('7', 'Da 50.001 a 200.000 abitanti'), ('8', 'Da 200.001 a 500.000 abitanti'), ('9', 'Oltre i 500.000 abitanti')])),
                ('gps_lat', models.FloatField(null=True, blank=True)),
                ('gps_lon', models.FloatField(null=True, blank=True)),
            ],
            options={
                'ordering': ['denominazione'],
                'verbose_name': 'Localit\xe0',
                'verbose_name_plural': 'Localit\xe0',
            },
            bases=(models.Model,),
        ),
    ]
