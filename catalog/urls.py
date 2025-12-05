from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                    # Главная страница
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    path('profile/', views.profile, name='profile'),      # Личный кабинет
    path('requests/', views.my_requests, name='my_requests'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<uuid:pk>/delete/', views.delete_request, name='delete_request'),
    path('requests/<uuid:pk>/', views.request_detail, name='request-detail'),
]
