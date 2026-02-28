from django.shortcuts import render

# Create your views here.

def question_themes_page(request):
    return render(request, template_name="questions.html")

def question_page(request):
    return render(request, template_name="question.html")

def question_make_page(request):
    return render(request, template_name="make_question.html")

def complaint_page(request):
    return render(request, template_name="complaint.html")

def themes_page(request):
    return render(request, template_name="themes.html")