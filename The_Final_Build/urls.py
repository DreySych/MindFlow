from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from ai import views as ai_views
from complaints import views as complaint_views
from main import views as main_views
from notifications import views as notifications_views
from questions import views as question_views
from users import views as users_views

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


    path('profile/', users_views.my_profile_redirect, name='profile_posts'),


    path('profile/<str:username>/',
         users_views.profile_page_general, name='profile_general'),
    path('profile/settings', users_views.profile_page_settings,
         name='profile_settings'),
    path('profile/<str:username>/comments/',
         users_views.profile_page_comments, name='profile_comments'),
    path('profile/<str:username>/liked/',
         users_views.profile_page_liked, name='profile_liked'),

    path('question/<int:question_id>/delete/',
         question_views.delete_question, name='delete_question'),
    path('question/<int:question_id>/',
         question_views.question_page, name='question'),
    path('question/theme/<int:theme_num>/',
         question_views.question_themes_page, name='questions'),
    path('question/make/', question_views.question_make_page, name='make_question'),
    path('question/edit/', question_views.question_edit_page, name='edit_question'),


    path('comment/make/<int:question_id>',
         question_views.make_comment_page, name='make_comment'),
    path('comment/like/', question_views.like_comment, name='like_comment'),
    path('comment/dislike/', question_views.dislike_comment, name='dislike_comment'),

    path('answer/make/<int:comment_id>',
         question_views.make_answer_page, name='make_answer'),
    path('comment/<int:comment_id>/answer/',
         question_views.make_answer_page, name='make_answer'),
    path('answer/like/', question_views.like_answer, name='like_answer'),
    path('answer/dislike/', question_views.dislike_answer, name='dislike_answer'),

    path('add_friend/<int:user_id>/', users_views.add_friend, name='add_friend'),
    path('delete_friend/<int:user_id>/',
         users_views.delete_friend, name='delete_friend'),

    path('complaint/', complaint_views.complaint_page, name='complaint'),
    path('complaint/panel/users/', complaint_views.complaint_user_panel_page,
         name='complains_panel_page_u'),
    path('complaint/panel/questions/',
         complaint_views.complaint_question_panel_page, name='complains_panel_page_p'),
    path('complaint/panel/comments/',
         complaint_views.complaint_comment_panel_page, name='complains_panel_page_c'),
    path('accept/', complaint_views.accept, name='accept_complaint'),
    path('decline/', complaint_views.decline, name='decline_complaint'),

    path('themes/', question_views.themes_page, name='themes'),
    path('messages/', include('private_messages.urls')),

    path('account/password-restore/',
         users_views.password_restore_page, name='password_restore'),
    path('account/password-restore/code/',
         users_views.password_restore_code_page, name='password_restore_code'),
    path('account/password-restore/new/',
         users_views.password_restore_new_page, name='password_restore_new'),

    path('ai/', ai_views.ai_search_page, name='ai_search'),
    path('ai/api/', ai_views.ai_search_api, name='ai_search_api'),

    path('profile/someone/', users_views.my_profile_redirect, name='profile_somelse'),
    path('settings/', users_views.profile_page_settings, name='settings'),

    path('notifications/', notifications_views.notifications_list,
         name='notifications'),
    path('notifications/list/', notifications_views.notifications_list,
         name='notifications_list'),
    path('notifications/count/', notifications_views.notifications_count,
         name='notifications_count'),
    path('notifications/read/<int:notification_id>/',
         notifications_views.read_notification, name='read_notification'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
