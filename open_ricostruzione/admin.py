from django.contrib import admin
from open_ricostruzione.models import Donazione, InterventoProgramma, InterventoPiano, Cofinanziamento, \
    EventoContrattuale, Intervento, Liquidazione, Impresa, Progetto, Programma, Piano, \
    QuadroEconomicoProgetto, QuadroEconomicoIntervento

from .filters import TerritorioWithDonazione


class InterventoAProgettoAdmin(admin.ModelAdmin):
    model = InterventoProgramma
    ordering = ['n_ordine']
    list_filter = ['tipo_immobile', ]
    search_fields = ['^denominazione', ]


class InterventoAdmin(admin.ModelAdmin):
    model = Intervento


class ProgrammaAdmin(admin.ModelAdmin):
    model = Programma


class PianoAdmin(admin.ModelAdmin):
    model = Piano
    ordering = ['id_piano']


class LiquidazioneAdmin(admin.ModelAdmin):
    model = Liquidazione


class ImpresaAdmin(admin.ModelAdmin):
    model = Impresa


class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto


class InterventoAPianoAdmin(admin.ModelAdmin):
    model = InterventoPiano


class CofinanziamentoAdmin(admin.ModelAdmin):
    model = Cofinanziamento


class EventoContrattualeAdmin(admin.ModelAdmin):
    model = EventoContrattuale


class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione
    search_fields = ['^denominazione', ]
    list_filter = [TerritorioWithDonazione, 'tipologia_cedente']
    ordering = ['denominazione','territorio__slug']


class QEProgettoAdmin(admin.ModelAdmin):
    model = QuadroEconomicoProgetto


class QEInterventoAdmin(admin.ModelAdmin):
    model = QuadroEconomicoIntervento


admin.site.register(QuadroEconomicoIntervento, QEInterventoAdmin)
admin.site.register(QuadroEconomicoProgetto, QEProgettoAdmin)
admin.site.register(Liquidazione, LiquidazioneAdmin)
admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Piano, PianoAdmin)
admin.site.register(Programma, ProgrammaAdmin)
admin.site.register(Impresa, ImpresaAdmin)
admin.site.register(Cofinanziamento, CofinanziamentoAdmin)
admin.site.register(EventoContrattuale, EventoContrattualeAdmin)
admin.site.register(InterventoPiano, InterventoAPianoAdmin)
admin.site.register(InterventoProgramma, InterventoAProgettoAdmin)
admin.site.register(Intervento, InterventoAdmin)
admin.site.register(Donazione, DonazioneAdmin)