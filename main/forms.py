from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
import datetime

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150, label='Никнейм')
    email = forms.EmailField(label='Почта', widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    name = forms.CharField(max_length=255, label='Имя')
    surname = forms.CharField(max_length=255, label='Фамилия')
    sex = forms.IntegerField(label='Пол')
    role = forms.CharField(max_length=50, label='Роль')
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Никнейм')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
