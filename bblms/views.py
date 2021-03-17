from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Avg, Sum, Count
from django.core import serializers

from .models import User, UserStats, Game, Team, Player, Coach, PlayerStats

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins, generics, permissions, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

from .serializers import TeamSerializer, UserSerializer, GameSerializer, PlayerSerializer, PlayerUserSerializer


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
                    'average_score': Game.objects.filter(team_id=team_id).aggregate(Avg('score')),

                }
            elif user.role == User.ADMIN:
                teams = Team.objects.all()
                team_serializer = TeamSerializer(teams)
                content = {
                    'teams': team_serializer.data,
                    'average_score': Team_Stat.objects.filter(team_id=team_id).aggregate(Avg('score')),

                }

            return Response(content)
        else:
            return HttpResponseForbidden()


class GenericTeamAPIView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin,
                         mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    serializer_class = TeamSerializer
    queryset = Team.objects.all().order_by('id')
    lookup_field = 'id'
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        if user.role == User.ADMIN:
            return self.list(request)
        elif user.role == User.COACH:
            coach = Coach.objects.get(user_id=user.id)
            team = Team.objects.get(id=coach.team_id)
            team_serializer = TeamSerializer(team)
            players = Player.objects.filter(team_id=coach.team_id)
            player_serializer = PlayerUserSerializer(players, many=True)

            content = {
                'team': team_serializer.data,
                'average_score': Team_Stat.objects.filter(team_id=coach.team_id).aggregate(Avg('score')),
                'players': player_serializer.data
            }
            return Response(content)

        else:
            return HttpResponseForbidden()

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        if (user.role == User.PLAYER):
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
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.create(request)

    def put(self, request, id=None):
        user = User.objects.get(id=request.user.id)
        if user.role == 3:
            return HttpResponseForbidden()

        return self.update(request, id)

    def delete(self, request, id):
        user = User.objects.get(id=request.user.id)
        if user.role == User.PLAYER:
            return HttpResponseForbidden()

        return self.destroy(request, id)
