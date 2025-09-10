""" Module for Application urls """

from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('players/', include('players.urls'), name='players'),
    path('teams/', include('teams.urls'), name='teams'),
    path('penalty/', include('penalties.urls'), name='penalty'),
    path('managers/', include('manager.urls'), name='managers'),
    path('settings/', include('settings.urls'), name='settings'),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('access-denied/', views.denied_page, name='access-denied'),
    path('500/', views.server_error, name='server-error'),
]
