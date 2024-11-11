# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
]
