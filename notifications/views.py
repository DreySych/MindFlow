from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import Notification


def smart_time(value):
    """Возвращает дату уведомления в коротком человекочитаемом виде."""
    diff = timezone.now() - value
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


def notification_to_dict(notification):
    """Преобразует уведомление в простой словарь для JSON."""
    return {
        'id': notification.id,
        'text': notification.text,
        'link': notification.link,
        'is_read': notification.is_read,
        'created_at': smart_time(notification.created_at),
    }


@login_required
def notifications_list(request):
    """Возвращает последние уведомления текущего пользователя."""
    notifications = Notification.objects.filter(user=request.user)[:10]
    data = [notification_to_dict(item) for item in notifications]
    return JsonResponse({'notifications': data})


@login_required
def notifications_count(request):
    """Возвращает количество непрочитанных уведомлений."""
    count = Notification.objects.filter(
        user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def read_notification(request, notification_id):
    """Помечает уведомление прочитанным и переводит по его ссылке."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if notification.link:
        return redirect(notification.link)
    return redirect('/')
