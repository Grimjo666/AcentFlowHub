from django.shortcuts import render
from djoser.views import UserViewSet


class CustomUserViewSet(UserViewSet):
    def create(self, request, *args, **kwargs):
        pass
