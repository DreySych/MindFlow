from django.contrib import admin
from .models import Question, Answer, Comment, User

models = (Question, Answer, Comment, User)
admin.site.register(models)
