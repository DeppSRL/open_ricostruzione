from django.contrib import admin
from open_ricostruzione.models import *
from open_ricostruzione.filters import HasProgetto

class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto
    search_fields = ['^denominazione', 'id_progetto' ]

class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione
    ordering = ['data']
    list_filter = ['tipologia', HasProgetto]
    search_fields = ['^denominazione', 'id_donazione', 'data']
    list_per_page = 500


class TerritorioAdmin(admin.ModelAdmin):
    model = Territorio
    search_fields = ['^denominazione', ]

class TipologiaProgettoAdmin(admin.ModelAdmin):
    model = TipologiaProgetto
    ordering = ['codice']


class TipologiaCedenteAdmin(admin.ModelAdmin):
    model = TipologiaCedente
    ordering = ['codice']
    prepopulated_fields = {'slug':('denominazione',),}

class EntryAdmin(admin.ModelAdmin):
    model=Entry
    ordering=['-published_at']
    prepopulated_fields = {'slug':('title',),}

class UltimoAggiornamentoAdmin(admin.ModelAdmin):
    model=UltimoAggiornamento


admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Territorio, TerritorioAdmin)
admin.site.register(TipologiaProgetto, TipologiaProgettoAdmin)
admin.site.register(Donazione, DonazioneAdmin)
admin.site.register(TipologiaCedente, TipologiaCedenteAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(UltimoAggiornamento, UltimoAggiornamentoAdmin)