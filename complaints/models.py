from django.db import models

from questions.models import Answer, Comment, Question
from users.models import User


class Complaint(models.Model):
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, null=True, related_name='question')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='user')
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, related_name='comment')
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, null=True, blank=True)
