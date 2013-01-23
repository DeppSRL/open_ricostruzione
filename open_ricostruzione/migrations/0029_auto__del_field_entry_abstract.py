# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Entry.abstract'
        db.delete_column('open_ricostruzione_entry', 'abstract')


    def backwards(self, orm):
        # Adding field 'Entry.abstract'
        db.add_column('open_ricostruzione_entry', 'abstract',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=400),
                      keep_default=False)


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
            'info': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'modalita_r': ('django.db.models.fields.TextField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'progetto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Progetto']", 'null': 'True', 'blank': 'True'}),
            'territorio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Territorio']"}),
            'tipologia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.TipologiaCedente']"})
        },
        'open_ricostruzione.entry': {
            'Meta': {'object_name': 'Entry'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'big_news': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_html': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 0, 0)'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'tipologia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.TipologiaProgetto']"}),
            'ubicazione': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'ulteriori_info': ('django.db.models.fields.TextField', [], {})
        },
        'open_ricostruzione.territorio': {
            'Meta': {'object_name': 'Territorio'},
            'cod_comune': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'cod_provincia': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gps_lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gps_lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sigla_provincia': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'tipo_territorio': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tipologia_cc': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'})
        },
        'open_ricostruzione.tipologiacedente': {
            'Meta': {'object_name': 'TipologiaCedente'},
            'codice': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'})
        },
        'open_ricostruzione.tipologiaprogetto': {
            'Meta': {'object_name': 'TipologiaProgetto'},
            'codice': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'})
        },
        'open_ricostruzione.ultimoaggiornamento': {
            'Meta': {'object_name': 'UltimoAggiornamento'},
            'data_donazioni': ('django.db.models.fields.DateTimeField', [], {}),
            'data_progetti': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['open_ricostruzione']