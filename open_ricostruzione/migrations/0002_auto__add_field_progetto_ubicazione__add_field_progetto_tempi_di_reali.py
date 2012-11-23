# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Progetto.ubicazione'
        db.add_column('open_ricostruzione_progetto', 'ubicazione',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=500),
                      keep_default=False)

        # Adding field 'Progetto.tempi_di_realizzazione'
        db.add_column('open_ricostruzione_progetto', 'tempi_di_realizzazione',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Progetto.stato_attuale'
        db.add_column('open_ricostruzione_progetto', 'stato_attuale',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Progetto.tempistica_prevista'
        db.add_column('open_ricostruzione_progetto', 'tempistica_prevista',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Progetto.interventi_previsti'
        db.add_column('open_ricostruzione_progetto', 'interventi_previsti',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Progetto.epoca'
        db.add_column('open_ricostruzione_progetto', 'epoca',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Progetto.cenni_storici'
        db.add_column('open_ricostruzione_progetto', 'cenni_storici',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Progetto.ulteriori_info'
        db.add_column('open_ricostruzione_progetto', 'ulteriori_info',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Progetto.ubicazione'
        db.delete_column('open_ricostruzione_progetto', 'ubicazione')

        # Deleting field 'Progetto.tempi_di_realizzazione'
        db.delete_column('open_ricostruzione_progetto', 'tempi_di_realizzazione')

        # Deleting field 'Progetto.stato_attuale'
        db.delete_column('open_ricostruzione_progetto', 'stato_attuale')

        # Deleting field 'Progetto.tempistica_prevista'
        db.delete_column('open_ricostruzione_progetto', 'tempistica_prevista')

        # Deleting field 'Progetto.interventi_previsti'
        db.delete_column('open_ricostruzione_progetto', 'interventi_previsti')

        # Deleting field 'Progetto.epoca'
        db.delete_column('open_ricostruzione_progetto', 'epoca')

        # Deleting field 'Progetto.cenni_storici'
        db.delete_column('open_ricostruzione_progetto', 'cenni_storici')

        # Deleting field 'Progetto.ulteriori_info'
        db.delete_column('open_ricostruzione_progetto', 'ulteriori_info')


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
            'cenni_storici': ('django.db.models.fields.TextField', [], {}),
            'comune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Comune']", 'null': 'True'}),
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
            'tempistica_prevista': ('django.db.models.fields.TextField', [], {}),
            'tipologia': ('django.db.models.fields.SmallIntegerField', [], {}),
            'ubicazione': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'ulteriori_info': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['open_ricostruzione']