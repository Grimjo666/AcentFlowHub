from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from rest_framework.authtoken.models import Token
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.urls import reverse

import requests as rqt

from AscentFlowHub_web import forms


def index_page(request):
    return render(request, 'AscentFlowHub_web/index.html')


def logout_handler(request):
    api_logout_endpoint = 'http://127.0.0.1:8000/api/v1/auth/token/logout/'

    user_token = Token.objects.filter(user_id=request.user.id)

    if user_token.exists():
        user_token = user_token[0]
        # Если токен существует, передаём его в пост запрос к апи для удаления
        response = rqt.post(api_logout_endpoint, headers={'Authorization': f'Token {user_token}'})

    logout(request)
    messages.success(request, 'Вы вышли мз системы')

    return redirect('index_page_path')


class LoginPageView(View):
    template_name = 'AscentFlowHub_web/login.html'
    api_login_endpoint = 'http://127.0.0.1:8000/api/v1/auth/token/login/'

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
            response = rqt.post(
                self.api_login_endpoint,
                data={'username': user.username, 'password': password}
            )
            # Если создание токена прошло успешно то логиним пользователя
            if response.status_code == 200:

                token = response.json().get('auth_token')
                cookie = {'Authorization': token}

                login(request, user)
                messages.success(request, 'Выполнен вход')

                return self.set_cookie_and_redirect(cookie_dict=cookie, redirect_path_name='index_page_path')

            else:
                messages.error(request, 'Произошла ошибка при попытке входа в аккаунт')

        except rqt.exceptions.RequestException as e:
            messages.error(request, f'Network error: {str(e)}')

        except Exception as e:
            print(str(e))

        return self.get(request)

    @staticmethod
    def set_cookie_and_redirect(cookie_dict: dict, redirect_path_name: str, httponly=True):
        """
        redirect_path_name - это имя, указанное в аргументе name, функции path, обычный путь эта функция не принимает
        """
        try:
            url = reverse(redirect_path_name)
            redirect_response = HttpResponseRedirect(url)
            for key, value in cookie_dict.items():
                redirect_response.set_cookie(key=key, value=value, httponly=httponly)

            return redirect_response

        except Exception as e:
            print(f"Error setting cookie: {str(e)}")

            return HttpResponseServerError("Внутрення ошибка сервера")


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
    return render(request, 'AscentFlowHub_web/registration.html', context={'form': form})
