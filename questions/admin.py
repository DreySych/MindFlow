from django.contrib import admin
from .models import Question, Answer, Comment, Tag, PostToTag, User

models = (Question, Answer, Comment, Tag, PostToTag, User)
admin.site.register(models)
