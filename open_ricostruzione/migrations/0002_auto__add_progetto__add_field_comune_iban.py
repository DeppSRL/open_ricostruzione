# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Progetto'
        db.create_table('open_ricostruzione_progetto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_progetto', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('comune', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['open_ricostruzione.Comune'])),
            ('denominazione', self.gf('django.db.models.fields.TextField')(max_length=4096)),
        ))
        db.send_create_signal('open_ricostruzione', ['Progetto'])

        # Adding field 'Comune.iban'
        db.add_column('open_ricostruzione_comune', 'iban',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Progetto'
        db.delete_table('open_ricostruzione_progetto')

        # Deleting field 'Comune.iban'
        db.delete_column('open_ricostruzione_comune', 'iban')


    models = {
        'open_ricostruzione.comune': {
            'Meta': {'object_name': 'Comune'},
            'codice_istat': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'open_ricostruzione.progetto': {
            'Meta': {'object_name': 'Progetto'},
            'comune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['open_ricostruzione.Comune']"}),
            'denominazione': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_progetto': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['open_ricostruzione']