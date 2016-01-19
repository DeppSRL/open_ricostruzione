from rest_framework import serializers, pagination
from .models import Donazione, InterventoProgramma, Programma, SoggettoAttuatore
from territori.models import Territorio


class TerritorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Territorio
        fields = (
            'istat_id',
            'prov',
            'regione',
            'denominazione',
            'slug',
            'gps_lat',
            'gps_lon',
        )


class DonazioneSerializer(serializers.ModelSerializer):
    """
    Serializes donazioni querysets.
    """
    territorio = TerritorioSerializer()

    class Meta:
        model = Donazione
        fields = (
            'id',
            'territorio',
            'denominazione',
            'informazioni',
            'data',
            'tipologia_donazione',
            'tipologia_cedente',
            'importo')


class ProgrammaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programma
        fields = (
            'denominazione',
            'id_fenice',
        )


class SoggettoAttuatoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoggettoAttuatore
        fields = (
            'denominazione',
            'descrizione',
            'slug',
        )


class InterventoProgrammaSerializer(serializers.ModelSerializer):
    """
    Serializes interv. programma querysets.
    """
    territorio = TerritorioSerializer()
    programma = ProgrammaSerializer()
    soggetto_attuatore = SoggettoAttuatoreSerializer()

    class Meta:
        model = InterventoProgramma
        fields = (
            'id',
            'programma',
            'id_fenice',
            'soggetto_attuatore',
            'propr_immobile',
            'n_ordine',
            'importo_generale',
            'importo_a_programma',
            'denominazione',
            'territorio',
            'vari_territori',
            'tipo_immobile_fenice',
            'categ_immobile',
            'slug',

        )


class PaginatedDonazioneSerializer(pagination.PaginationSerializer):
    """
    Serializes page objects of donazione querysets.
    """

    class Meta:
        object_serializer_class = Donazione