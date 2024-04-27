from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

import requests as rqt

from frontend import forms
from .mixins import HttpResponseMixin
from .models import UserTraining
from api.api_client import LifeCategoryAPI, UserApiError, TreeGoalsAPI


def page_not_found(request):
    return render(request, 'frontend/page_not_found.html')


def index_page(request):
    return render(request, 'frontend/index.html')


def test_page(request):
    return render(request, 'frontend/test_page.html')


class LogoutView(View, HttpResponseMixin):
    domain = settings.DOMAIN_NAME

    def get(self, request):
        try:
            user_token = request.COOKIES.get('Authorization')

            logout(request)
            messages.success(request, 'Вы вышли из системы')

            if user_token:
                api_logout_endpoint = self.domain + reverse('logout')
                #  Аннулируем токен пользователя
                response = rqt.post(api_logout_endpoint, headers={'Authorization': user_token})

                cookie_names = ('Authorization',)  # кортеж с именами кук для удаления
                return self.delete_cookie_and_redirect(cookie_names, 'index_page_path')

        except Exception as e:

            messages.error(request, 'Произошла ошибка при выходе из системы')
            return redirect('index_page_path')

        else:
            return redirect('index_page_path')


class LoginPageView(View, HttpResponseMixin):
    template_name = 'frontend/login.html'
    domain = settings.DOMAIN_NAME

    def get(self, request, context=None):
        form = forms.UserAuthenticationForm()
        if not context:
            context = {
                'form': form
            }
        return render(request, self.template_name, context)

    def post(self, request):
        form = forms.UserAuthenticationForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            # Если пользователь существует делаем пост-запрос к эндпоинту для создания токена
            if user:
                return self.handle_login(request, user, password)

        return self.get(request, context={'form': form})

    def handle_login(self, request, user, password):
        try:
            api_login_endpoint = self.domain + reverse('login')
            response = rqt.post(
                api_login_endpoint,
                data={'username': user.username, 'password': password}
            )
            # Если создание токена прошло успешно то логиним пользователя
            if response.status_code == 200:

                token = response.json().get('auth_token')
                cookie_dict = {'Authorization': f'Token {token}'}  # словарь с куками

                login(request, user)
                messages.success(request, 'Выполнен вход')

                return self.set_cookie_and_redirect(cookie_dict=cookie_dict, redirect_path_name='index_page_path')

            else:
                messages.error(request, 'Произошла ошибка при попытке входа в аккаунт')

        except rqt.exceptions.RequestException as e:
            messages.error(request, f'Network error: {str(e)}')

        except Exception as e:
            messages.error(request, str(e))

        return self.get(request)


def registration_page(request):
    api_register_endpoint = 'http://127.0.0.1:8000/api/v1/auth/users/'

    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            response = rqt.post(
                api_register_endpoint,
                data={
                    'username': username,
                    'email': email,
                    'password': password,
                    're_password': confirm_password
                }
            )

            if response.status_code == 201:
                messages.success(request, 'Вы успешно зарегистрировались')
                user = authenticate(request, username=username, password=password)

                return LoginPageView().handle_login(request, user, password)

            else:

                messages.warning(request, response.data)

            return redirect('index_page_path')
    else:
        form = forms.RegistrationForm()
    return render(request, 'frontend/registration.html', context={'form': form})


class MyProgressPageView(View):
    template_name = 'frontend/my_progress.html'

    def get(self, request):
        try:
            api_requests = LifeCategoryAPI(request)
            response = api_requests.get_list_data()

            if response.ok:
                context = {
                    'life_category_list': response.json(),
                    'modal_window': False,
                    'life_category_form': forms.LifeCategoryForm
                }

                user_training = UserTraining.objects.filter(user=request.user.id)[0]

                # Получаем инфу о том, создавал ли пользователь сферы жизни
                already_created_categories = user_training.creating_base_categories
                if not already_created_categories:
                    context['modal_window'] = True
                    user_training.creating_base_categories = True
                    user_training.save()

                return render(request, self.template_name, context=context)

            raise ValueError(response.json()['detail'])

        except Exception as e:
            messages.error(request, str(e))
            return redirect('index_page_path')

    def post(self, request):
        try:
            api_requests = LifeCategoryAPI(request)
            form_type = request.POST.get('form_type')

            #  Создание базовых сфер жизни
            if form_type == 'create_base_category_form' and request.POST.get('button') == 'create':

                api_requests.create_base_life_categories()
                messages.success(request, 'Созданы базовые сферы жизни')

            #  Обработка формы изменения сфер жизни
            elif form_type == 'edit_categories_form':

                delete_category_id = request.POST.get('delete_category')
                if delete_category_id:
                    api_requests.delete_data(delete_category_id)
                    messages.success(request, 'Сфера жизни удалена')

            # Обработка формы добавления новых сфер жизни
            if form_type == 'create_new_category_form':
                form = forms.LifeCategoryForm(request.POST)
                if form.is_valid():
                    data = {
                        'name': form.cleaned_data['name'],
                        'first_color': form.cleaned_data['first_color'],
                        'second_color': form.cleaned_data['second_color'],
                        'user': request.user.id
                    }
                    api_requests.create_life_category(data=data)
                    messages.success(request, 'Сфера жизни добавлена')

            return redirect('my_progress_page_path')

        except UserApiError as e:
            messages.warning(request, str(e))
            return redirect('my_progress_page_path')

        except Exception as e:
            messages.error(request, f'Произошла непредвиденная ошибка: {e}')
            return redirect('index_page_path')


class SphereOfLifePageView(View):
    template_name = 'frontend/sphere_of_life.html'

    def get(self, request, category_name):
        api_life_category_requests = LifeCategoryAPI(request)
        api_tree_goals_requests = TreeGoalsAPI(request)

        new_goal_form = forms.TreeGoalsForm()

        context = {
            'new_goal_form': new_goal_form,
        }

        life_category_response = api_life_category_requests.get_life_category_by_slug_name(slug_name=category_name)

        if life_category_response.ok:
            context['current_life_category'] = life_category_response.json()[0]

            # Получаем id текущей категории
            life_category_id = life_category_response.json()[0].get('id')

            goals_response = api_tree_goals_requests.get_goals(life_category=life_category_id, sub_goals=True)

            if goals_response.ok:
                # Фильтруем разбиваем данные на два массива (активные цели и завершённые)
                active_goals_list = filter(lambda goal: goal['completed'] is False, goals_response.json())
                completed_goals_list = filter(lambda goal: goal['completed'] is True, goals_response.json())

                context['active_goals_list'] = active_goals_list
                context['completed_goals_list'] = completed_goals_list

            else:
                messages.error(request, goals_response.text)
        else:
            messages.error(request, life_category_response.text)

        return render(request, self.template_name, context=context)

    def post(self, request, category_name):
        form_type = request.POST.get('form_type')

        try:
            # Обработка формы добавления новой цели
            if form_type == 'new_goal_from':
                self.new_goal_form_handler(request, category_name)

            # Обработка формы выполнения\изменения\удаления цели
            elif form_type == 'manage_goal_form':
                self.button_processing_process(request)

            elif form_type == 'checkbox_form':
                self.checkbox_form_handler(request)

            # Обновляем процент выполненных целей пользователя
            self.update_life_category_percent(request, slug_name=category_name)

        except Exception as e:
            messages.error(request, f'Ошибка при обработке формы: {form_type} - {e}')

        return redirect('sphere_of_life_page_path', category_name=category_name)

    def checkbox_form_handler(self, request):
        checkbox_list = request.POST.getlist('checkbox')
        # Проходим по списку и достаём ID цели
        if checkbox_list:
            for goal_id in checkbox_list:
                # Вызываем процесс обработки кнопок
                self.button_processing_process(request, int(goal_id))

    def new_goal_form_handler(self, request, category_name=None, life_category_id=None):
        goal_form = forms.TreeGoalsForm(request.POST)

        if goal_form.is_valid():
            # Получаем parent_id из скрытого поля формы
            parent_id = request.POST.get('parent_id')
            # Если parent_id пустое, то мы добавляем основную цель, если нет, то подцель
            if parent_id == '':
                parent_id = None

            self.create_new_goal_process(request, goal_form, category_name, parent_id, life_category_id)
            messages.success(request, 'Цель добавлена')

    def button_processing_process(self, request, goal_id=None):
        """
        Обработчик нажатия кнопок из присылаемой от клиента формы
        :param request:
        :param goal_id: ID текущей цели, для которой нужно выполнить действие, по умолчанию берётся из request
        :return:
        """

        # Узнаём на какую кнопку нажал пользователь
        button = request.POST.get('button')

        if button == 'done':
            self.switch_goal_process(request, goal_id=goal_id)
            messages.success(request, 'Цель выполнена')

        elif button == 'edit':
            pass

        elif button == 'make_active':
            self.switch_goal_process(request, completed=False, goal_id=goal_id)
            messages.success(request, 'Цель снова активна')

        elif button == 'delete':
            self.delete_goal_process(request, goal_id)
            messages.success(request, 'Цель удалена')

        else:
            messages.warning(request, 'Не зарегистрированная кнопка')

    @staticmethod
    def update_life_category_percent(request, slug_name=None, life_category_id=None):
        """
        Обновляем информацию о проценте выполнения в модели LifeCategoryModel
        :param life_category_id: ID категории сфер жизни
        :param request:
        :param slug_name:
        :return:
        """
        api_life_category_requests = LifeCategoryAPI(request)
        api_tree_goals_requests = TreeGoalsAPI(request)
        if not life_category_id:
            life_category_response = api_life_category_requests.get_life_category_by_slug_name(slug_name=slug_name)
            life_category_id = life_category_response.json()[0].get('id')

        # Получаем текущий процент выполнения
        percent = api_tree_goals_requests.calculate_completion_percentage(life_category_id)
        # Делаем запрос на обновление данных
        api_life_category_requests.partially_update(pk=life_category_id, data={'percent': percent})

    @staticmethod
    def create_new_goal_process(request, goal_form, category_name=None, parent_id=None, life_category_id=None):
        name = goal_form.cleaned_data['name']
        weight = goal_form.cleaned_data['weight']
        description = goal_form.cleaned_data['description']

        api_life_category_requests = LifeCategoryAPI(request)
        api_tree_goals_requests = TreeGoalsAPI(request)

        if not life_category_id:
            # Получаем текущую категорию
            life_category_response = api_life_category_requests.get_life_category_by_slug_name(slug_name=category_name)

            if not life_category_response.ok:
                raise UserApiError('Ошибка во время создания цели')

            life_category_id = life_category_response.json()[0].get('id')

        tree_goal_response = api_tree_goals_requests.create_data({
            'name': name,
            'weight': weight,
            'description': description,
            'life_category': life_category_id,
            'user': request.user.id,
            'parent': parent_id
        })
        return tree_goal_response

    @staticmethod
    def delete_goal_process(request, goal_id=None):
        if not goal_id:
            goal_id = request.POST.get('goal_id')

        if goal_id:
            api_tree_goals_requests = TreeGoalsAPI(request)
            api_response = api_tree_goals_requests.delete_data(goal_id)
            return api_response
        else:
            raise Exception('Отсутствует goal_id')

    @staticmethod
    def switch_goal_process(request, completed=True, goal_id=None):
        """
        Обработчик переключения цели (выполнена / активна)
        :param request:
        :param completed: по умолчанию True (делает цель завершённой)
        :param goal_id: ID цели
        :return: API response
        """

        if not goal_id:
            goal_id = request.POST.get('goal_id')

        if goal_id:
            api_tree_goals_requests = TreeGoalsAPI(request)
            api_response = api_tree_goals_requests.partially_update(goal_id, data={'completed': completed})
            return api_response
        else:
            raise Exception('Отсутствует goal_id')


class SubGoalPageView(View):
    template_name = 'frontend/sub_goal_page.html'

    def get(self, request, sub_goal_id):
        api_tree_goals_requests = TreeGoalsAPI(request)
        api_response = api_tree_goals_requests.get_goal_by_id(sub_goal_id, sub_goals=True)

        new_goal_form = forms.TreeGoalsForm()

        context = {
            'new_goal_form': new_goal_form,
        }

        if api_response.ok:
            context['goal'] = api_response.json()[0]
        else:
            messages.error(request, api_response.text)

        return render(request, self.template_name, context=context)

    def post(self, request, sub_goal_id):
        form_type = request.POST.get('form_type')
        sphere_of_life_view = SphereOfLifePageView()
        api_tree_goal_requests = TreeGoalsAPI(request)
        try:
            # Получаем id категории сфер жизни
            api_goal_response = api_tree_goal_requests.get_goal_by_id(goal_id=sub_goal_id)
            life_category_id = api_goal_response.json().get('life_category')[0]

            if form_type == 'manage_goal_form':
                sphere_of_life_view.button_processing_process(request, sub_goal_id)

            elif form_type == 'new_goal_from':
                sphere_of_life_view.new_goal_form_handler(request, life_category_id=life_category_id)

            elif form_type == 'checkbox_form':
                sphere_of_life_view.checkbox_form_handler(request)

            # Обновляем процент выполненных целей пользователя
            sphere_of_life_view.update_life_category_percent(request, life_category_id=life_category_id)

        except Exception as e:
            messages.error(request, f'Ошибка при обработке формы: {form_type} - {e}')

        url = reverse('sub_goal_page_path', kwargs={'sub_goal_id': sub_goal_id})
        return redirect(url)
