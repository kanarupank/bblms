from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import GenericTeamAPIView, GenericPlayerAPIView, TeamStatsView, GamesView, TopPlayersView, UserSessionView

router = routers.DefaultRouter()
schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
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
    # path('team/stats/<int:team_id>', TeamStatsView.as_view()),
    path('games/', GamesView.as_view()),
    path('login/', include('rest_framework.urls', namespace='rest_framework')),
    path('sessions/', UserSessionView.as_view()),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
