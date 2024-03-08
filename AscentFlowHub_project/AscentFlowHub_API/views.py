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

    @action(methods=['get'], detail=False, url_path='get-goals-sub-goals/(?P<life_category_id>[^/.]+)')
    def get_all_goals_with_sub_goals(self, request, life_category_id):

        try:
            parent_id = request.query_params.get('parent_id')

            goals_data = models.TreeGoalsModel.objects.filter(user=self.request.user,
                                                              parent=parent_id,
                                                              life_category=life_category_id)

            serialized_data = self.add_sub_goals_in_serialized_data(goals_data)

            return Response(serialized_data)
        except Exception as e:
            return Response(str(e), status=404)

    def add_sub_goals_in_serialized_data(self, goals_data):

        if isinstance(goals_data, models.TreeGoalsModel):
            goals_data = [goals_data]

        # Проходимся по queryset и создаём словарь с id цели = сериализованые данные подцелей это цели
        sub_goal_dict = {}
        for goal in goals_data:
            sub_goal_dict[goal.id] = self.serializer_class(goal.children.all(), many=True).data

        # Сериализуем queryset целей и добавляем в него данные о подцелях
        serialized_data = self.serializer_class(goals_data, many=True).data
        for goal in serialized_data:
            goal_id = goal['id']  # получаем id цели
            # Добавляем в сериализованые данные информацию о подцелях
            goal['sub_goals'] = sub_goal_dict[goal_id]
        return serialized_data

    @action(methods=['get'], detail=True, url_path='get-goal-sub-goals')
    def get_one_goal_with_sub_goals(self, request, pk=None):
        try:
            goal_data = models.TreeGoalsModel.objects.get(id=pk)

            serialized_data = self.add_sub_goals_in_serialized_data(goal_data)

            return Response(serialized_data)

        except Exception as e:
            return Response(str(e), status=404)




