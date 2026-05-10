from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince
from .models import Notification


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
            'created_at': timesince(notification.created_at) + ' назад',
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