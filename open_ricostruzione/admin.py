from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from open_ricostruzione.models import Donazione, InterventoProgramma, InterventoPiano, Cofinanziamento, \
    EventoContrattuale, Intervento, Liquidazione, Impresa, Progetto, Programma, Piano, \
    QuadroEconomicoProgetto, QuadroEconomicoIntervento, DonazioneInterventoProgramma,TipoImmobile,\
    RUP, ProprietarioImmobile, \
    SoggettoAttuatore

from .filters import TerritorioWithDonazione, TerritorioWithIntervento


class InterventoProgrammaAdmin(admin.ModelAdmin):
    model = InterventoProgramma
    ordering = ['n_ordine']
    list_filter = ['programma', TerritorioWithIntervento, 'tipo_immobile', ]
    search_fields = ['^denominazione', 'id_fenice']


class TipoImmobileAdmin(admin.ModelAdmin):
    model = TipoImmobile


class DonazioneInterventoProgrammaAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'intervento_programma': ('n_ordine', 'denominazione'),
        'donazione': ('denominazione', 'territorio__denominazione'),
    }
    fields = ('donazione', 'intervento_programma', 'importo', )


class DonazioneInterventoProgrammaAdminInline(admin.TabularInline):
    model = DonazioneInterventoProgramma


class InterventoAdmin(admin.ModelAdmin):
    model = Intervento


class ProgrammaAdmin(admin.ModelAdmin):
    model = Programma


class PianoAdmin(admin.ModelAdmin):
    model = Piano
    ordering = ['id_fenice']


class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione
    search_fields = ['^denominazione', ]
    list_filter = [TerritorioWithDonazione, 'tipologia_cedente']
    ordering = ['denominazione', 'territorio__slug']


class LiquidazioneAdmin(admin.ModelAdmin):
    model = Liquidazione


class ImpresaAdmin(admin.ModelAdmin):
    model = Impresa


class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto


class InterventoPianoAdmin(admin.ModelAdmin):
    model = InterventoPiano


class CofinanziamentoAdmin(admin.ModelAdmin):
    model = Cofinanziamento


class EventoContrattualeAdmin(admin.ModelAdmin):
    model = EventoContrattuale


class QEProgettoAdmin(admin.ModelAdmin):
    model = QuadroEconomicoProgetto


class QEInterventoAdmin(admin.ModelAdmin):
    model = QuadroEconomicoIntervento


class SoggettoAttuatoreAdmin(admin.ModelAdmin):
    model = SoggettoAttuatore
    ordering = ('denominazione',)


class RUPAdmin(admin.ModelAdmin):
    model = RUP


class ProprietarioImmobileAdmin(admin.ModelAdmin):
    model = ProprietarioImmobile


admin.site.register(TipoImmobile, TipoImmobileAdmin)
admin.site.register(ProprietarioImmobile, ProprietarioImmobileAdmin)
admin.site.register(RUP, RUPAdmin)
admin.site.register(SoggettoAttuatore, SoggettoAttuatoreAdmin)
admin.site.register(DonazioneInterventoProgramma, DonazioneInterventoProgrammaAdmin)
admin.site.register(QuadroEconomicoIntervento, QEInterventoAdmin)
admin.site.register(QuadroEconomicoProgetto, QEProgettoAdmin)
admin.site.register(Liquidazione, LiquidazioneAdmin)
admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Piano, PianoAdmin)
admin.site.register(Programma, ProgrammaAdmin)
admin.site.register(Impresa, ImpresaAdmin)
admin.site.register(Cofinanziamento, CofinanziamentoAdmin)
admin.site.register(EventoContrattuale, EventoContrattualeAdmin)
admin.site.register(InterventoPiano, InterventoPianoAdmin)
admin.site.register(InterventoProgramma, InterventoProgrammaAdmin)
admin.site.register(Intervento, InterventoAdmin)
admin.site.register(Donazione, DonazioneAdmin)