from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user/", views.user, name="user"),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('download_video/', views.download_video, name='download_video'),
    path('logout/', views.view_logout, name='logout'),
    path("test/", views.test, name="test")
]