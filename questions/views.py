from django.shortcuts import render, redirect, get_object_or_404
from questions.forms import *
import datetime
from questions.models import *

# Create your views here.

def question_themes_page(request):
    return render(request, template_name="questions.html")

def question_page(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question)
    comments = Comment.objects.filter(question=question)
    context = {
        'question': question,
        'answers': answers,
        'comments': comments
    }
    return render(request, 'question.html', context)

def question_make_page(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            time = datetime.datetime.now()
            title = form.data['title']
            description = form.data['description']
            tags = form.data['tags'].split()
            images = form.data['images']

            question = Question(title=title, description=description,
                                creation_date=time, views=0, images=images, author=request.user)
            question.save()

            for tag_title in tags:
                if len(Tag.objects.filter(title=tag_title)) == 0:
                    tag = Tag(title=tag_title)
                    tag.save()

                link = PostToTag(question=question, tag=tag)
                link.save()

        else:
            form = QuestionForm()

        context['form'] = form
    else:
        return redirect('/account/login')

    return render(request, template_name='make_question.html', context=context)


def complaint_page(request):
    context = {}

    question_id = request.GET.get('question_id')
    user_id = request.GET.get('user_id')

    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        complaint_text = form.data['description']

        if user_id and int(user_id) != int(request.user.id) or question_id:
            complaint = Complaint(author=request.user, description=complaint_text,
                                  question=Question.objects.filter(id=question_id)[0] if "question_id" in request.GET else None,
                                  user=User.objects.filter(id=user_id)[0] if "user_id" in request.GET else None)
            complaint.save()
    else:
        form = ComplaintForm()

    context['form'] = form

    return render(request, "complaint.html", context)

def themes_page(request):
    return render(request, template_name="themes.html")