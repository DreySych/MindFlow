from django.shortcuts import render, redirect
import datetime
from users.models import User, Subscription
from django.contrib.auth.hashers import check_password, make_password


# Create your views here.
def index_page(request):
    username = request.user.username if request.user.is_authenticated else "Профиль"
    all_users = User.objects .all()
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
    return render(request, template_name="index.html", context=context)

def sidebar_page(request):
    context = {}

    subscriptions = Subscription.objects.filter(user1=request.user)
    context['subscriptions'] = subscriptions

    return render(request, template_name="sidebar.html", context=context)


