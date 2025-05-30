from rest_framework import serializers
from .models import Disease

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ['id', 'name', 'description', 'treatment', 'advice']