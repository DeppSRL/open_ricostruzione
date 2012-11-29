from django.contrib import admin
from open_ricostruzione.models import *

class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto
    search_fields = ['^denominazione', ]

class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione
    ordering = ['data']

class TerritorioAdmin(admin.ModelAdmin):
    model = Territorio
    search_fields = ['^denominazione', ]

class TipologiaProgettoAdmin(admin.ModelAdmin):
    model = TipologiaProgetto

admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Territorio, TerritorioAdmin)
admin.site.register(TipologiaProgetto, TipologiaProgettoAdmin)
admin.site.register(Donazione, DonazioneAdmin)