from django.shortcuts import render

# Create your views here.

def signup_page(request):
    return render(request, template_name="signup.html")

def login_page(request):
    return render(request, template_name="login.html")

def password_restore_page(request):
    return render(request, template_name="password_restore.html")

def profile_page(request):
    return render(request, template_name="profile.html")
