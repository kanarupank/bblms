from django.urls import include, path
from rest_framework import routers

from .views import GenericTeamAPIView, GenericPlayerAPIView, TeamStatsView, GamesView, TopPlayersView, UserSessionView

router = routers.DefaultRouter()

# Wire up API using automatic URL routing.
# Additionally, include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    path('', GamesView.as_view()),  # once logged in land here
    path('team/', GenericTeamAPIView.as_view()),
    path('team/<int:id>', GenericTeamAPIView.as_view()),
    path('team/<int:id>/top-players', TopPlayersView.as_view()),
    path('player/', GenericPlayerAPIView.as_view()),
    path('player/<int:id>', GenericPlayerAPIView.as_view()),
    path('team/stats/<int:team_id>', TeamStatsView.as_view()),
    path('games/', GamesView.as_view()),
    path('login/', include('rest_framework.urls', namespace='rest_framework')),
    path('sessions/', UserSessionView.as_view())
]
