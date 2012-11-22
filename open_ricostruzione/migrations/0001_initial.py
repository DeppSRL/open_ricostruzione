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
            ('codice_istat', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('open_ricostruzione', ['Comune'])


    def backwards(self, orm):
        # Deleting model 'Comune'
        db.delete_table('open_ricostruzione_comune')


    models = {
        'open_ricostruzione.comune': {
            'Meta': {'object_name': 'Comune'},
            'codice_istat': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['open_ricostruzione']