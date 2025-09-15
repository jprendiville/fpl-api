""" Module for Application urls """

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API schema & docs (nice to have)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/v1/", include(("api.v1.urls", "api-v1"), namespace="v1")),
    # path('players/', include('players.urls'), name='players'),
    # path('teams/', include('teams.urls'), name='teams'),
    # path('penalty/', include('penalties.urls'), name='penalty'),
    # path('managers/', include('manager.urls'), name='managers'),
    # path('settings/', include('settings.urls'), name='settings'),
    # path('', views.home, name='home'),
    # path('home/', views.home, name='home'),
    # path('access-denied/', views.denied_page, name='access-denied'),
    # path('500/', views.server_error, name='server-error'),
]
