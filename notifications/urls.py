from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.notifications_list, name='notifications_list'),
    path('count/', views.notifications_count, name='notifications_count'),
    path('read/<int:notification_id>/', views.read_notification, name='read_notification'),
    path('', views.notifications_list, name='notifications'),
]