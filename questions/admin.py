from django.contrib import admin

from complaints.models import Complaint
from users.models import Subscription
from .models import Question, Answer, Comment, User, AnswerLike, QuestionLike, CommentLike

models = (Question, Answer, Comment, User, Subscription, AnswerLike, QuestionLike, CommentLike, Complaint)
admin.site.register(models)
