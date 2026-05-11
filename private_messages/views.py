from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from users.models import User
from .models import Message
from django.http import JsonResponse

def chat_page(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/account/login/')

    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        text = request.POST.get('text')

        if text and request.user.active:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text
            )

        return redirect('chat_page', user_id=other_user.id)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'PM.html', {
        'other_user': other_user,
        'messages': messages
    })
def chat_messages(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False})

    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    data = []

    for message in messages:
        data.append({
            'text': message.text,
            'sender_id': message.sender.id,
            'time': message.created_at.strftime('%H:%M'),
        })

    return JsonResponse({
        'ok': True,
        'messages': data
    })