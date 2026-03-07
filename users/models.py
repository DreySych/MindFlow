from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# Create your models here.
class User(AbstractBaseUser):
    username = models.TextField(unique=True)
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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name", "surname", "sex", "level", "role", "birth_date", "registration_date", "reputation"]