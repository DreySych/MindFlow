from django.db import models
from users.models import *
from questions.models import *

class Complaint(models.Model):
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=CASCADE, null=True, related_name='question')
    user = models.ForeignKey(User, on_delete=CASCADE, null=True, related_name='user')
    comment = models.ForeignKey(Comment, on_delete=CASCADE, null=True, related_name='comment')