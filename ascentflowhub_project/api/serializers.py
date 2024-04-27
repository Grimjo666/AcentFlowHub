from rest_framework import serializers
from .models import *


class LifeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeCategory
        fields = '__all__'


class TreeGoalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeGoals
        fields = '__all__'
