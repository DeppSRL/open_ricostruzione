from django.contrib import admin
from open_ricostruzione.models import *

class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto

class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione

class ComuneAdmin(admin.ModelAdmin):
    model = Comune

admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Comune, ComuneAdmin)
admin.site.register(Donazione, DonazioneAdmin)