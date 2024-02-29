from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

import requests as rqt

from AscentFlowHub_web import forms
from .mixins import HttpResponseMixin
from constants.base_life_category_data import BASE_LIFE_CATEGORY_DATA
from .models import UserTrainingModel


def page_not_found(request):
    return render(request, 'AscentFlowHub_web/page_not_found.html')


def index_page(request):
    return render(request, 'AscentFlowHub_web/index.html')


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

            print(f"Error during logout: {str(e)}")
            messages.error(request, 'Произошла ошибка при выходе из системы')
            return redirect('index_page_path')

        else:
            return redirect('index_page_path')


class LoginPageView(View, HttpResponseMixin):
    template_name = 'AscentFlowHub_web/login.html'
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
            print(str(e))

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

                # Создаём модель обучения пользователя
                user_training = UserTrainingModel(user=request.user.id).save()

                return LoginPageView().handle_login(request, user, password)

            else:
                messages.warning(request, response.data)

            return redirect('index_page_path')
    else:
        form = forms.RegistrationForm()
    return render(request, 'AscentFlowHub_web/registration.html', context={'form': form})


class MyProgressPageView(View):
    template_name = 'AscentFlowHub_web/my_progress.html'
    domain = settings.DOMAIN_NAME

    def get(self, request):
        try:
            user_token = request.COOKIES.get('Authorization')
            api_data_endpoint = self.domain + reverse('life_category_path-list')
            response = rqt.get(api_data_endpoint, headers={'Authorization': user_token})

            if response.ok:
                context = {
                    'life_category_list': response.json(),
                    'modal_window': False
                }

                user_training = UserTrainingModel.objects.filter(user=request.user.id)[0]

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
            #  Создание базовых сфер жизни
            if request.POST.get('form_type') == 'create_base_category_form' and request.POST.get('button') == 'create':

                api_data_endpoint = self.domain + reverse('life_category_path-list')
                self.create_base_life_category_processing(request, api_data_endpoint)

            #  Обработка формы изменения сфер жизни
            elif request.POST.get('form_type') == 'edit_categories_form':

                delete_category_id = request.POST.get('delete_category')
                if delete_category_id:
                    api_data_detail_endpoint = self.domain + reverse('life_category_path-detail',
                                                                     kwargs={'pk': delete_category_id})

                    self.category_delete_processing(request, api_data_detail_endpoint)

            return redirect('my_progress_page_path')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('index_page_path')

    @staticmethod
    def category_delete_processing(request, api_data_endpoint):
        user_token = request.COOKIES.get('Authorization')
        response = rqt.delete(api_data_endpoint, headers={'Authorization': user_token})
        messages.success(request, 'Сфера жизни удалена')

    @staticmethod
    def create_base_life_category_processing(request, api_endpoint):
        user_token = request.COOKIES.get('Authorization')

        # создаём список со словарями для создания сфер жизни пользователя
        for category_data in BASE_LIFE_CATEGORY_DATA:
            data = {'user': request.user.id, **category_data}
            response = rqt.post(api_endpoint, data=data, headers={'Authorization': user_token})
