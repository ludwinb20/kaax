from rest_framework import serializers
from .models import Verificaciones

class VerificacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verificaciones
        fields = '__all__'
