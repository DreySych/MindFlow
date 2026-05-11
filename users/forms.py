from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
import datetime
from django.contrib.auth.models import User

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
    sex_vatiants = [
        (1, "Мужской"),
        (2, "Женский")
    ]

    username = forms.CharField(label='Никнейм', max_length=100, required=True)
    sex = forms.TypedChoiceField(label='Пол', widget=forms.RadioSelect, choices=sex_vatiants, required=False,empty_value=None, coerce=lambda x: int(x))
    email = forms.EmailField(label='Почта', required=True)
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    image = forms.ImageField(label='Фото профиля', required=False)

class PasswordRestoreEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'Введите вашу почту',
            'required': True
        })
    )


class PasswordRestoreCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Введите код из письма',
            'required': True,
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        })
    )


class PasswordRestoreNewForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Придумайте новый пароль',
            'required': True,
            'minlength': '6'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Повторите новый пароль',
            'required': True,
            'minlength': '6'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')

        if password1 and len(password1) < 6:
            raise forms.ValidationError('Пароль должен быть не менее 6 символов')

        return cleaned_data
