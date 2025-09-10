""" Module for Penalty urls """

from django.urls import path

from . import views

urlpatterns = [
    path('penalties', views.penalties, name='penalties'),
    path('create', views.penalty_create, name='create'),
]
