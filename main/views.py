from django.shortcuts import render, redirect, get_object_or_404

from notifications.models import Notification
from main.model_loader import get_model
from questions.forms import CommentForm
from questions.models import Question, Like, Comment
from questions.views import get_question_context
from users.models import User, Subscription
from django.http import JsonResponse
from django.utils import timezone
from django.template.loader import render_to_string


def can_act(user):
    return user.is_authenticated and user.active


def build_post_context(post, request):
    ctx = get_question_context(post.pk)
    ctx['comment_form'] = CommentForm()
    if request.user.is_authenticated:
        user_like = Like.objects.filter(
            user=request.user, question=post).first()
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

        if q_vec is not None:
            similarity = model.similarity([q_vec], [input_vec]).item()
        else:
            similarity = -1

        results.append((q, similarity))

    return [q for q, _ in sorted(results, key=lambda x: x[1], reverse=True)]


def get_default_questions(request):
    if not can_act(request.user):
        return Question.objects.all().order_by('-rating', '-creation_date')

    friends_ids = Subscription.objects.filter(
        user1=request.user).values_list('user2_id', flat=True)
    fresh_friends = Question.objects.filter(
        author_id__in=friends_ids).order_by('-creation_date')[:5]
    fresh_ids = [p.id for p in fresh_friends]

    popular_all = Question.objects.exclude(
        id__in=fresh_ids).order_by('-rating', '-creation_date')
    popular_friends = Question.objects.filter(
        author_id__in=friends_ids).exclude(
        id__in=fresh_ids).order_by(
            '-rating',
        '-creation_date')

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


def index_page(request):
    if request.method == "POST" and 'question_id' in request.POST:
        question = get_object_or_404(
            Question, pk=request.POST.get('question_id'))
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
    results = perform_search(
        search_text) if search_text else get_default_questions(request)
    page = int(request.GET.get('page', 1))
    per_page = 10

    start = (page - 1) * per_page
    end = start + per_page

    page_posts = results[start:end]
    has_more = len(results) > end

    posts_context = [build_post_context(p, request) for p in page_posts]
    context = {
        "username": request.user.username if request.user.is_authenticated else "Профиль",
        "users": User.objects.all(),
        "link1": "account/login/",
        "page1": 'Логин',
        "link2": "account/signup/",
        "page2": 'Регистрация',
        'subscriptions': Subscription.objects.filter(
            user1=request.user) if request.user.is_authenticated else [],
        'posts_context': posts_context,
        'has_more': has_more,
        'next_page': page + 1,
        'user': request.user,
        'notifications': Notification.objects.filter(
            user=request.user).order_by('-created_at')[
                :20] if request.user.is_authenticated else [],
    }

    if request.user.is_authenticated:
        context.update({
            'link1': "account/logout/",
            "page1": 'Выход',
            'link2': "",
            "page2": ''
        })
    context['images'] = {
        p.id: p.images.split(',')[0] if p.images else ''
        for p in results
    }
    context['len'] = len(results)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = ''
        for post_data in posts_context:
            html += render_to_string(
                'question_card.html',
                {
                    'question': post_data['question'],
                    'question_images': post_data['question_images'],
                    'comments': post_data['comments'],
                    'user_rating': post_data['user_rating'],
                    'request': request,
                    'user': request.user,
                }
            )

        return JsonResponse({
            'ok': True,
            'html': html,
            'has_more': has_more,
            'next_page': page + 1,
        })

    return render(request, "index.html", context)


def get_subscribed_authors(user):
    if not user.is_authenticated:
        return []
    return Subscription.objects.filter(
        user1=user).values_list(
        'user2', flat=True)


def vote_question(request, vote):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    if not request.user.active:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': False,
                'error': 'Вы заблокированы и не можете выполнять это действие'
            })
        return redirect('/')

    question_id = request.GET.get('id')
    question = get_object_or_404(Question, id=question_id)

    like_obj, created = Like.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'rating': 0}
    )

    old_rating = like_obj.rating

    if old_rating == vote:
        like_obj.rating = 0
    else:
        like_obj.rating = vote

    question.rating += like_obj.rating - old_rating

    like_obj.save()
    question.save()

    if question.author != request.user and old_rating != 1 and like_obj.rating == 1:
        Notification.objects.create(
            user=question.author,
            text=f'{request.user.username} оценил ваш пост',
            link=f'/question/{question.id}/'
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': question.rating,
            'user_rating': like_obj.rating,
        })

    return redirect(request.GET.get('to', '/'))


def like(request):
    return vote_question(request, 1)


def dislike(request):
    return vote_question(request, -1)


def sidebar_page(request):
    context = {}

    if request.user.is_authenticated:
        subscriptions = Subscription.objects.filter(user1=request.user)
    else:
        subscriptions = []

    context['subscriptions'] = subscriptions

    return render(request, template_name="sidebar.html", context=context)
