from django.urls import path
from explore_scotland_app import views

app_name = 'explore_scotland_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]