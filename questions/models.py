from django.db import models
from django.db.models import CASCADE
from users.models import User

# Create your models here.

class Question(models.Model):
    title = models.TextField()
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField()
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField(null=True)
    close_date = models.DateTimeField(null=True)
    images = models.TextField()
    #theme = models.TextField()

class Answer(models.Model):
    answer = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    creation_date = models.DateTimeField()
    images = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Comment(models.Model):
    text = models.TextField()
    likes = models.IntegerField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)

class Tag(models.Model):
    title = models.TextField()

class PostToTag(models.Model):
    question = models.ForeignKey(Question, on_delete=CASCADE)
    tag = models.ForeignKey(Tag, on_delete=CASCADE)

class Complaint(models.Model):
    description = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=CASCADE)