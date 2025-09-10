""" This module is for registering the Player admin """

from django.contrib import admin

from .models import Player

admin.site.register(Player)
