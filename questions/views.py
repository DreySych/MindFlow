import uuid, datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from questions.forms import *
from questions.models import *


# Create your views here.

def question_themes_page(request):
	return render(request, template_name="questions.html")


def question_page(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	answers = Answer.objects.filter(question=question)
	comments = Comment.objects.filter(question=question)
	question_images = list(question.images.split(","))
	context = {
		'question': question,
		'question_images': question_images,
		'answers': answers,
		'comments': comments
	}
	return render(request, 'question.html', context)


def question_make_page(request):
	context = {}
	if request.user.is_authenticated:
		if request.method == "POST":
			form = QuestionForm(request.POST)
			if form.is_valid():
				time = datetime.datetime.now()
				title = form.cleaned_data['title']
				description = form.cleaned_data['description']
				images = request.FILES.getlist('images')
				image_paths = []
				for image in images:
					ext = image.name.split('.')[-1]
					filename = f"question_images/{uuid.uuid4()}.{ext}"
					path = default_storage.save(filename, ContentFile(image.read()))
					image_paths.append(path)
				images_str = ','.join(image_paths)

				question = Question(title=title, description=description,
									creation_date=time, images=images_str, author=request.user)
				question.save()

				# for tag_title in tags:
				#     if len(Tag.objects.filter(title=tag_title)) == 0:
				#         tag = Tag(title=tag_title)
				#         tag.save()
				#         link = PostToTag(question=question, tag=tag)
				#         link.save()



		else:
			form = QuestionForm()

		context['form'] = form
	else:
		return redirect('/account/login')

	return render(request, template_name='make_question.html', context=context)


def themes_page(request):
	return render(request, template_name="themes.html")
