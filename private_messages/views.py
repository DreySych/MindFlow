from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from users.models import User
from .models import Message


def chat_page(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/account/login/')

    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        text = request.POST.get('text')

        if text:
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