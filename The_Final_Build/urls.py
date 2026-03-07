from django.contrib import admin
import main.views as view
from django.urls import path
from main import views as main_views
from users import views as users_views
from questions import views as question_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index_page, name='index'),

    path('account/signup/', users_views.signup_page, name='signup'),
    path('account/login/', users_views.login_page, name='login'),
    path('account/password-restore/', users_views.password_restore_page, name='password_restore'),
    path('profile/', users_views.profile_page, name='profile'),

    path('question/', question_views.question_page, name='question'),
    path('question/theme/<int:theme_num>/', question_views.question_themes_page, name='questions'),
    path('question/make/', question_views.question_make_page, name='make_question'),

    path('complaint/', question_views.complaint_page, name='complaint'),

    path('themes/', question_views.themes_page, name='themes'),
]
