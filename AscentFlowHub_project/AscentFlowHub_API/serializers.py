from rest_framework import serializers
from .models import *


class LifeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeCategoryModel
        fields = '__all__'
