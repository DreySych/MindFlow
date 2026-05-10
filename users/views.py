import os
import uuid
from itertools import chain
from operator import attrgetter

from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from notifications.models import Notification
from questions.forms import CommentForm
from questions.models import Question, Comment, Like, QuestionLike, CommentLike, AnswerLike
from users.forms import ProfileForm
from users.forms import *
from users.models import User, Subscription
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from questions.views import get_question_context

# Create your views here.

def logout_page(request):
    logout(request)
    return redirect('/')

def signup_page(request):
    context = {}

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        print(form.errors)
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

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким логином не найден')
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Неверный пароль')
            return redirect('login')

        login(request, user)
        return redirect('index')
    return render(request, 'login.html', {'form': form})


def password_restore_page(request):
    return render(request, template_name="password_restore.html")


def profile_page_general(request, username):
    if request.user.is_authenticated:
        user = request.user
        target_user = get_object_or_404(User, username=username)
        posts = Question.objects.filter(author=target_user)
        is_owner = (request.user.is_authenticated and user == target_user)
        posts_context = []
        for post in posts:
            posts_context.append(get_question_context(post.pk))

        context = {
            'user': target_user,
            'posts_context': posts_context,
            'is_owner': is_owner,
            'is_friend': is_friend(user, target_user),
            'comment_form': CommentForm(),
            'subscriptions': Subscription.objects.filter(user1=request.user),
        }
        return render(request, 'profile_general.html', context)

    else:
        return redirect('/account/login')

def profile_page_settings(request):
    if not request.user.is_authenticated:
        return redirect('/account/login')

    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.birth_date = form.cleaned_data['birth_date']
            user.sex = form.cleaned_data['sex']

            image_file = request.FILES.get('image')

            if image_file:
                ext = image_file.name.split('.')[-1]
                filename = f"avatars/{uuid.uuid4()}.{ext}"
                path = default_storage.save(filename, ContentFile(image_file.read()))
                user.image = path

            user.save()

            return redirect('profile_general', username=user.username)

    else:
        form = ProfileForm(initial={
            'username': user.username,
            'email': user.email,
            'sex': user.sex,
            'birth_date': user.birth_date,
        })

    context = {
        'form': form,
        'user': user,
        'subscriptions': Subscription.objects.filter(user1=request.user),
    }

    return render(request, 'profile_settings.html', context)


def profile_page_comments(request, username):
    if request.user.is_authenticated:
        target_user = get_object_or_404(User, username=username)
        posts = Question.objects.filter(author=target_user)
        comments = Comment.objects.filter(author=target_user)
        context = {
            'user': target_user,
            'comments': comments,
            'posts': posts,
            'subscriptions': Subscription.objects.filter(user1=request.user),
        }
        context['is_owner'] = request.user == target_user

        context['is_friend'] = Subscription.objects.filter(
            user1=request.user,
            user2=target_user
        ).exists()
        return render(request, 'profile_comments.html', context=context)

    else:
        return redirect('/account/login')

def profile_page_liked(request, username):
    if request.user.is_authenticated:
        target_user = get_object_or_404(User, username=username)

        question_likes = Like.objects.filter(user=target_user, rating=1)
        comments_likes = CommentLike.objects.filter(author=target_user, rating=1)
        answers_likes = AnswerLike.objects.filter(author=target_user, rating=1)

        def get_like_date(like):
            if hasattr(like, 'created_at'):
                return like.created_at

            if hasattr(like, 'question'):
                return like.question.creation_date

            if hasattr(like, 'comment'):
                return like.comment.creation_date

            if hasattr(like, 'answer'):
                return like.answer.creation_date

            return datetime.datetime.now()

        all_likes = sorted(
            chain(question_likes, comments_likes, answers_likes),
            key=get_like_date,
            reverse=True
        )

        context = {
            'user': target_user,
            'all_likes': all_likes,
            'questions_likes': question_likes,
            'comments_likes': comments_likes,
            'answers_likes': answers_likes,
            'subscriptions': Subscription.objects.filter(user1=request.user),
        }

        return render(request, 'profile_liked.html', context=context)

    return redirect('/account/login')


def add_friend(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    current_user = request.user
    subscription_exists = Subscription.objects.filter(user1=current_user, user2=friend).exists()
    if not subscription_exists and current_user != friend:
        Subscription.objects.create(user1=current_user, user2=friend)
        Notification.objects.create(
            user=friend,
            text=f'{current_user.username} подписался на вас',
            link=f'/profile/{current_user.username}/'
        )

    next_url = request.POST.get('next', request.GET.get('next', f'/profile/{friend.username}'))
    return redirect(next_url)


def delete_friend(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    current_user = request.user
    subscription = Subscription.objects.filter(user1=current_user, user2=friend).first()
    if subscription:
        subscription.delete()

    next_url = request.POST.get('next', request.GET.get('next', f'/profile/{friend.username}'))
    return redirect(next_url)

def is_friend(current_user, other_user):
    if not current_user.is_authenticated or current_user == other_user:
        return False
    return Subscription.objects.filter(user1=current_user, user2=other_user).exists()

def my_profile_redirect(request):
    if request.user.is_authenticated:
        return redirect(
            'profile_general',
            username=request.user.username
        )

    return redirect('/account/login/')