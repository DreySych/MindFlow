from django.shortcuts import render, redirect
import datetime

from django.template.context_processors import request

from sentence_transformers import SentenceTransformer
from main.forms import SearchForm
from questions.models import Question, Like
from users.models import User, Subscription
from django.contrib.auth.hashers import check_password, make_password


# Create your views here.
def index_page(request):
	username = request.user.username if request.user.is_authenticated else "Профиль"
	all_users = User.objects .all()
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			model = SentenceTransformer("my_local_model", local_files_only=True)
			input_text = model.encode([form.cleaned_data['input_text']])[0]
			questions = Question.objects.all()
			results = []
			for question in questions:
				question_vec = question.get_embedding()
				if question_vec is not None:
					sim = model.similarity([question_vec], [input_text])[0][0]
					results.append((question, sim))
				else:
					results.append((question, -1))
			results = sorted(results, key=lambda x: x[1], reverse=True)
			results = [q for q, _ in results]
		else:
			results = get_default_questions(request)
	else:
		results = get_default_questions(request)

	context = {
		"username": username,
		"users": all_users,
		"link1": "account/login/",
		"page1": 'Логин',
		"link2": "account/signup/",
		"page2": 'Регистрация'
	}
	if request.user.is_authenticated:
		context['link1'] = "account/logout/"
		context["page1"] = 'Выход'
		context['link2'] = ""
		context["page2"] = ''


	context['questions'] = results
	context['user'] = request.user
	images = {}
	for i in results:
		images[f'{i.id}'] = i.images.split(',')[0]
	context['images'] = images
	context['len'] = len(results)

	return render(request, template_name="index.html", context=context)

def get_default_questions(request):
	questions = []

	if request.user.is_authenticated:
		subscriptions = Subscription.objects.filter(user1=request.user)
		authors = []
		for i in subscriptions:
			authors.append(i.user2)
		question = Question.objects.filter(author__in=authors).order_by('-creation_date')
		for j in question:
			questions.append(j)
		question = Question.objects.exclude(author__in=authors).order_by('-creation_date')
		for j in question:
			questions.append(j)

	else:
		question = Question.objects.all().order_by('-creation_date')
		for i in question:
			questions.append(i)

	return questions

def delete_post(request):
	question = Question.objects.filter(id=request.GET.get('id'))[0]
	question.delete()
	page = request.GET.get('to')
	return redirect(page)

def change_rating(request, x):
	question = Question.objects.filter(id=request.GET.get('id'))[0]

	if len(Like.objects.filter(user=request.user, question=question)) == 0:
		question.rating += x
		question.save()
		Like(user=request.user, question=question, rating=x).save()
	else:
		like_obj = Like.objects.filter(user=request.user, question=question)[0]
		if x > 0:
			if like_obj.rating == 0:
				like_obj.rating += 1
				like_obj.save()
				question.rating += x
				question.save()
			elif like_obj.rating == -1:
				like_obj.rating += 2
				like_obj.save()
				question.rating += 2
				question.save()
			elif like_obj.rating == 1:
				like_obj.rating = 0
				like_obj.save()
				question.rating -= 1
				question.save()
		elif x < 0:
			if like_obj.rating == 1:
				like_obj.rating -= 2
				like_obj.save()
				question.rating -= 2
				question.save()
			elif like_obj.rating == 0:
				like_obj.rating -= 1
				like_obj.save()
				question.rating -= 1
				question.save()
			elif like_obj.rating == -1:
				like_obj.rating = 0
				like_obj.save()
				question.rating += 1
				question.save()

def like(request):
	change_rating(request, 1)
	page = request.GET.get('to')
	return redirect(page + f"#question-{request.GET.get('id')}")

def dislike(request):
	change_rating(request, -1)
	page = request.GET.get('to')
	return redirect(page + f"#question-{request.GET.get('id')}")

def sidebar_page(request):
	context = {}

	subscriptions = Subscription.objects.filter(user1=request.user)
	context['subscriptions'] = subscriptions

	return render(request, template_name="sidebar.html", context=context)


