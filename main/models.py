from django.db import models

# Кирилл, Женя!
# -----> Сюда все модели

class User(models.Model):
    username = models.TextField()
    password = models.CharField(max_length=128)
    email = models.TextField()
    name = models.TextField()
    surname = models.TextField()
    sex = models.IntegerField()
    level = models.TextField()
    reputation = models.IntegerField()
    role = models.TextField()
    birth_date = models.DateField()
    registration_date = models.DateField()
    image = models.TextField()

class Question(models.Model):
    title = models.TextField()
    description = models.TextField()
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    views = models.IntegerField()
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    close_date = models.DateTimeField()
    tags = models.TextField()
    images = models.TextField()
    theme = models.TextField()

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
