import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from notifications.models import Notification
from main.model_loader import get_model
from questions.forms import CommentForm, QuestionForm
from questions.models import (
    Answer,
    AnswerLike,
    Comment,
    CommentLike,
    Like,
    Question,
)
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from users.models import Subscription
from django.utils import timezone
import logging

logger = logging.getLogger('project')


def can_act(user):
    """Проверяет, авторизован ли пользователь и не заблокирован."""
    return user.is_authenticated and user.active


def get_question_context(question_id):
    """Возвращает словарь с вопросом, комментариями и изображениями по ID."""
    question = Question.objects.filter(pk=question_id).first()
    if question is None:
        return None
    comments = Comment.objects.filter(question=question).prefetch_related('answer_set')
    question_images = list(question.images.split(",")) if question.images else []
    return {
        'question': question,
        'question_images': question_images,
        'comments': comments,
    }


def process_comment(request, question):
    """Обрабатывает POST-запрос с комментарием и создаёт уведомление автору вопроса."""
    if not can_act(request.user):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': False,
                'error': 'Вы заблокированы и не можете выполнять это действие'
            })
        return redirect('/')
    form = CommentForm(request.POST)
    if form.is_valid() and request.user.is_authenticated:
        comment = Comment(
            text=form.cleaned_data['text'],
            author=request.user,
            question=question,
            creation_date=timezone.now(),
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
        if form.is_valid():
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'error': 'Комментарий не может быть пустым'})

    return redirect('question', question_id=question.id)


def build_question_context(question, request):
    """Формирует полный контекст для вопроса с рейтингами лайков и подписками."""
    comments = Comment.objects.filter(question=question).prefetch_related('answer_set')
    question_images = list(question.images.split(",")) if question.images else []
    context = {
        'question': question,
        'question_images': question_images,
        'comments': comments,
    }
    if request.user.is_authenticated:
        user_like = Like.objects.filter(user=request.user, question=question).first()
        context['user_rating'] = user_like.rating if user_like else 0
    else:
        context['user_rating'] = 0

    for comment in context['comments']:
        if request.user.is_authenticated:
            comment_like = CommentLike.objects.filter(
                author=request.user,
                comment=comment
            ).first()
            comment.user_rating = comment_like.rating if comment_like else 0

            for answer in comment.answer_set.all():
                answer_like = AnswerLike.objects.filter(
                    author=request.user,
                    answer=answer
                ).first()
                answer.user_rating = answer_like.rating if answer_like else 0
        else:
            comment.user_rating = 0
            for answer in comment.answer_set.all():
                answer.user_rating = 0

    if request.user.is_authenticated:
        context['subscriptions'] = Subscription.objects.filter(user1=request.user)
    else:
        context['subscriptions'] = []
    return context


def question_themes_page(request):
    """Отображает страницу с темами вопросов."""
    return render(request, template_name="questions.html")


def question_page(request, question_id, template_name='question.html'):
    """Страница конкретного вопроса: GET – показ, POST – добавление комментария."""
    context = get_question_context(question_id)
    if context is None:
        return redirect('/')
    question = context['question']

    if request.method == 'POST':
        return process_comment(request, question)

    form = CommentForm()
    context['comment_form'] = form
    context.update(build_question_context(question, request))

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "group",
        {
            "type": "send_data",
            "message": {
                'question_rating': question.rating,
                'question_title': question.title,
                'question_description': question.description,
            }
        }
    )
    return render(request, template_name, context=context)


def save_uploaded_images(images):
    """Сохраняет загруженные изображения в хранилище и возвращает строку с путями через запятую."""
    image_paths = []
    for image in images:
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']

        if image.content_type not in allowed_types:
            continue

        if image.size > 5 * 1024 * 1024:
            continue
        ext = image.name.split('.')[-1]
        filename = f"question_images/{uuid.uuid4()}.{ext}"
        path = default_storage.save(filename, ContentFile(image.read()))
        image_paths.append(path)
    return ','.join(image_paths)


def create_question_from_form(form, request):
    """Создаёт новый вопрос из формы, генерирует эмбеддинги и сохраняет изображения."""
    model = get_model()
    title = form.cleaned_data['title']
    description = form.cleaned_data['description']
    tag = form.cleaned_data['tag']
    images = request.FILES.getlist('images')
    if len(images) > 10:
        images = images[:10]
    logger.debug('Uploaded files for question: %s', request.FILES)
    logger.info('Question images count: %s', len(images))

    text = f"{title}\n{description}"
    embeddings = model.encode([text])[0]

    images_str = save_uploaded_images(images) if images else ''

    question = Question(
        title=title,
        description=description,
        tag=tag,
        rating=0,
        creation_date=timezone.now(),
        images=images_str,
        author=request.user,
    )
    question.set_embedding(embeddings)
    question.save()
    logger.info('Question created: id=%s, author=%s', question.id, request.user.username)
    return question


def update_question_from_form(question, form, request):
    """Обновляет существующий вопрос данными из формы."""
    question.title = form.cleaned_data['title']
    question.description = form.cleaned_data['description']
    question.tag = form.cleaned_data['tag']

    images = request.FILES.getlist('images')
    if images:
        question.images = save_uploaded_images(images)
    question.save()
    logger.info('Question edited: id=%s, author=%s', question.id, request.user.username)
    return question


def get_available_tags(request):
    with open('questions/available_tags.txt', mode='r', encoding='utf-8') as file:
        available_tags = [
            tag.strip()
            for tag in file.read().splitlines()
            if tag.strip()
        ]
    logger.info('Available tags requested')
    return JsonResponse(available_tags, safe=False)


def question_make_page(request):
    """Страница создания нового вопроса (только для авторизованных)."""
    if not request.user.is_authenticated:
        return redirect('/account/login')
    if not request.user.active:
        return redirect('/')

    context = {}
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info(
                'User %s creating question with tag %s',
                request.user.username,
                form.cleaned_data['tag']
            )
            question = create_question_from_form(form, request)
            return redirect(f'/profile/{request.user.username}/#question-{question.id}')
    else:
        form = QuestionForm()
    context['form'] = form
    if request.user.is_authenticated:
        context['subscriptions'] = Subscription.objects.filter(user1=request.user)
    else:
        context['subscriptions'] = []
    return render(request, 'make_edit_question.html', context=context)


def question_edit_page(request):
    """Страница редактирования вопроса (только автор вопроса)."""
    if not can_act(request.user):
        return redirect('/')

    question_id = request.GET.get('id')
    question = get_object_or_404(Question, id=question_id)

    if question.author != request.user:
        return redirect('/')

    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info(
                'User %s editing question %s',
                request.user.username,
                question.id
            )
            update_question_from_form(question, form, request)
            return redirect(f'/profile/{request.user.username}/#question-{question.id}')
    else:
        form = QuestionForm(initial={
            'title': question.title,
            'description': question.description,
            'tag': question.tag,
        })

    context = {
        'form': form,
        'question': question,
        'is_edit': True,
        'question_images': question.images.split(',') if question.images else [],
    }
    if request.user.is_authenticated:
        context['subscriptions'] = Subscription.objects.filter(user1=request.user)
    else:
        context['subscriptions'] = []
    return render(request, 'make_edit_question.html', context=context)


def themes_page(request):
    """Отображает страницу с темами."""
    return render(request, template_name="themes.html")


def make_comment_page(request, question_id):
    """Страница создания комментария к вопросу."""
    if not can_act(request.user):
        return redirect('/account/login')
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                text=form.cleaned_data['text'],
                rating=0,
                author=request.user,
                creation_date=timezone.now(),
                question=get_object_or_404(Question, pk=question_id)
            )
            return redirect('/')
        else:
            form = CommentForm()
            return render(request, 'make_comment_answer.html', {'form': form})
    else:
        form = CommentForm()
        return render(request, 'make_comment_answer.html', {'form': form})


def generic_like_dislike(request, model_class, like_model, obj_id_field, obj_name):
    """Универсальная функция для лайков/дизлайков комментариев и ответов."""
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'login': '/account/login/'})
        return redirect('/account/login/')
    if not request.user.active:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Вы заблокированы и не можете выполнять это действие'})
        return redirect('/')

    obj_id = request.GET.get('id')
    obj = get_object_or_404(model_class, id=obj_id)

    like_obj, created = like_model.objects.get_or_create(
        author=request.user,
        **{obj_id_field: obj},
        defaults={'rating': 0, 'created_at': timezone.now()}
    )

    is_like = '/like/' in request.path
    delta = 1 if is_like else -1

    if (delta == 1 and like_obj.rating == 1) or (delta == -1 and like_obj.rating == -1):
        like_obj.rating = 0
        obj.rating -= delta
    elif like_obj.rating == 0:
        like_obj.rating = delta
        obj.rating += delta
    elif (delta == 1 and like_obj.rating == -1) or (delta == -1 and like_obj.rating == 1):
        like_obj.rating = delta
        obj.rating += 2 * delta

    like_obj.save()
    obj.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'rating': obj.rating,
            'user_rating': like_obj.rating,
        })
    return redirect(request.GET.get('to', '/'))


def like_comment(request):
    """Лайк комментария."""
    return generic_like_dislike(
        request,
        Comment,
        CommentLike,
        'comment',
        'like'
    )


def dislike_comment(request):
    """Дизлайк комментария."""
    return generic_like_dislike(
        request,
        Comment,
        CommentLike,
        'comment',
        'dislike'
    )


def like_answer(request):
    """Лайк ответа на комментарий."""
    return generic_like_dislike(
        request,
        Answer,
        AnswerLike,
        'answer',
        'like'
    )


def dislike_answer(request):
    """Дизлайк ответа на комментарий."""
    return generic_like_dislike(
        request,
        Answer,
        AnswerLike,
        'answer',
        'dislike'
    )


def make_answer_page(request, comment_id):
    """Страница создания ответа на комментарий (обрабатывает POST и уведомления)."""
    if not can_act(request.user):
        return redirect('/')

    comment = get_object_or_404(Comment, id=comment_id)
    text = ''

    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        logger.info(
            'User %s answered comment %s',
            request.user.username,
            comment.id
        )
        if text:
            Answer.objects.create(
                answer=text,
                rating=0,
                author=request.user,
                creation_date=timezone.now(),
                comment=comment
            )

            if comment.author != request.user:
                Notification.objects.create(
                    user=comment.author,
                    text=f'{request.user.username} ответил на ваш комментарий',
                    link=f'/question/{comment.question.id}/#comment-{comment.id}'
                )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if text:
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'error': 'Ответ не может быть пустым'})

    return redirect('/question/' + str(comment.question.id) + '/')


def question_card(request):
    """Рендерит карточку вопроса (шаблон questions.html)."""
    return render(request, template_name="questions.html")


def delete_question(request, question_id):
    """Удаляет вопрос (POST) с проверкой прав и очисткой изображений."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Только POST'})
    if not can_act(request.user):
        return JsonResponse({'ok': False, 'error': 'Нет доступа'})
    question = get_object_or_404(Question, id=question_id)
    if question.author != request.user and not request.user.is_staff:
        return JsonResponse({'ok': False, 'error': 'Нет прав'})
    if question.images:
        for path in question.images.split(','):
            if path and default_storage.exists(path):
                default_storage.delete(path)
    logger.warning(
        'Question deleted: id=%s by user=%s',
        question.id,
        request.user.username
    )
    question.delete()
    return JsonResponse({'ok': True})
