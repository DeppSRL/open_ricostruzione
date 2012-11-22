# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Comune.slug'
        db.alter_column('open_ricostruzione_comune', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=60))
        # Adding index on 'Comune', fields ['slug']
        db.create_index('open_ricostruzione_comune_slug', ['slug'])

        # Adding field 'Progetto.slug'
        db.add_column('open_ricostruzione_progetto', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='', max_length=60),
                      keep_default=False)


    def backwards(self, orm):
        # Removing index on 'Comune', fields ['slug']
        db.delete_index('open_ricostruzione_comune', ['slug'])


        # Changing field 'Comune.slug'
        db.alter_column('open_ricostruzione_comune', 'slug', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Deleting field 'Progetto.slug'
        db.delete_column('open_ricostruzione_progetto', 'slug')


    models = {
        'open_ricostruzione.comune': {
            'Meta': {'object_name': 'Comune'},
            'cod_comune': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'cod_provincia': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'tipo_territorio': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'open_ricostruzione.donazione': {
            'Meta': {'object_name': 'Donazione'},
            'avvenuto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Comune']"}),
            'confermato': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data': ('django.db.models.fields.DateField', [], {}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_donazione': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'importo': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'open_ricostruzione.progetto': {
            'Meta': {'object_name': 'Progetto'},
            'comune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Comune']", 'null': 'True'}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_padre': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'id_progetto': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'importo_previsto': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'riepilogo_importi': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['open_ricostruzione']