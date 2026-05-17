import uuid
from itertools import chain

from django.http import JsonResponse

from .models import RecoveryCode
from .utils import send_recovery_code
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from notifications.models import Notification
from questions.forms import CommentForm
from questions.models import Question, Comment, Like, CommentLike, AnswerLike
from users.forms import (
    LoginForm,
    PasswordRestoreCodeForm,
    PasswordRestoreEmailForm,
    PasswordRestoreNewForm,
    ProfileForm,
    SignUpForm,
)
from users.models import User, Subscription
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from questions.views import get_question_context
import traceback

logger = logging.getLogger('project')


# Create your views here.
def can_act(user):
    return user.is_authenticated and user.active


def logout_page(request):
    logout(request)
    return redirect('/')


def signup_page(request):
    context = {}

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        logger.warning('Signup form errors: %s', form.errors)
        if form.is_valid():
            password1 = form.cleaned_data['password']
            password2 = form.cleaned_data['password_confirm']
            if password1 == password2:
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
                logger.warning('Password confirmation failed during signup')
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
                logger.warning('Login failed: wrong username or password')
    else:
        form = LoginForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            User.objects.get(username=username)
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
    if request.method == 'POST':
        form = PasswordRestoreEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                recovery = RecoveryCode.create_for_user(user)

                try:
                    send_recovery_code(email, recovery.code)

                    request.session['restore_email'] = email
                    request.session['restore_user_id'] = user.id

                    logger.info('Recovery email sent to %s', email)
                    logger.debug('Email settings: %s:%s, from %s', settings.EMAIL_HOST, settings.EMAIL_PORT,
                                 settings.DEFAULT_FROM_EMAIL)

                    messages.success(
                        request, 'Код восстановления отправлен на вашу почту!')
                    return redirect('password_restore_code')

                except Exception as e:
                    logger.error('Recovery email sending failed: %s', e)
                    logger.debug('Traceback: %s', traceback.format_exc())
                    messages.error(
                        request, f'Ошибка отправки письма: {str(e)}')

                else:
                    messages.success(
                        request, 'Если почта существует, код отправлен на неё.')
                    return redirect('password_restore')
    else:
        form = PasswordRestoreEmailForm()

    return render(request, 'password_restore.html', {'form': form})


def password_restore_code_page(request):
    if 'restore_email' not in request.session:
        messages.error(request, 'Сначала введите почту')
        return redirect('password_restore')

    if request.method == 'POST':
        form = PasswordRestoreCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user_id = request.session.get('restore_user_id')

            recovery = RecoveryCode.objects.filter(
                user_id=user_id,
                code=code,
                is_used=False
            ).first()

            if recovery and recovery.is_valid():

                recovery.is_used = True
                recovery.save()
                request.session['restore_code_verified'] = True

                messages.success(
                    request, 'Код подтверждён! Теперь придумайте новый пароль.')
                return redirect('password_restore_new')
            else:
                messages.error(request, 'Неверный или истёкший код')
    else:
        form = PasswordRestoreCodeForm()

    return render(request, 'password_restore_code.html', {'form': form})


def password_restore_new_page(request):
    if not request.session.get('restore_code_verified'):
        messages.error(request, 'Сначала подтвердите код')
        return redirect('password_restore_code')

    if request.method == 'POST':
        form = PasswordRestoreNewForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password1']
            user_id = request.session.get('restore_user_id')

            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()

            del request.session['restore_email']
            del request.session['restore_user_id']
            del request.session['restore_code_verified']

            messages.success(
                request, 'Пароль успешно изменён! Теперь войдите.')
            return redirect('login')

    else:
        form = PasswordRestoreNewForm()

    return render(request, 'password_restore_new.html', {'form': form})


def profile_page_general(request, username):
    if request.user.is_authenticated:
        user = request.user
        target_user = get_object_or_404(User, username=username)
        posts = Question.objects.filter(
            author=target_user).order_by('-creation_date')
        is_owner = (request.user.is_authenticated and user == target_user)
        posts_context = []
        for post in posts:
            post_context = get_question_context(post.pk)

            if request.user.is_authenticated:
                user_like = Like.objects.filter(
                    user=request.user, question=post).first()
                post_context['user_rating'] = user_like.rating if user_like else 0
            else:
                post_context['user_rating'] = 0

            posts_context.append(post_context)

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
    if not can_act(request.user):
        return redirect('/')

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
                path = default_storage.save(
                    filename, ContentFile(image_file.read()))
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
        posts = Question.objects.filter(
            author=target_user).order_by('-creation_date')
        comments = Comment.objects.filter(author=target_user)

        # Создаем список с данными о комментариях и рейтингах пользователя
        comments_data = []
        for comment in comments:
            user_rating = 0
            if request.user.is_authenticated:
                comment_like = CommentLike.objects.filter(
                    author=request.user, comment=comment).first()
                user_rating = comment_like.rating if comment_like else 0

            comments_data.append({
                'comment': comment,
                'user_rating': user_rating,
            })

        context = {
            'user': target_user,
            'comments_data': comments_data,
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
        comments_likes = CommentLike.objects.filter(
            author=target_user, rating=1)
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
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    if not request.user.active:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Вы заблокированы'})

        return JsonResponse({
            'ok': False,
            'error': 'Вы заблокированы'
        }, status=200)

    friend = get_object_or_404(User, id=user_id)
    current_user = request.user

    if current_user == friend:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Нельзя подписаться на себя'})
        return redirect(f'/profile/{friend.username}/')

    subscription_exists = Subscription.objects.filter(
        user1=current_user,
        user2=friend
    ).exists()

    if not subscription_exists:
        Subscription.objects.create(user1=current_user, user2=friend)
        Notification.objects.create(
            user=friend,
            text=f'{current_user.username} подписался на вас',
            link=f'/profile/{current_user.username}/'
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    next_url = request.POST.get('next', request.GET.get(
        'next', f'/profile/{friend.username}/'
    ))
    return redirect(next_url)


def delete_friend(request, user_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    if not request.user.active:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Вы заблокированы'})

        return JsonResponse({
            'ok': False,
            'error': 'Вы заблокированы'
        }, status=200)

    friend = get_object_or_404(User, id=user_id)
    current_user = request.user

    subscription = Subscription.objects.filter(
        user1=current_user,
        user2=friend
    ).first()

    if subscription:
        subscription.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    next_url = request.POST.get('next', request.GET.get(
        'next', f'/profile/{friend.username}/'
    ))
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
