from rest_framework import serializers
from .models import Donazione
from territori.models import Territorio


class TerritorioSerializer(serializers.ModelSerializer):

    class Meta:
        model=Territorio
        fields = {'slug',}

class DonazioneSerializer(serializers.ModelSerializer):
    """
    Serializing all the Donazione
    """

    territorio = TerritorioSerializer()

    class Meta:
        model = Donazione
        fields = ('id', 'territorio','denominazione','informazioni','data' ,'tipologia_donazione', 'tipologia_cedente', 'importo')