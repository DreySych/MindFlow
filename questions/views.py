import uuid, datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from sentence_transformers import SentenceTransformer

from questions.forms import *
from questions.models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
    return render(request, template_name=template_name, context=context)


def question_make_page(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                model = SentenceTransformer("my_local_model", local_files_only=True)
                time = datetime.datetime.now()
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                images = request.FILES.getlist('images')
                image_paths = []
                text = f"{title}\n{description}"
                embeddings = model.encode([text])[0]
                for image in images:
                    ext = image.name.split('.')[-1]
                    filename = f"question_images/{uuid.uuid4()}.{ext}"
                    path = default_storage.save(filename, ContentFile(image.read()))
                    image_paths.append(path)
                images_str = ','.join(image_paths)

                question = Question(title=title, description=description, rating=0,
                                    creation_date=time, images=images_str, author=request.user, )
                question.set_embedding(embeddings)
                question.save()

                # for tag_title in tags:
                #     if len(Tag.objects.filter(title=tag_title)) == 0:
                #         tag = Tag(title=tag_title)
                #         tag.save()
                #         link = PostToTag(question=question, tag=tag)
                #         link.save()

        else:
            form = QuestionForm()

        context['form'] = form
    else:
        return redirect('/account/login')

    return render(request, template_name='make_edit_question.html', context=context)


def question_edit_page(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                images = request.FILES.getlist('images')
                image_paths = []
                for image in images:
                    ext = image.name.split('.')[-1]
                    filename = f"question_images/{uuid.uuid4()}.{ext}"
                    path = default_storage.save(filename, ContentFile(image.read()))
                    image_paths.append(path)
                images_str = ','.join(image_paths)

                question = Question.objects.filter(id=request.GET.get('id'))[0]
                question.title = title
                question.description = description
                question.images = images_str
                question.save()
        else:
            form = QuestionForm()

        context['form'] = form
    else:
        return redirect('/account/login')

    return render(request, template_name='make_edit_question.html', context=context)


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

def make_answer_page(request, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.method == "POST":
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer_text = form.cleaned_data['text']
                answer = Answer(
                    answer=answer_text,
                    rating=0,
                    author=request.user,
                    creation_date=datetime.datetime.now(),
                    comment=comment
                )
                answer.save()
                return redirect('/')
        return redirect('/')
    return redirect('/account/login')