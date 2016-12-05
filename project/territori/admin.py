from django.contrib.gis import admin
from .models import Territorio


class TerritorioAdmin(admin.GeoModelAdmin):
    model = Territorio
    list_filter = ('tipologia','cluster')
    search_fields = ('denominazione',)
    prepopulated_fields = {"slug": ("denominazione",)}


admin.site.register(Territorio, TerritorioAdmin)