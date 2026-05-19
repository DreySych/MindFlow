from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from datetime import timedelta
from django.utils import timezone
import random


class MyUserManager(BaseUserManager):
    """Менеджер пользователей для кастомной модели User."""

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя с нормализованным email и хешированным паролем."""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперпользователя с правами staff и superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с полями username, email, рейтингом и статусом."""

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
    REQUIRED_FIELDS = ["email", "sex", "role",
                       "birth_date", "registration_date", "reputation"]


class Subscription(models.Model):
    """Модель подписки пользователя user1 на user2."""

    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user2')


class RecoveryCode(models.Model):
    """Модель кода восстановления пароля с временной валидностью (10 минут)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.code}'

    @staticmethod
    def generate_code():
        """Генерирует случайный 6-значный цифровой код."""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    def create_for_user(user):
        """Создаёт новый код восстановления для пользователя, инвалидируя старые."""
        RecoveryCode.objects.filter(
            user=user, is_used=False).update(is_used=True)

        code = RecoveryCode.generate_code()
        recovery = RecoveryCode.objects.create(user=user, code=code)
        return recovery

    def is_valid(self):
        """Проверяет, не использован ли код и не истёк ли его срок действия (10 минут)."""
        if self.is_used:
            return False

        if timezone.now() > self.created_at + timedelta(minutes=10):
            return False

        return True