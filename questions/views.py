from django.shortcuts import render, redirect
from questions.forms import *
import datetime
from questions.models import *

# Create your views here.

def question_themes_page(request):
    return render(request, template_name="questions.html")

def question_page(request):
    return render(request, template_name="question.html")

def question_make_page(request):
	context = {}
	if request.user.is_authenticated:
		if request.method == "POST":
			form = QuestionForm(request.POST)
			time = datetime.datetime.now()
			title = form.data['title']
			description = form.data['description']
			tags = form.data['tags']
			theme = form.data['theme']
			images = form.data['images']

			question = Question(title=title, description=description, tags=tags, theme=theme,
								creation_date=time, views=0, images=images, author=request.user)
			question.save()
		else:
			form = QuestionForm()

		context['form'] = form
	else:
		return redirect('/account/login')

	return render(request, template_name='make_question.html', context=context)


def complaint_page(request):
    return render(request, template_name="complaint.html")

def themes_page(request):
    return render(request, template_name="themes.html")