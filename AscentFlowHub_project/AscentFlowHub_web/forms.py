from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=100, required=True)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput, required=True)


class UserAuthenticationForm(AuthenticationForm):
    model = User
    fields = ['username', 'password']