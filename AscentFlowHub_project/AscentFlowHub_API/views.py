from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets
from .serializers import *
from .models import *


class LifeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = LifeCategorySerializer

    def get_queryset(self):
        return LifeCategoryModel.objects.filter(user=self.request.user)





