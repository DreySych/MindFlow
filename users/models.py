from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



# Create your models here.
class User(AbstractBaseUser, PermissionsMixin ):
    username = models.TextField(unique=True)
    password = models.CharField(max_length=128)
    email = models.TextField()
    name = models.TextField()
    surname = models.TextField()
    sex = models.IntegerField()
    #level = models.TextField()
    reputation = models.IntegerField()
    role = models.TextField()
    birth_date = models.DateField()
    registration_date = models.DateField()
    image = models.ImageField()
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name", "surname", "sex", "role", "birth_date", "registration_date", "reputation"]