from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='ms-home'),
    path('about/', views.about, name='ms-about'),
    path('login/', views.login, name='ms-login'),
    path('recent-msgs/', views.recent_threads, name='ms-recent'),
    path('thread/', views.thread, name='thread'),

]
