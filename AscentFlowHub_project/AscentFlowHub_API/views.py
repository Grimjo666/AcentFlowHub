from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from AscentFlowHub_API import serializers, models


class LifeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LifeCategorySerializer

    def get_queryset(self):
        return models.LifeCategoryModel.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        category_name = request.query_params.get('category_name')

        if not user_id and not category_name:
            return super().list(request, *args, **kwargs)

        elif not user_id or not category_name:
            return Response({'error': 'Поля user_id и category_name являются обязательными'}, status=400)

        else:

            # Извлекаем объект из базы данных
            try:
                category_data = models.LifeCategoryModel.objects.get(user=user_id, slug_name=category_name)
            except models.LifeCategoryModel.DoesNotExist:
                return Response({'error': 'Категория не найдена'}, status=404)

            serializer = self.serializer_class(category_data)
            return Response(serializer.data)


class TreeGoalsViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TreeGoalsSerializer

    def get_queryset(self):
        return models.TreeGoalsModel.objects.filter(user=self.request.user)
