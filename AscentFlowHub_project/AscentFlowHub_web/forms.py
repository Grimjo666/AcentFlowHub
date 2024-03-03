from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from AscentFlowHub_API.models import LifeCategoryModel


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=100, required=True)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput, required=True)


class UserAuthenticationForm(AuthenticationForm):
    model = User
    fields = ['username', 'password']


class LifeCategoryForm(forms.ModelForm):
    class Meta:
        model = LifeCategoryModel
        fields = ['name', 'first_color', 'second_color']
        labels = {'name': 'Название сферы'}
        widgets = {
            'first_color': forms.HiddenInput(),
            'second_color': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Установка значений по умолчанию
        self.fields['first_color'].initial = '#e52e71'
        self.fields['second_color'].initial = '#d6b8ff'
