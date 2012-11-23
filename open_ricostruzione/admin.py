from django.contrib import admin
from open_ricostruzione.models import *

class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto
    search_fields = ['^denominazione', ]

class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione

class ComuneAdmin(admin.ModelAdmin):
    model = Comune
    search_fields = ['^denominazione', ]

admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Comune, ComuneAdmin)
admin.site.register(Donazione, DonazioneAdmin)