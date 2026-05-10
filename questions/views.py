import uuid, datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from sentence_transformers import SentenceTransformer
from notifications.models import Notification
from questions.forms import *
from questions.models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from users.models import Subscription
# Create your views here.

def get_question_context(question_id):
    question = get_object_or_404(Question, pk=question_id)
    comments = Comment.objects.filter(question=question).prefetch_related('answer_set')
    question_images = list(question.images.split(",")) if question.images else []
    return {
        'question': question,
        'question_images': question_images,
        'comments': comments,
    }


def question_themes_page(request):
    return render(request, template_name="questions.html")


def question_page(request, question_id, template_name='question.html'):
    context = get_question_context(question_id)
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
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
            if question.author != request.user:
                Notification.objects.create(
                    user=question.author,
                    text=f'{request.user.username} оставил комментарий к вашему посту',
                    link=f'/question/{question.id}/'
                )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})

        return redirect('question', question_id=question_id)
    else:
        form = CommentForm()
    context['comment_form'] = form
    context_for_update = {
        'question_rating': context['question'].rating,
        'question_title': context['question'].title,
        'question_description': context['question'].description,
    }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "group",
        {
            "type": "send_data",
            "message": context_for_update
        }
    )
    context['subscriptions'] = Subscription.objects.filter(user1=request.user)
    return render(request, template_name=template_name, context=context)


def question_make_page(request):
    context = {}

    if request.user.is_authenticated:
        if request.user.active:
            if request.method == "POST":
                form = QuestionForm(request.POST)

                if form.is_valid():
                    model = SentenceTransformer("my_local_model", local_files_only=True)

                    time = datetime.datetime.now()
                    title = form.cleaned_data['title']
                    description = form.cleaned_data['description']

                    images = request.FILES.getlist('images')
                    print('FILES:', request.FILES)
                    print('IMAGES:', images)

                    image_paths = []
                    text = f"{title}\n{description}"
                    embeddings = model.encode([text])[0]

                    for image in images:
                        ext = image.name.split('.')[-1]
                        filename = f"question_images/{uuid.uuid4()}.{ext}"
                        path = default_storage.save(filename, ContentFile(image.read()))
                        image_paths.append(path)

                    images_str = ','.join(image_paths)

                    question = Question(
                        title=title,
                        description=description,
                        rating=0,
                        creation_date=time,
                        images=images_str,
                        author=request.user,
                    )

                    question.set_embedding(embeddings)
                    question.save()

                    return redirect('/')

            else:
                form = QuestionForm()

            context['form'] = form
        else:
            return redirect('/')
    else:
        return redirect('/account/login')
    context['subscriptions'] = Subscription.objects.filter(user1=request.user)
    return render(request, template_name='make_edit_question.html', context=context)

def question_edit_page(request):
    if not request.user.is_authenticated:
        return redirect('/account/login')

    question_id = request.GET.get('id')
    question = get_object_or_404(Question, id=question_id)

    if question.author != request.user:
        return redirect('/')

    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)

        if form.is_valid():
            question.title = form.cleaned_data['title']
            question.description = form.cleaned_data['description']

            images = request.FILES.getlist('images')

            if images:
                image_paths = []

                for image in images:
                    ext = image.name.split('.')[-1]
                    filename = f"question_images/{uuid.uuid4()}.{ext}"
                    path = default_storage.save(filename, ContentFile(image.read()))
                    image_paths.append(path)

                question.images = ','.join(image_paths)

            question.save()

            return redirect('question', question_id=question.id)

    else:
        form = QuestionForm(initial={
            'title': question.title,
            'description': question.description,
        })

    context = {
        'form': form,
        'question': question,
        'is_edit': True,
    }
    context['subscriptions'] = Subscription.objects.filter(user1=request.user)
    return render(request, 'make_edit_question.html', context)


def themes_page(request):


    return render(request, template_name="themes.html")

def make_comment_page(request, question_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data['text']
                rating = 0
                author = request.user
                creation_date = datetime.datetime.now()
                question = get_object_or_404(Question, pk=question_id)
                comment = Comment(text=text, rating=rating, author=author, creation_date=creation_date,
                                  question=question)
                comment.save()
                return redirect('/')
            else:
                form = CommentForm()
                return render(request, 'make_comment_answer.html', {'form': form})

        else:
            form = CommentForm()
            return render(request, 'make_comment_answer.html', {'form': form})
    else:
        return redirect('/account/login')



def like_comment(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    comment_id = request.GET.get('id')
    comment = get_object_or_404(Comment, id=comment_id)

    like_obj, created = CommentLike.objects.get_or_create(
        author=request.user,
        comment=comment,
        defaults={'rating': 0, 'created_at': datetime.datetime.now()}
    )

    if like_obj.rating == 1:
        like_obj.rating = 0
        comment.rating -= 1
    elif like_obj.rating == 0:
        like_obj.rating = 1
        comment.rating += 1
    elif like_obj.rating == -1:
        like_obj.rating = 1
        comment.rating += 2

    like_obj.save()
    comment.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': comment.rating,
            'user_rating': like_obj.rating

        })

    return redirect(request.GET.get('to', '/'))


def dislike_comment(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    comment_id = request.GET.get('id')
    comment = get_object_or_404(Comment, id=comment_id)

    like_obj, created = CommentLike.objects.get_or_create(
        author=request.user,
        comment=comment,
        defaults={'rating': 0, 'created_at': datetime.datetime.now()}
    )

    if like_obj.rating == -1:
        like_obj.rating = 0
        comment.rating += 1
    elif like_obj.rating == 0:
        like_obj.rating = -1
        comment.rating -= 1
    elif like_obj.rating == 1:
        like_obj.rating = -1
        comment.rating -= 2

    like_obj.save()
    comment.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({

            'ok': True,
            'rating': comment.rating,
            'user_rating': like_obj.rating

            })

    return redirect(request.GET.get('to', '/'))


def make_answer_page(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('/account/login/')

    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        text = request.POST.get('text')

        if text:
            answer = Answer(
                answer=text,
                rating=0,
                author=request.user,
                creation_date=datetime.datetime.now(),
                comment=comment
            )
            answer.save()
            if comment.author != request.user:
                Notification.objects.create(
                    user=comment.author,
                    text=f'{request.user.username} ответил на ваш комментарий',
                    link=f'/question/{comment.question.id}/#comment-{comment.id}'
                )

    return redirect('/question/' + str(comment.question.id) + '/')

def like_answer(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    answer_id = request.GET.get('id')
    answer = get_object_or_404(Answer, id=answer_id)

    like_obj, created = AnswerLike.objects.get_or_create(
        author=request.user,
        answer=answer,
        defaults={'rating': 0, 'created_at': datetime.datetime.now()}
    )

    if like_obj.rating == 1:
        like_obj.rating = 0
        answer.rating -= 1
    elif like_obj.rating == 0:
        like_obj.rating = 1
        answer.rating += 1
    elif like_obj.rating == -1:
        like_obj.rating = 1
        answer.rating += 2

    like_obj.save()
    answer.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': answer.rating,
            'user_rating': like_obj.rating,
        })

    return redirect(request.GET.get('to', '/question/' + str(answer.comment.question.id) + '/'))


def dislike_answer(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')

    answer_id = request.GET.get('id')
    answer = get_object_or_404(Answer, id=answer_id)

    like_obj, created = AnswerLike.objects.get_or_create(
        author=request.user,
        answer=answer,
        defaults={'rating': 0, 'created_at': datetime.datetime.now()}
    )

    if like_obj.rating == -1:
        like_obj.rating = 0
        answer.rating += 1
    elif like_obj.rating == 0:
        like_obj.rating = -1
        answer.rating -= 1
    elif like_obj.rating == 1:
        like_obj.rating = -1
        answer.rating -= 2

    like_obj.save()
    answer.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': answer.rating,
            'user_rating': like_obj.rating

        })

    return redirect(request.GET.get('to', '/question/' + str(answer.comment.question.id) + '/'))