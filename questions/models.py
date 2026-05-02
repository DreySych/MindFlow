from django.db import models
from django.db.models import CASCADE
from users.models import User

# Create your models here.

class Question(models.Model):
    title = models.TextField()
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    images = models.TextField()
    rating = models.IntegerField()

class Comment(models.Model):
    text = models.TextField()
    rating = models.IntegerField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Answer(models.Model):
    answer = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    creation_date = models.DateTimeField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

# class Tag(models.Model):
#     title = models.TextField()

# class PostToTag(models.Model):
#     question = models.ForeignKey(Question, on_delete=CASCADE)
#     tag = models.ForeignKey(Tag, on_delete=CASCADE)