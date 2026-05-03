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
    sex = forms.TypedChoiceField(label='Пол', widget=forms.RadioSelect, choices=sex_vatiants, required=False, empty_value=None, coerce= lambda x: int(x))
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}), required=False)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Никнейм')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

class ProfileForm(forms.Form):
    username = forms.CharField(label='Никнейм', max_length=100, required=True)
    role = forms.CharField(label='Роль', max_length=100, required=False)
    email = forms.EmailField(label='Почта', required=True)
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    image = forms.ImageField(label='Фото профиля', required=False)
