from django.contrib import admin
from open_ricostruzione.models import Donazione, Progetto, Territorio


class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto
    search_fields = ['^denominazione',]


class TerritorioAdmin(admin.ModelAdmin):
    model = Territorio
    search_fields = ['^denominazione', ]

class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione
    search_fields = ['^denominazione', ]


admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Territorio, TerritorioAdmin)
admin.site.register(Donazione, DonazioneAdmin)