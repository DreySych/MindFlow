from django.contrib import admin
import main.views as view
from django.urls import path
from main import views as main_views
from users import views as users_views
from complaints import views as complaint_views
from questions import views as question_views
from django.conf import settings
from django.conf.urls.static import static
from private_messages import views as private_messages_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index_page, name='index'),
    path('sidebar/', main_views.sidebar_page, name='sidebar'),
    path('like/', main_views.like, name='like'),
    path('dislike/', main_views.dislike, name='dislike'),
    path('delete/', main_views.delete_post, name='delete_post'),

    path('account/signup/', users_views.signup_page, name='signup'),
    path('account/login/', users_views.login_page, name='login'),
    path('account/logout/', users_views.logout_page, name='logout'),
    path('account/password-restore/', users_views.password_restore_page, name='password_restore'),
    path('profile/<str:username>/', users_views.profile_page_general, name='profile_general'),
    path('profile/<str:username>/comments.', users_views.profile_page_comments, name='profile_comments'),
    path('profile/<str:username>/liked.', users_views.profile_page_liked, name='profile_liked'),
    path('profile/settings', users_views.profile_page_settings, name='profile_settings'),

    path('question/<int:question_id>/', question_views.question_page, name='question'),
    path('question/theme/<int:theme_num>/', question_views.question_themes_page, name='questions'),
    path('question/make/', question_views.question_make_page, name='make_question'),
    path('question/edit/', question_views.question_edit_page, name='edit_question'),

    path('comment/make/<int:question_id>', question_views.make_comment_page, name='make_comment'),
    path('answer/make/<int:comment_id>', question_views.make_answer_page, name='make_answer'),
    path('add_friend/<int:user_id>/', users_views.add_friend, name='add_friend'),
    path('delete_friend/<int:user_id>/', users_views.delete_friend, name='delete_friend'),


    path('complaint/panel/users', complaint_views.complaint_user_panel_page, name='complaint_user_panel'),
    path('complaint/panel/questions', complaint_views.complaint_question_panel_page, name='complaint_question_panel'),
    path('complaint/panel/comments', complaint_views.complaint_comment_panel_page, name='complaint_comment_panel'),
    path('complaint/', complaint_views.complaint_page, name='complaint'),
    path('accept/', complaint_views.accept, name='accept_complaint'),
    path('decline/', complaint_views.decline, name='decline_complaint'),

    path('themes/', question_views.themes_page, name='themes'),

    path('chat/<int:user_id>/', private_messages_views.chat_page, name='chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)