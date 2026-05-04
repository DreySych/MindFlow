import os
import uuid
from django.conf import settings
from django.shortcuts import render, redirect

from questions.models import Question, Comment
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
                user.role = ''
                user.sex = form.cleaned_data['sex']
                user.birth_date = form.cleaned_data['birth_date']
                user.registration_date = datetime.date.today()
                user.reputation = 0
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

def profile_page_general(request):
    if request.user.is_authenticated:
        user = request.user
        posts = Question.objects.filter(author=user)
        context = {
            'user': user,
            'posts': posts,
        }
        return render(request, 'profile_general.html', context=context)

    else:
        return redirect('/account/login')

def profile_page_settings(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.birth_date = form.cleaned_data['birth_date']
                user.sex = form.cleaned_data['sex']
                image_file = form.cleaned_data.get('image')
                if image_file:
                    ext = image_file.name.split('.')[-1]
                    filename = f"avatars/{uuid.uuid4()}.{ext}"
                    path = default_storage.save(filename, ContentFile(image_file.read()))
                    user.image = path
                user.save()
                return redirect('profile_general')
        else:
            initial_data = {
                'username': user.username,
                'sex': user.sex,
                'email': user.email,
                'birth_date': user.birth_date,
                'image_photo': user.image
            }
            form = ProfileForm(initial=initial_data)
            context = {
                'form': form,
                'user': user,
            }
            return render(request, 'profile_settings.html', context=context)
    else:
        return redirect('/account/login')
    return render(request, 'profile_settings.html')


def profile_page_comments(request):
    if request.user.is_authenticated:
        user = request.user
        comments = Comment.objects.filter(author=user)
        context = {
            'user': user,
            'comments': comments,
        }
        return render(request, 'profile_comments.html', context=context)

    else:
        return redirect('/account/login')

def profile_page_liked(request):
    return render(request, 'profile_liked.html')