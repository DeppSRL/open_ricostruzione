# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Donazione.importo'
        db.alter_column('open_ricostruzione_donazione', 'importo', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2))

        # Changing field 'Progetto.riepilogo_importi'
        db.alter_column('open_ricostruzione_progetto', 'riepilogo_importi', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2))

        # Changing field 'Progetto.importo_previsto'
        db.alter_column('open_ricostruzione_progetto', 'importo_previsto', self.gf('django.db.models.fields.TextField')(default=0, max_length=4096))

    def backwards(self, orm):

        # Changing field 'Donazione.importo'
        db.alter_column('open_ricostruzione_donazione', 'importo', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=2))

        # Changing field 'Progetto.riepilogo_importi'
        db.alter_column('open_ricostruzione_progetto', 'riepilogo_importi', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=2))

        # Changing field 'Progetto.importo_previsto'
        db.alter_column('open_ricostruzione_progetto', 'importo_previsto', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=2))

    models = {
        'open_ricostruzione.comune': {
            'Meta': {'object_name': 'Comune'},
            'cod_comune': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'cod_provincia': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
            'comune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Comune']"}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_padre': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'id_progetto': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'importo_previsto': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'riepilogo_importi': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['open_ricostruzione']