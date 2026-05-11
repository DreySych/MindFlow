from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.utils import timezone

def smart_time(value):
    now = timezone.now()
    diff = now - value

    minutes = int(diff.total_seconds() // 60)
    hours = int(diff.total_seconds() // 3600)
    days = diff.days

    if minutes < 1:
        return 'только что'
    if minutes < 60:
        return f'{minutes} мин. назад'
    if hours < 24:
        return f'{hours} ч. назад'
    if days <= 7:
        return f'{days} дн. назад'

    return value.strftime('%d.%m.%Y')

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]

    data = []

    for notification in notifications:
        data.append({
            'id': notification.id,
            'text': notification.text,
            'link': notification.link,
            'is_read': notification.is_read,
            'created_at': smart_time(notification.created_at),
        })

    return JsonResponse({
        'notifications': data
    })


@login_required
def notifications_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({
        'count': count
    })


@login_required
def read_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)

    return redirect('/')