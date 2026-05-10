from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/', views.chat_page, name='chat_page'),
    path('<int:user_id>/messages/', views.chat_messages, name='chat_messages'),
]