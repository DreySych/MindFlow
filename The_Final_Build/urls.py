from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),

    path('account/signup/', views.signup_page, name='signup'),
    path('account/login/', views.login_page, name='login'),
    path('account/password-restore/', views.password_restore_page, name='password_restore'),
    path('profile/', views.profile_page, name='profile'),

    path('question/', views.question_page, name='question'),
    path('question/theme/<int:theme_num>/', views.question_themes_page, name='questions'),
    path('question/make/', views.question_make_page, name='make_question'),

    path('complaint/', views.complaint_page, name='complaint'),

    path('themes/', views.themes_page, name='themes'),
]
