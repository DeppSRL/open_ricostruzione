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

admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Territorio, TerritorioAdmin)
admin.site.register(Donazione, DonazioneAdmin)