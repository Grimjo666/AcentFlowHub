import requests as rqt

from django.conf import settings
from django.urls import reverse

from constants.base_life_category_data import BASE_LIFE_CATEGORY_DATA


class UserApiError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ServerApiError(Exception):
    """
    Класс ошибок для возбуждения исключений, предназначенных для разработчиков
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BaseAPI:
    """
    Базовый класс для взаимодействия с API. Предоставляет общие методы для CRUD операций.
    """
    _domain = settings.DOMAIN_NAME  # Доменное имя API
    list_url_pattern = ''  # Url шаблон для получения queryset
    detail_url_pattern = ''  # Url шаблон для получения конкретной записи

    def __init__(self, request):
        self.user_headers = {}
        self.user_id = request.user.id
        self._api_data_list_endpoint = self._domain + reverse(self.list_url_pattern)
        if request.COOKIES.get('Authorization'):
            self.user_headers['Authorization'] = request.COOKIES.get('Authorization')

    def set_user_token(self, user_token):
        self.user_headers['Authorization'] = user_token

    def get_detail_endpoint(self, pk):
        """
        Метод для получения эндпоинта на конкретную запись
        :param pk: id записи в базе данных
        :return: url
        """
        return self._domain + reverse(self.detail_url_pattern, kwargs={'pk': pk})

    def get_list_data(self, pk=None):
        """
        Получаем данные из апи для конкретного пользователя:
        pk=None - в виде списка
        :param pk: id записи в базе данных
        :return: API response
        """
        if pk:
            api_endpoint = self.get_detail_endpoint(pk)
            response = rqt.get(api_endpoint, headers=self.user_headers)
        else:
            response = rqt.get(self._api_data_list_endpoint, headers=self.user_headers)

        if not response.ok:
            response_message = response.json().get('detail')
            raise ServerApiError(f'класс: {self} Ошибка при получении данных: {response_message}')

        return response

    def create_data(self, data):
        """
        Создаём запись в базе данных
        :param data: python словарь с данными. Ключи словаря = поля модели
        :return: API response
        """
        response = rqt.post(self._api_data_list_endpoint, headers=self.user_headers, data=data)

        if not response.ok:
            response_message = response.json().get('detail')
            raise ServerApiError(f'класс: {self} Ошибка при сохранении данных: {response_message}')

        return response

    def partially_update(self, pk, data):
        """
        Частичное обновление данных с помощью метода patch
        :param pk: id изменяемой записи
        :param data: словарь с данными
        :return: API response
        """
        api_endpoint = self.get_detail_endpoint(pk)
        response = rqt.patch(api_endpoint, data=data, headers=self.user_headers)

        if not response.ok:
            response_message = response.json().get('detail')
            raise ServerApiError(f'класс: {self} Ошибка при обновлении данных: {response_message}')

        return response

    def delete_data(self, pk):
        """
        Удаляем запись из БД
        :param pk: id записи в базе данных
        :return: API response
        """
        delete_endpoint = self.get_detail_endpoint(pk)
        response = rqt.delete(delete_endpoint, headers=self.user_headers)

        if not response.ok:
            response_message = response.json().get('detail')
            raise ServerApiError(f'класс: {self} Ошибка при удалении данных: {response_message}')

        return response


class LifeCategoryAPI(BaseAPI):
    list_url_pattern = 'life_category_path-list'  # Url шаблон для получения queryset Модели LifeCategoryModel
    detail_url_pattern = 'life_category_path-detail'  # Url шаблон для получения конкретной записи LifeCategoryModel

    def get_category_by_user_and_name(self, user_id, category_name):
        """
        Получаем конкретную запись по user_id и category_name
        :param user_id: id пользователя
        :param category_name: является полем slug_name из LifeCategoryModel
        :return: API response
        """
        api_endpoint = self._domain + reverse(self.list_url_pattern)
        api_endpoint += f'?user_id={user_id}&category_name={category_name}'
        response = rqt.get(api_endpoint, headers=self.user_headers)
        return response

    def create_life_category(self, data):
        """
        Создаём категорию сферы жизни пользователя
        :param data: python словарь с данными. Ключи словаря = поля модели
        :return: API response
        """
        user_categories_dict = self.get_list_data().json()
        # Проверяем есть ли у пользователя уже категория с таким же названием
        already_exists = any(map(lambda item: item['name'] == data['name'], user_categories_dict))
        if already_exists:
            raise UserApiError('Категория с таким названием уже существует, придумайте другое название')

        return self.create_data(data=data)

    def create_base_life_categories(self):
        """
        Создаём базовые сферы жизни на основе BASE_LIFE_CATEGORY_DATA
        :return: None
        """
        for category_data in BASE_LIFE_CATEGORY_DATA:
            data = {'user': self.user_id, **category_data}
            self.create_life_category(data=data)


class TreeGoalsAPI(BaseAPI):
    list_url_pattern = 'tree_goals_path-list'
    detail_url_pattern = 'tree_goals_path-detail'

    def get_goals(self, life_category_id, parent_id=None):
        """
        Получаем цели из модели TreeGoalsModel
        :param life_category_id: id родительской категории сферы жизни
        :param parent_id: если передаётся, то будут возвращены подцели, передаваемой parent_id (TreeGoalsModel.parent)
        :return: API response
        """
        api_endpoint = self._domain + reverse('tree_goals_path-get-all-goals-with-sub-goals',
                                              kwargs={'life_category_id': life_category_id})
        if parent_id:
            api_endpoint += f'?parent_id={parent_id}'
        response = rqt.get(api_endpoint, headers=self.user_headers)
        return response

    def get_goal_by_id(self, goal_id, sub_goals=False):
        url_pattern = self.detail_url_pattern
        if sub_goals:
            url_pattern = 'tree_goals_path-get-one-goal-with-sub-goals'
        api_endpoint = self._domain + reverse(url_pattern, kwargs={'pk': goal_id})

        response = rqt.get(api_endpoint, headers=self.user_headers)
        return response

