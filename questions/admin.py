from django.contrib import admin
from .models import Question, Answer, Comment, Tag, PostToTag, Complaint, User

models = (Question, Answer, Comment, Tag, PostToTag, Complaint, User)
admin.site.register(models)
