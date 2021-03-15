from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from .models import User, User_Stat, Game, Team, Player, Coach, Player_Stat, Team_Stat
from django.db.models import Avg, Sum, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from rest_framework import viewsets
from .serializers import TeamSerializer, UserSerializer, GameSerializer


# Create your views here.

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('team_name')
    serializer_class = TeamSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
