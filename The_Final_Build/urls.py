from django.contrib import admin
import main.views as view
from django.urls import path
from main import views as main_views
from users import views as users_views
from questions import views as question_views
from complains import views as complains_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index_page, name='index'),
    path('posts/', users_views.profile_posts_page, name='profile_posts'),
    path('comments/', users_views.profile_comments_view, name='profile_comments'),
    path('likes/', users_views.profile_likes_view, name='profile_likes'),
    path('account/signup/', users_views.signup_page, name='signup'),
    path('settings', users_views.settings_page, name='settings'),
    path('account/login/', users_views.login_page, name='login'),
    path('account/password-restore/', users_views.password_restore_page, name='password_restore'),
    path('profile/', users_views.profile_page, name='profile'),
    path('profile/somelse/', users_views.profile_somelse_page, name='profile_somelse'),
    path('notifications/', users_views.notifications_page, name='notifications'),
    path('PM/', users_views.PM_page, name='PM'),

    path('question/', question_views.question_page, name='question'),
    path('question/make/', question_views.question_make_page, name='make_question'),

    path('complaint/question/', complains_views.complain_question_page, name='complain_question'),
    path('complaint/user/', complains_views.complain_user_page, name='complain_user'),
    path('complaint/panel/', complains_views.complains_panel_page, name='complains_panel'),
]
