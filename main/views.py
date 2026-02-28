from django.shortcuts import render

# Create your views here.
def index_page(request):
    return render(request, template_name="index.html")

def signup_page(request):
    return render(request, template_name="signup.html")

def login_page(request):
    return render(request, template_name="login.html")

def password_restore_page(request):
    return render(request, template_name="password_restore.html")

def profile_page(request):
    return render(request, template_name="profile.html")

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
