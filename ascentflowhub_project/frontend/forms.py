from django import forms
from django.contrib.auth.forms import AuthenticationForm
from api.models import ManualUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from api import models as api_models
from .models import UserProfilePhoto


class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=150, required=True)
    confirmation = forms.BooleanField(
        label="I confirm the terms",
        required=True
    )

    def clean_confirmation(self):
        if self.cleaned_data['confirmation'] is not True:
            raise ValidationError('You must confirm')


class UserAuthenticationForm(AuthenticationForm):
    model = ManualUser
    fields = ['email', 'password']


class LifeCategoryForm(forms.ModelForm):
    class Meta:
        model = api_models.LifeCategory
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


class TreeGoalsForm(forms.ModelForm):
    class Meta:
        model = api_models.TreeGoals
        fields = ['name', 'weight', 'description']
        labels = {
            'name': 'Название цели',
            'weight': 'Значимость цели',
            'description': 'Описание (не обязательно)'
        }
        widgets = {
            'description': forms.Textarea
        }


class UploadUserPhotoForm(forms.ModelForm):
    class Meta:
        model = UserProfilePhoto
        fields = ['photo']

    photo = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], label=''
    )


class UserProfileInfoFrom(forms.ModelForm):
    class Meta:
        model = ManualUser
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта'
        }


class ChangeProfilePasswordFrom(forms.ModelForm):
    password_repeat = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = ManualUser
        fields = ['password']
        labels = {
            'password': 'Пароль'
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password and password_repeat and password != password_repeat:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data