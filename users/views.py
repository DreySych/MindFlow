from django.shortcuts import render, redirect
from users.forms import *
from users.models import User
from django.contrib.auth.hashers import check_password, make_password
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def logout_page(request):
    logout(request)
    return redirect('/')

def signup_page(request):
    context = {}

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password']
            password2 = form.cleaned_data['password_confirm']
            if password1==password2:
                user = User(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=make_password(form.cleaned_data['password']),
                    name=form.cleaned_data['name'],
                    surname=form.cleaned_data['surname'],
                    sex=form.cleaned_data['sex'],
                    role='',
                    birth_date=form.cleaned_data['birth_date'],
                    registration_date=datetime.date.today(),
                    reputation=0,
                    image=form.cleaned_data['image']
                )
                username = user.username
                user.save()
                user = User.objects.get(username=username)
                login(request, user)
                return redirect('/')
            else:
                print("Пароли не совпадают")
    else:
        form = SignUpForm()

    context['form'] = form

    return render(request, 'signup.html', context)

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            if user and check_password(password, user.password):
                request.session['user_id'] = user.id
                login(request, user)
                return redirect('index')
            else:
                print("ОШИБКА. НЕВЕРНЫЙ ПАРОЛЬ")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def password_restore_page(request):
    return render(request, template_name="password_restore.html")

def profile_page(request):
    return render(request, template_name="profile.html")
