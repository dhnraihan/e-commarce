from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('reset-password/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]