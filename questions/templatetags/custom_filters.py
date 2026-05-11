from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def smart_time(value):
    if not value:
        return ''

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