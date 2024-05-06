from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api import serializers, models


class CustomFilterMixin:
    @staticmethod
    def get_filtered_request_params(request, model: object) -> dict:
        filtered_params = dict()
        if not request.query_params:
            return filtered_params

        # Получаем поля модели
        model_fields = [field.name for field in model._meta.fields]
        many_to_many_fields = [field.name for field in model._meta.many_to_many]
        model_fields.extend(many_to_many_fields)

        # Получаем параметры запроса и фильтруем их на основе model_fields
        query_params = request.query_params
        filtered_params = dict(filter(lambda param: param[0] in model_fields, query_params.items()))

        # Возвращаем отфильтрованный словарь параметров
        return filtered_params


class LifeCategoryViewSet(viewsets.ModelViewSet, CustomFilterMixin):
    serializer_class = serializers.LifeCategorySerializer
    model = models.LifeCategory

    def get_queryset(self):
        filtered_params = self.get_filtered_request_params(self.request, self.model)

        queryset = self.model.objects.filter(user=self.request.user, **filtered_params)
        return queryset


class TreeGoalsViewSet(viewsets.ModelViewSet, CustomFilterMixin):
    serializer_class = serializers.TreeGoalsSerializer
    model = models.TreeGoals

    def get_queryset(self):
        filtered_params = self.get_filtered_request_params(self.request, self.model)

        parent = filtered_params.get('parent')

        if parent and parent.lower() in ('none', 'null'):
            filtered_params['parent'] = None

        queryset = self.model.objects.filter(user=self.request.user, **filtered_params).order_by('creation_date')
        return queryset

    @action(methods=['get'], detail=False, url_path='with-sub-goals')
    def get_goals_with_sub_goals_list(self, request):
        """
        Получаем список целей с подцелями
        :param request:
        :return:
        """
        try:
            filtered_params = self.get_filtered_request_params(request, models.TreeGoals)
            parent = filtered_params.get('parent')

            if parent and parent.lower() in ('none', 'null'):
                filtered_params['parent'] = None

            goals_data = self.model.objects.filter(user=self.request.user, **filtered_params).order_by('creation_date')

            serialized_data = self.add_sub_goals_in_serialized_data(goals_data)

            return Response(serialized_data)
        except Exception as e:
            return Response(str(e), status=404)

    def add_sub_goals_in_serialized_data(self, goals_data):
        """
        Сериализуем и добавляем подцель к сериализованным данным цели
        :param goals_data:
        :return:
        """
        if isinstance(goals_data, models.TreeGoals):
            goals_data = [goals_data]

        # Проходимся по queryset и создаём словарь с id цели = сериализованые данные подцелей это цели
        sub_goal_dict = {}
        for goal in goals_data:
            sub_goal_dict[goal.id] = self.serializer_class(goal.children.order_by('creation_date'), many=True).data

        # Сериализуем queryset целей и добавляем в него данные о подцелях
        serialized_data = self.serializer_class(goals_data, many=True).data
        for goal in serialized_data:
            goal_id = goal['id']  # получаем id цели
            # Добавляем в сериализованые данные информацию о подцелях
            goal['sub_goals'] = sub_goal_dict[goal_id]
        return serialized_data

    @action(methods=['get'], detail=True, url_path='with-sub-goals')
    def get_goals_with_sub_goals_detail(self, request, pk=None):
        """
        Получаем конкретную цель с данными о подцелях
        :param request:
        :param pk: id цели
        :return:
        """
        try:
            goal_data = models.TreeGoals.objects.get(id=pk)
            serialized_data = self.add_sub_goals_in_serialized_data(goal_data)

            return Response(serialized_data)

        except Exception as e:
            return Response(str(e), status=404)

    @action(methods=['patch', 'put'], detail=False)
    def update_goals(self, request):
        print(request.data)
        goal_data = models.TreeGoals.objects.update()
        return Response({'xnj': 1})
