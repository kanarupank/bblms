from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Avg, Sum, Count
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

from .models import User, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins, generics, permissions, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

from .serializers import TeamSerializer, UserSerializer, GameSerializer, PlayerSerializer, PlayerUserSerializer
from .services import TeamService, PlayerService


# accessible for all, default landing page
class GamesView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # user = User.objects.get(id=request.user.id) # all logged in users will access this
        games = Game.objects.all()
        game_serializer = GameSerializer(games, many=True)
        content = {
            'games': game_serializer.data,
        }
        return Response(content)


# accessible for coach and admins, coaches could only check within their teams
class TopPlayersView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, id=None):
        user = User.objects.get(id=request.user.id)
        content = PlayerService.get_top_players_for_coach(user, id)
        return Response(content)


class GenericTeamAPIView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin,
                         mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    serializer_class = TeamSerializer
    queryset = Team.objects.all().order_by('id')
    lookup_field = 'id'
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        user = User.objects.get(id=request.user.id)

        if id:
            if user.role == User.ADMIN:
                return self.retrieve(request)
            elif user.role == User.COACH:
                return Response(TeamService.get_team_stats_for_coach(user, id))
            else:
                return HttpResponseForbidden()

        else:
            if user.role == User.ADMIN:
                return self.list(request)
            elif user.role == User.COACH:
                return Response(TeamService.get_team_stats_for_coach(user))
            else:
                return HttpResponseForbidden()

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.create(request)

    def put(self, request, id=None):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.update(request, id)

    def delete(self, request, id):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.destroy(request, id)


class GenericPlayerAPIView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()

    lookup_field = 'id'

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        user = User.objects.get(id=request.user.id)

        if id:
            if user.role == User.ADMIN:
                return self.retrieve(request)
            elif user.role == User.COACH:
                return Response(PlayerService.get_player_stats_for_coach(user, id))
            else:
                return HttpResponseForbidden()

        else:
            if user.role == User.ADMIN:
                return self.list(request)
            elif user.role == User.COACH:
                return Response(PlayerService.get_player_stats_for_coach(user, id))
            else:
                return HttpResponseForbidden()

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.create(request)

    def put(self, request, id=None):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.update(request, id)

    def delete(self, request, id):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.destroy(request, id)


class TeamStatsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'team_id'

    def get(self, request, team_id=None):
        user = User.objects.get(id=request.user.id)

        if user.role != User.PLAYER:
            # coach could view only his/her team's stat
            if user.role == User.COACH:
                coach = Coach.objects.filter(id=user.id)
                team = Team.objects.filter(id=coach.team_id)
                team_serializer = TeamSerializer(team)
                content = {
                    'team': team_serializer.data,
                    'average_score': TeamStats.objects.filter(team_id=team_id).aggregate(Avg('score')),

                }
            elif user.role == User.ADMIN:
                teams = Team.objects.all()
                team_serializer = TeamSerializer(teams)
                content = {
                    'teams': team_serializer.data,
                    'average_score': TeamStats.objects.filter(team_id=team_id).aggregate(Avg('score')),

                }

            return Response(content)
        else:
            return HttpResponseForbidden()


#  only the admin would access
class UserSessionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        if user.role == User.ADMIN:
            # Query all non-expired sessions
            # use timezone.now() instead of datetime.now() in latest versions of Django
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            uid_list = []

            # Build a list of user ids from that query
            for session in sessions:
                data = session.get_decoded()
                uid_list.append(data.get('_auth_user_id', None))

                # Query all logged in users based on id list
            users = User.objects.filter(id__in=uid_list)
            user_serializer = UserSerializer(users)
            content = {
                'user_sessions': user_serializer.data,
            }

        return Response(content)
