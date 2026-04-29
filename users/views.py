import os
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from users.forms import ProfileForm
from users.forms import *
from users.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
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
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            password1 = form.cleaned_data['password']
            password2 = form.cleaned_data['password_confirm']
            if password1==password2:
                user = User()
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.password = make_password(form.cleaned_data['password'])
                user.name = form.cleaned_data['name']
                user.surname = form.cleaned_data['surname']
                user.sex = form.cleaned_data['sex']
                user.role = ''
                user.birth_date = form.cleaned_data['birth_date']
                user.registration_date = datetime.date.today()
                user.reputation = 0
                image_file = form.cleaned_data.get('image')
                if image_file:
                    ext = image_file.name.split('.')[-1]
                    filename = f"avatars/{uuid.uuid4()}.{ext}"
                    path = default_storage.save(filename, ContentFile(image_file.read()))
                    user.image = path
                user.save()
                username = user.username
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
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.birth_date = form.cleaned_data['birth_date']
                user.role = ''
                image_file = form.cleaned_data.get('image')
                if image_file:
                    ext = image_file.name.split('.')[-1]
                    filename = f"avatars/{uuid.uuid4()}.{ext}"
                    path = default_storage.save(filename, ContentFile(image_file.read()))
                    user.image = path
                user.save()
                return redirect('profile')
        else:
            initial_data = {
                'username': user.username,
                'role': user.role,
                'email': user.email,
                'birth_date': user.birth_date,
                'image_photo': user.image
            }
            form = ProfileForm(initial=initial_data)
            return render(request, 'profile.html', {'form': form, 'user': user})

    else:
        return redirect('/account/login')
    return render(request, template_name="profile.html")
