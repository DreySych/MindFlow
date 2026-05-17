from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from users.models import User
from .models import Message


def get_dialog_messages(user, other_user):
    """Возвращает все сообщения между двумя пользователями."""
    return Message.objects.filter(
        Q(sender=user, receiver=other_user) |
        Q(sender=other_user, receiver=user)
    ).order_by('created_at')


def mark_messages_as_read(user, other_user):
    """Помечает входящие сообщения как прочитанные."""
    Message.objects.filter(
        sender=other_user,
        receiver=user,
        is_read=False
    ).update(is_read=True)


def create_message(sender, receiver, text):
    """Создаёт сообщение, если текст не пустой и пользователь не заблокирован."""
    text = (text or '').strip()

    if not text or not sender.active:
        return None

    return Message.objects.create(
        sender=sender,
        receiver=receiver,
        text=text
    )


def message_to_dict(message):
    """Преобразует сообщение в словарь для AJAX-ответа."""
    return {
        'text': message.text,
        'sender_id': message.sender_id,
        'time': message.created_at.strftime('%H:%M'),
    }


def chat_page(request, user_id):
    """Показывает страницу диалога и обрабатывает обычную отправку формы."""
    if not request.user.is_authenticated:
        return redirect('/account/login/')

    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        create_message(
            sender=request.user,
            receiver=other_user,
            text=request.POST.get('text')
        )
        return redirect('chat_page', user_id=other_user.id)

    messages = get_dialog_messages(request.user, other_user)
    mark_messages_as_read(request.user, other_user)

    return render(request, 'PM.html', {
        'other_user': other_user,
        'messages': messages,
    })


def chat_messages(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False})

    other_user = get_object_or_404(User, id=user_id)

    page = int(request.GET.get('page', 1))
    per_page = 20

    all_messages = get_dialog_messages(
        request.user,
        other_user
    ).order_by('-created_at')

    start = (page - 1) * per_page
    end = start + per_page

    messages = list(all_messages[start:end])

    has_more = all_messages.count() > end

    mark_messages_as_read(request.user, other_user)

    messages.reverse()

    return JsonResponse({
        'ok': True,
        'messages': [message_to_dict(m) for m in messages],
        'has_more': has_more,
        'next_page': page + 1,
    })
