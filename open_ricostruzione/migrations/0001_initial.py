# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Comune'
        db.create_table('open_ricostruzione_comune', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo_territorio', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('cod_comune', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('cod_provincia', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('iban', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=60)),
        ))
        db.send_create_signal('open_ricostruzione', ['Comune'])

        # Adding model 'Progetto'
        db.create_table('open_ricostruzione_progetto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_progetto', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('id_padre', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('tipologia', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('comune', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Comune'], null=True)),
            ('importo_previsto', self.gf('django.db.models.fields.TextField')(max_length=4096)),
            ('riepilogo_importi', self.gf('django.db.models.fields.DecimalField')(default=0.0, null=True, max_digits=15, decimal_places=2, blank=True)),
            ('denominazione', self.gf('django.db.models.fields.TextField')(max_length=4096)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=60)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Progetto'], null=True)),
        ))
        db.send_create_signal('open_ricostruzione', ['Progetto'])

        # Adding model 'Donazione'
        db.create_table('open_ricostruzione_donazione', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_donazione', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('comune', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Comune'])),
            ('denominazione', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('tipologia', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('data', self.gf('django.db.models.fields.DateField')()),
            ('avvenuto', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('importo', self.gf('django.db.models.fields.DecimalField')(default=0.0, null=True, max_digits=15, decimal_places=2, blank=True)),
            ('confermato', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('open_ricostruzione', ['Donazione'])


    def backwards(self, orm):
        # Deleting model 'Comune'
        db.delete_table('open_ricostruzione_comune')

        # Deleting model 'Progetto'
        db.delete_table('open_ricostruzione_progetto')

        # Deleting model 'Donazione'
        db.delete_table('open_ricostruzione_donazione')


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
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Progetto']", 'null': 'True'}),
            'riepilogo_importi': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['open_ricostruzione']