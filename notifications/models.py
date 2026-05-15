from django.db import models
from users.models import User


class Notification(models.Model):
    """Уведомление для пользователя."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.text}'


def create_notification(user, text, link=''):
    """Создаёт уведомление, если пользователь существует."""
    if not user:
        return None

    return Notification.objects.create(
        user=user,
        text=text,
        link=link
    )
