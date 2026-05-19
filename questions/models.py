from django.db import models
from users.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
import logging

logger = logging.getLogger('project')

# Create your models here.

class Question(models.Model):
    """Модель вопроса с заголовком, описанием, автором, рейтингом и эмбеддингом."""

    title = models.TextField()
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    images = models.TextField()
    rating = models.IntegerField()
    embedding = models.TextField(blank=True)
    tag = models.TextField(default='Другое')

    def set_embedding(self, vector):
        """Сохраняет вектор эмбеддинга в виде строки через запятую."""
        self.embedding = ",".join(map(str, vector))

    def get_embedding(self):
        """Возвращает эмбеддинг как список чисел или None."""
        return list(map(float, self.embedding.split(','))) if self.embedding else None

    @property
    def image_list(self):
        """Возвращает список путей к изображениям вопроса."""
        if not self.images:
            return [[]]
        images = []
        for i in self.images.split(','):
            images.append("media/" + i)

        logger.debug('Question image list: %s', images)

        return images


class Comment(models.Model):
    """Модель комментария к вопросу."""

    text = models.TextField()
    rating = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-rating', '-creation_date']


class Answer(models.Model):
    """Модель ответа на комментарий."""

    answer = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    creation_date = models.DateTimeField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-rating', 'creation_date']


class Like(models.Model):
    """Универсальная модель лайка (для вопроса, ответа или комментария)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=0)


class QuestionLike(models.Model):
    """Модель лайка/дизлайка вопроса."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        unique_together = ('author', 'question')


class AnswerLike(models.Model):
    """Модель лайка/дизлайка ответа."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        unique_together = ('author', 'answer')


class CommentLike(models.Model):
    """Модель лайка/дизлайка комментария."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=False)

    class Meta:
        unique_together = ('author', 'comment')


@receiver(post_save, sender=Question)
def announce_new_data(sender, instance, **kwargs):
    """Сигнал: при создании вопроса отправляет веб-сокет о новом посте."""
    channel_layer = get_channel_layer()

    context = {
        "question_description": instance.description,
        "question_title": instance.title,
        "question_rating": instance.rating,
        "event_type": "new_data",
    }

    async_to_sync(channel_layer.group_send)(
        "group",
        {
            "type": "send_data",
            "message": context,
        }
    )


@receiver(post_save, sender=Comment)
def announce_new_comment(sender, instance, created, **kwargs):
    """Сигнал: при создании комментария обновляет через веб-сокет список комментариев."""
    if created:
        channel_layer = get_channel_layer()

        question = instance.question
        all_comments = question.comment_set.all().order_by('-creation_date')
        html_content = render_to_string(
            'comments.html', {'comments': all_comments})

        async_to_sync(channel_layer.group_send)(
            "group",
            {
                "type": "send_data",
                "message": {
                    "html": html_content,
                    "event_type": "new_comment",
                    "question_id": question.id,
                    "count": all_comments.count(),
                }
            }
        )


@receiver(post_save, sender=Answer)
def announce_new_answer(sender, instance, created, **kwargs):
    """Сигнал: при создании ответа обновляет через веб-сокет список комментариев."""
    if created:
        channel_layer = get_channel_layer()

        question = instance.comment.question
        all_comments = question.comment_set.all().order_by('-creation_date')
        html_content = render_to_string(
            'comments.html', {'comments': all_comments})

        async_to_sync(channel_layer.group_send)(
            "group",
            {
                "type": "send_data",
                "message": {
                    "html": html_content,
                    "event_type": "new_answer",
                    "question_id": question.id,
                    "count": all_comments.count(),
                }
            }
        )


# class Tag(models.Model):
#     title = models.TextField()

# class PostToTag(models.Model):
#     question = models.ForeignKey(Question, on_delete=CASCADE)
#     tag = models.ForeignKey(Tag, on_delete=CASCADE)