from django.urls import path, include
from rest_framework.routers import DefaultRouter
from players.api.v1.views import DefenceViewSet, PlayerViewSet
from teams.api.v1.teams import TeamViewSet

router = DefaultRouter()
router.register(r"players", PlayerViewSet, basename="players")
router.register(r"defence", DefenceViewSet, basename="defence")
router.register(r"teams", TeamViewSet, basename="teams")


urlpatterns = [path("", include(router.urls))]
