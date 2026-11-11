from rest_framework import serializers
from .models import Products


class SerializerProduct(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'