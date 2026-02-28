from django.shortcuts import render, redirect
import datetime
from main.forms import SignUpForm, LoginForm
from main.models import User
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

def signup_page(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password']),
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                sex=form.cleaned_data['sex'],
                role=form.cleaned_data.get('role', ''),
                birth_date=form.cleaned_data['birth_date'],
                registration_date=datetime.date.today(),
                level='',
                reputation=0,
                image=''
            )
            user.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, template_name='signup.html', context={'form': form})

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            if user and check_password(password, user.password):
                request.session['user_id'] = user.id
                return redirect('index')
            else:
                print("ОШИБКА. НЕВЕРНЫЙ ПАРОЛЬ")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
