from django.contrib import admin

from users.models import Subscription
from .models import Question, Answer, Comment, User, AnswerLike, QuestionLike, CommentLike

models = (Question, Answer, Comment, User, Subscription, AnswerLike, QuestionLike, CommentLike)
admin.site.register(models)
