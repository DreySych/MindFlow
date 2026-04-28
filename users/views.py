from django.shortcuts import render, redirect
from users.forms import SignUpForm, LoginForm
from users.models import User
from django.contrib.auth.hashers import check_password, make_password
import datetime
from django.contrib.auth import authenticate, login

# Create your views here.
def login_page(request):
    return render(request, 'login.html')

def notifications_page(request):
    return render(request, template_name="notifications.html")

def password_restore_page(request):
    return render(request, template_name="password_restore.html")

def PM_page(request):
    return render(request, template_name="PM.html")

def signup_page(request):
    return render(request, 'signup.html')

def profile_page(request):
    return render(request, template_name="profile.html")

def profile_somelse_page(request):
    return render(request, template_name="profile_somelse.html")
