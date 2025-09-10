""" This module is for registering the Penalty admin """

from django.contrib import admin

from penalties.models.penalty import Penalty

admin.site.register(Penalty)
