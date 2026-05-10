from django.shortcuts import render, redirect, get_object_or_404
import datetime

from django.template.context_processors import request


from main.forms import SearchForm
from main.model_loader import get_model
from questions.forms import CommentForm
from questions.models import Question, Like, Comment
from questions.views import get_question_context
from users.models import User, Subscription
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse

# Create your views here.
def index_page(request):
    username = request.user.username if request.user.is_authenticated else "Профиль"
    all_users = User.objects .all()
    model = get_model()
    if request.method == "POST" and 'question_id' in request.POST:
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, pk=question_id)
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            text = form.cleaned_data['text']
            comment = Comment(
                text=text,
                author=request.user,
                question=question,
                creation_date=datetime.datetime.now(),
                rating=0
            )
            comment.save()
        return redirect('index')

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            model = get_model()
            input_text = model.encode([form.cleaned_data['input_text']])[0]
            questions = Question.objects.all()
            results = []
            for question in questions:
                question_vec = question.get_embedding()
                if question_vec is not None:
                    sim = model.similarity([question_vec], [input_text])[0][0]
                    results.append((question, sim))
                else:
                    results.append((question, -1))
            results = sorted(results, key=lambda x: x[1], reverse=True)
            results = [q for q, _ in results]
        else:
            results = get_default_questions(request)
    else:
        results = get_default_questions(request)

    posts_context = []
    for post in results:
        post_context = get_question_context(post.pk)
        post_context['comment_form'] = CommentForm()
        posts_context.append(post_context)
    context = {
        "username": username,
        "users": all_users,
        "link1": "account/login/",
        "page1": 'Логин',
        "link2": "account/signup/",
        "page2": 'Регистрация'
    }
    if request.user.is_authenticated:
        context['link1'] = "account/logout/"
        context["page1"] = 'Выход'
        context['link2'] = ""
        context["page2"] = ''


    context['posts_context'] = posts_context
    context['user'] = request.user
    images = {}
    for i in results:
        images[f'{i.id}'] = i.images.split(',')[0]
    context['images'] = images
    context['len'] = len(results)

    return render(request, template_name="index.html", context=context)

def get_subscribed_authors(user):
    if not user.is_authenticated:
        return []
    return Subscription.objects.filter(user1=user).values_list('user2', flat=True)

def get_default_questions(request):
    if not request.user.is_authenticated:
        return Question.objects.all().order_by('-rating', '-creation_date')

    friends_ids = Subscription.objects.filter(
        user1=request.user
    ).values_list('user2_id', flat=True)

    fresh_friends_posts = Question.objects.filter(
        author_id__in=friends_ids
    ).order_by('-creation_date')[:5]

    popular_all_posts = Question.objects.exclude(
        id__in=[post.id for post in fresh_friends_posts]
    ).order_by('-rating', '-creation_date')

    popular_friends_posts = Question.objects.filter(
        author_id__in=friends_ids
    ).exclude(
        id__in=[post.id for post in fresh_friends_posts]
    ).order_by('-rating', '-creation_date')

    result = list(fresh_friends_posts)

    all_posts = list(popular_all_posts)
    friends_posts = list(popular_friends_posts)

    max_len = max(len(all_posts), len(friends_posts))

    for i in range(max_len):
        if i < len(friends_posts):
            result.append(friends_posts[i])

        if i < len(all_posts):
            result.append(all_posts[i])

    final_result = []
    used_ids = []

    for post in result:
        if post.id not in used_ids:
            final_result.append(post)
            used_ids.append(post.id)

    return final_result

def delete_post(request):
    if request.user.is_authenticated:
        question = Question.objects.filter(id=request.GET.get('id'))[0]
        question.delete()
        page = request.GET.get('to')
        return redirect(page)
    else:
        return redirect('/account/login')


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
    question.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': question.rating
        })

    return redirect(request.GET.get('to', '/'))


def dislike(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': question.rating
        })

    return redirect(request.GET.get('to', '/'))

def sidebar_page(request):
    context = {}

    subscriptions = Subscription.objects.filter(user1=request.user)
    context['subscriptions'] = subscriptions

    return render(request, template_name="sidebar.html", context=context)



