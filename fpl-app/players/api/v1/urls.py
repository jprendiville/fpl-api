# api/v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from players.api.v1.views import PlayerViewSet

router = DefaultRouter()
router.register(r"players", PlayerViewSet, basename="players")

urlpatterns = [
    path("", include(router.urls)),
]
