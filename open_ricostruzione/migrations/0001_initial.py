# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Territorio'
        db.create_table('open_ricostruzione_territorio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo_territorio', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('cod_comune', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('cod_provincia', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('iban', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=60)),
        ))
        db.send_create_signal('open_ricostruzione', ['Territorio'])

        # Adding model 'TipologiaProgetto'
        db.create_table('open_ricostruzione_tipologiaprogetto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codice', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('open_ricostruzione', ['TipologiaProgetto'])

        # Adding model 'Progetto'
        db.create_table('open_ricostruzione_progetto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_progetto', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('id_padre', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('tipologia', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('territorio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Territorio'], null=True)),
            ('importo_previsto', self.gf('django.db.models.fields.TextField')(max_length=4096)),
            ('riepilogo_importi', self.gf('django.db.models.fields.DecimalField')(default=0.0, null=True, max_digits=15, decimal_places=2, blank=True)),
            ('denominazione', self.gf('django.db.models.fields.TextField')(max_length=4096)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=60)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Progetto'], null=True)),
            ('ubicazione', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('tempi_di_realizzazione', self.gf('django.db.models.fields.TextField')()),
            ('stato_attuale', self.gf('django.db.models.fields.TextField')()),
            ('interventi_previsti', self.gf('django.db.models.fields.TextField')()),
            ('epoca', self.gf('django.db.models.fields.TextField')()),
            ('cenni_storici', self.gf('django.db.models.fields.TextField')()),
            ('ulteriori_info', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('open_ricostruzione', ['Progetto'])

        # Adding model 'Donazione'
        db.create_table('open_ricostruzione_donazione', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_donazione', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('territorio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Territorio'])),
            ('denominazione', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('tipologia', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('data', self.gf('django.db.models.fields.DateField')()),
            ('avvenuto', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('importo', self.gf('django.db.models.fields.DecimalField')(default=0.0, null=True, max_digits=15, decimal_places=2, blank=True)),
            ('confermato', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('open_ricostruzione', ['Donazione'])


    def backwards(self, orm):
        # Deleting model 'Territorio'
        db.delete_table('open_ricostruzione_territorio')

        # Deleting model 'TipologiaProgetto'
        db.delete_table('open_ricostruzione_tipologiaprogetto')

        # Deleting model 'Progetto'
        db.delete_table('open_ricostruzione_progetto')

        # Deleting model 'Donazione'
        db.delete_table('open_ricostruzione_donazione')


    models = {
        'open_ricostruzione.donazione': {
            'Meta': {'object_name': 'Donazione'},
            'avvenuto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confermato': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data': ('django.db.models.fields.DateField', [], {}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_donazione': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'importo': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'territorio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Territorio']"}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'open_ricostruzione.progetto': {
            'Meta': {'object_name': 'Progetto'},
            'cenni_storici': ('django.db.models.fields.TextField', [], {}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'epoca': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_padre': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'id_progetto': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'importo_previsto': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'interventi_previsti': ('django.db.models.fields.TextField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Progetto']", 'null': 'True'}),
            'riepilogo_importi': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'stato_attuale': ('django.db.models.fields.TextField', [], {}),
            'tempi_di_realizzazione': ('django.db.models.fields.TextField', [], {}),
            'territorio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Territorio']", 'null': 'True'}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {}),
            'ubicazione': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'ulteriori_info': ('django.db.models.fields.TextField', [], {})
        },
        'open_ricostruzione.territorio': {
            'Meta': {'object_name': 'Territorio'},
            'cod_comune': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'cod_provincia': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'tipo_territorio': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'open_ricostruzione.tipologiaprogetto': {
            'Meta': {'object_name': 'TipologiaProgetto'},
            'codice': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['open_ricostruzione']