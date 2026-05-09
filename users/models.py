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
    sex = models.IntegerField(null=True)
    reputation = models.IntegerField()
    role = models.TextField()
    birth_date = models.DateField(null=True)
    registration_date = models.DateField()
    image = models.ImageField(null=True)
    is_staff = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "sex", "role", "birth_date", "registration_date", "reputation"]

class Subscription(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')