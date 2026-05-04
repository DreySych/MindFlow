from django.shortcuts import render, redirect
from questions.forms import *
import datetime
from questions.models import *

# Create your views here.
def question_page(request):
    return render(request, template_name="question.html")

def question_make_page(request):
    return render(request, template_name='make_question.html')

def question_edit_page(request):
    return render(request, template_name='edit_question.html')
