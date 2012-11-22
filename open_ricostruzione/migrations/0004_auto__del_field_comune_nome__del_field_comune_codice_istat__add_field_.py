# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Comune.nome'
        db.delete_column('open_ricostruzione_comune', 'nome')

        # Deleting field 'Comune.codice_istat'
        db.delete_column('open_ricostruzione_comune', 'codice_istat')

        # Adding field 'Comune.tipo_territorio'
        db.add_column('open_ricostruzione_comune', 'tipo_territorio',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=2),
                      keep_default=False)

        # Adding field 'Comune.cod_comune'
        db.add_column('open_ricostruzione_comune', 'cod_comune',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=10),
                      keep_default=False)

        # Adding field 'Comune.cod_provincia'
        db.add_column('open_ricostruzione_comune', 'cod_provincia',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=3),
                      keep_default=False)

        # Adding field 'Comune.denominazione'
        db.add_column('open_ricostruzione_comune', 'denominazione',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Comune.slug'
        db.add_column('open_ricostruzione_comune', 'slug',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)


        # Changing field 'Comune.iban'
        db.alter_column('open_ricostruzione_comune', 'iban', self.gf('django.db.models.fields.CharField')(max_length=30, null=True))

    def backwards(self, orm):
        # Adding field 'Comune.nome'
        db.add_column('open_ricostruzione_comune', 'nome',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Comune.codice_istat'
        db.add_column('open_ricostruzione_comune', 'codice_istat',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=10),
                      keep_default=False)

        # Deleting field 'Comune.tipo_territorio'
        db.delete_column('open_ricostruzione_comune', 'tipo_territorio')

        # Deleting field 'Comune.cod_comune'
        db.delete_column('open_ricostruzione_comune', 'cod_comune')

        # Deleting field 'Comune.cod_provincia'
        db.delete_column('open_ricostruzione_comune', 'cod_provincia')

        # Deleting field 'Comune.denominazione'
        db.delete_column('open_ricostruzione_comune', 'denominazione')

        # Deleting field 'Comune.slug'
        db.delete_column('open_ricostruzione_comune', 'slug')


        # Changing field 'Comune.iban'
        db.alter_column('open_ricostruzione_comune', 'iban', self.gf('django.db.models.fields.CharField')(default='', max_length=30))

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
        'open_ricostruzione.progetto': {
            'Meta': {'object_name': 'Progetto'},
            'comune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Comune']"}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_progetto': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['open_ricostruzione']