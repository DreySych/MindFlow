from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
import datetime
from .models import User

from django.forms import ImageField


class SignUpForm(forms.Form):
    sex_vatiants = [
        (1, "Мужской"),
        (2, "Женский")
    ]

    username = forms.CharField(max_length=150, label='Никнейм')
    email = forms.EmailField(label='Почта', widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')
    name = forms.CharField(max_length=255, label='Имя')
    surname = forms.CharField(max_length=255, label='Фамилия')
    sex = forms.ChoiceField(label='Пол', widget=forms.RadioSelect, choices=sex_vatiants)
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))
    image = ImageField(label='Изображение', required=False)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Никнейм')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
