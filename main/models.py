from django.db import models

# Кирилл, Женя!
# -----> Сюда все модели

#УБРАТЬ
#МОДЕЛИ ТУТ - ЭТО ПОЛНАЯ КОПИРКА DATABASE ВЕТКИ
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