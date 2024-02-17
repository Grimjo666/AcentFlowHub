from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.contrib import messages

import requests as rqt


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


def login_page(request):
    return render(request, 'AscentFlowHub_web/login.html')
