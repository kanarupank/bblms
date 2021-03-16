from django.urls import include, path
from rest_framework import routers
from . import views

from .views import GenericTeamAPIView, GenericPlayerAPIView, TeamStatsView, ScoreView

router = routers.DefaultRouter()

# Wire up API using automatic URL routing.
# Additionally, include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('team/', GenericTeamAPIView.as_view()),
    path('team/<int:id>', GenericTeamAPIView.as_view()),
    path('player/', GenericPlayerAPIView.as_view()),
    path('player/<int:id>', GenericPlayerAPIView.as_view()),
    path('team/stats/<int:team_id>', TeamStatsView.as_view()),
    path('games/', ScoreView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
