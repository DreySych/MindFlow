from django.shortcuts import render, redirect
import datetime
from users.models import User
from django.contrib.auth.hashers import check_password, make_password


# Create your views here.
def index_page(request):
    username = request.user.username if request.user.is_authenticated else "Профиль"
    all_users = User.objects.all()
    context = {
        "username": username,
        "users": all_users,
    }
    return render(request, template_name="index.html", context=context)


