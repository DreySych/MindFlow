from django.contrib import admin

from users.models import Subscription
from .models import Question, Answer, Comment, User

models = (Question, Answer, Comment, User, Subscription)
admin.site.register(models)
