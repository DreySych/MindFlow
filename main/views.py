from django.shortcuts import render, redirect, get_object_or_404
import datetime

from django.template.context_processors import request

from notifications.models import Notification
from main.forms import SearchForm
from main.model_loader import get_model
from questions.forms import CommentForm
from questions.models import Question, Like, Comment
from questions.views import get_question_context
from users.models import User, Subscription
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.utils import timezone

def can_act(user):
    return user.is_authenticated and user.active

def build_post_context(post, request):
    ctx = get_question_context(post.pk)
    ctx['comment_form'] = CommentForm()
    if request.user.is_authenticated:
        user_like = Like.objects.filter(user=request.user, question=post).first()
        ctx['user_rating'] = user_like.rating if user_like else 0
    else:
        ctx['user_rating'] = 0
    return ctx


def perform_search(search_text):
    model = get_model()
    input_vec = model.encode([search_text])[0]
    questions = Question.objects.all()
    results = []
    for q in questions:
        q_vec = q.get_embedding()
        sim = model.similarity([q_vec], [input_vec])[0][0] if q_vec is not None else -1
        results.append((q, sim))
    return [q for q, _ in sorted(results, key=lambda x: x[1], reverse=True)]


def get_default_questions(request):
    if not can_act(request.user):
        return Question.objects.all().order_by('-rating', '-creation_date')

    friends_ids = Subscription.objects.filter(user1=request.user).values_list('user2_id', flat=True)
    fresh_friends = Question.objects.filter(author_id__in=friends_ids).order_by('-creation_date')[:5]
    fresh_ids = [p.id for p in fresh_friends]

    popular_all = Question.objects.exclude(id__in=fresh_ids).order_by('-rating', '-creation_date')
    popular_friends = Question.objects.filter(author_id__in=friends_ids).exclude(id__in=fresh_ids).order_by('-rating', '-creation_date')

    result = list(fresh_friends)
    all_list = list(popular_all)
    friends_list = list(popular_friends)
    for i in range(max(len(all_list), len(friends_list))):
        if i < len(friends_list):
            result.append(friends_list[i])
        if i < len(all_list):
            result.append(all_list[i])

    seen = set()
    unique = []
    for p in result:
        if p.id not in seen:
            unique.append(p)
            seen.add(p.id)
    return unique

# Create your views here.
def index_page(request):
    if request.method == "POST" and 'question_id' in request.POST:
        question = get_object_or_404(Question, pk=request.POST.get('question_id'))
        form = CommentForm(request.POST)
        if form.is_valid() and can_act(request.user):
            Comment.objects.create(
                text=form.cleaned_data['text'],
                author=request.user,
                question=question,
                creation_date=timezone.now(),
                rating=0
            )
        return redirect('index')

    search_text = request.GET.get('q', '').strip()
    results = perform_search(search_text) if search_text else get_default_questions(request)
    posts_context = [build_post_context(p, request) for p in results]
    context = {
        "username": request.user.username if request.user.is_authenticated else "Профиль",
        "users": User.objects.all(),
        "link1": "account/login/",
        "page1": 'Логин',
        "link2": "account/signup/",
        "page2": 'Регистрация',
        'subscriptions': Subscription.objects.filter(user1=request.user) if request.user.is_authenticated else [],
        'posts_context': posts_context,
        'user': request.user,
        'notifications': Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
                        if request.user.is_authenticated else [],
    }

    if request.user.is_authenticated:
        context.update({
            'link1': "account/logout/",
            "page1": 'Выход',
            'link2': "",
            "page2": ''
        })
    context['images'] = {p.id: p.images.split(',')[0] for p in results}
    context['len'] = len(results)

    return render(request, "index.html", context)

def get_subscribed_authors(user):
    if not user.is_authenticated:
        return []
    return Subscription.objects.filter(user1=user).values_list('user2', flat=True)

def delete_post(request):
    if can_act(request.user):
        question = Question.objects.filter(id=request.GET.get('id')).first()
        if question:
            question.delete()
        page = request.GET.get('to', '/')
        return redirect(page)
    return redirect('/')


def change_rating(request, question, x):
    like_obj = Like.objects.filter(user=request.user, question=question)[0]
    if x > 0:
        if like_obj.rating == 0:
            like_obj.rating += 1
            like_obj.save()
            question.rating += 1
            question.save()
        elif like_obj.rating == -1:
            like_obj.rating += 2
            like_obj.save()
            question.rating += 2
            question.save()
        elif like_obj.rating == 1:
            like_obj.rating = 0
            like_obj.save()
            question.rating -= 1
            question.save()
    elif x < 0:
        if like_obj.rating == 1:
            like_obj.rating -= 2
            like_obj.save()
            question.rating -= 2
            question.save()
        elif like_obj.rating == 0:
            like_obj.rating -= 1
            like_obj.save()
            question.rating -= 1
            question.save()
        elif like_obj.rating == -1:
            like_obj.rating = 0
            like_obj.save()
            question.rating += 1
            question.save()


def _vote(request, delta):
    question_id = request.GET.get('id')
    if not question_id:
        return redirect('index')
    question = get_object_or_404(Question, id=question_id)
    like_obj, created = Like.objects.get_or_create(
        user=request.user, question=question,
        defaults={'rating': 0}
    )
    if created:
        like_obj.rating = delta
        question.rating += delta
    else:
        change_rating(request, question, delta)
    like_obj.save()
    question.save()
    page = request.GET.get('to', 'index')
    return redirect('/#question-' + str(question_id))


def like(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    if not request.user.active:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Вы заблокированы и не можете выполнять это действие'})
        return redirect('/')

    question_id = request.GET.get('id')
    question = get_object_or_404(Question, id=question_id)

    like_obj, created = Like.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'rating': 0}
    )

    if like_obj.rating == 1:
        like_obj.rating = 0
        question.rating -= 1
    elif like_obj.rating == 0:
        like_obj.rating = 1
        question.rating += 1
    elif like_obj.rating == -1:
        like_obj.rating = 1
        question.rating += 2

    like_obj.save()
    if question.author != request.user and like_obj.rating == 1:
        Notification.objects.create(
            user=question.author,
            text=f'{request.user.username} оценил ваш пост',
            link=f'/question/{question.id}/'
        )
    question.save()

    # ВСЕГДА возвращаем JSON для AJAX запросов
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': question.rating,
            'user_rating': like_obj.rating,
        })

    return redirect(request.GET.get('to', '/'))


def dislike(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    if not request.user.active:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Вы заблокированы и не можете выполнять это действие'})
        return redirect('/')

    question_id = request.GET.get('id')
    question = get_object_or_404(Question, id=question_id)

    like_obj, created = Like.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'rating': 0}
    )

    if like_obj.rating == -1:
        like_obj.rating = 0
        question.rating += 1
    elif like_obj.rating == 0:
        like_obj.rating = -1
        question.rating -= 1
    elif like_obj.rating == 1:
        like_obj.rating = -1
        question.rating -= 2

    like_obj.save()
    question.save()

    # ВСЕГДА возвращаем JSON для AJAX запросов
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': question.rating,
            'user_rating': like_obj.rating,
        })

    return redirect(request.GET.get('to', '/'))


def sidebar_page(request):
    context = {}

    if request.user.is_authenticated:
        subscriptions = Subscription.objects.filter(user1=request.user)
    else:
        subscriptions = []

    context['subscriptions'] = subscriptions

    return render(request, template_name="sidebar.html", context=context)