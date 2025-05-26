from rest_framework import serializers
from .models import Conducteur

class ConducteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conducteur
        fields = '__all__'
