from django.contrib import admin
from open_ricostruzione.models import Donazione, InterventoAProgramma, InterventoAPiano, Cofinanziamento, EventoContrattuale, QuadroEconomico, Intervento, Liquidazione, Impresa, Progetto


class InterventoAProgettoAdmin(admin.ModelAdmin):
    model = InterventoAProgramma
    search_fields = ['^denominazione', ]


class InterventoAdmin(admin.ModelAdmin):
    model = Intervento


class LiquidazioneAdmin(admin.ModelAdmin):
    model = Liquidazione


class ImpresaAdmin(admin.ModelAdmin):
    model = Impresa


class ProgettoAdmin(admin.ModelAdmin):
    model = Progetto


class InterventoAPianoAdmin(admin.ModelAdmin):
    model = InterventoAPiano


class QuadroEconomicoAdmin(admin.ModelAdmin):
    model = QuadroEconomico


class CofinanziamentoAdmin(admin.ModelAdmin):
    model = Cofinanziamento


class EventoContrattualeAdmin(admin.ModelAdmin):
    model = EventoContrattuale


class DonazioneAdmin(admin.ModelAdmin):
    model = Donazione
    search_fields = ['^denominazione', ]


admin.site.register(Liquidazione, LiquidazioneAdmin)
admin.site.register(Progetto, ProgettoAdmin)
admin.site.register(Impresa, ImpresaAdmin)
admin.site.register(QuadroEconomico, QuadroEconomicoAdmin)
admin.site.register(Cofinanziamento, CofinanziamentoAdmin)
admin.site.register(EventoContrattuale, EventoContrattualeAdmin)
admin.site.register(InterventoAPiano, InterventoAPianoAdmin)
admin.site.register(InterventoAProgramma, InterventoAProgettoAdmin)
admin.site.register(Intervento, InterventoAdmin)
admin.site.register(Donazione, DonazioneAdmin)