from django.core import serializers
from django.db.models import Avg

from .dtos import TopPlayer
from .models import User, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats
from .serializers import TeamSerializer, UserSerializer, GameSerializer, PlayerSerializer, PlayerUserSerializer, \
    TeamPlayerSerializer, TopPlayerSerializer

import numpy


class TeamService():
    @staticmethod
    def get_team_stats_for_coach(coachUser, team_id=None):
        coach = Coach.objects.get(user_id=coachUser.id)
        if team_id is None or (team_id and team_id == coach.team_id):
            team = Team.objects.get(id=coach.team_id)
            team_serializer = TeamSerializer(team)
            players = Player.objects.filter(team_id=coach.team_id)
            player_serializer = TeamPlayerSerializer(players, many=True)
            content = {
                'team': team_serializer.data,
                'average_score': TeamStats.objects.filter(team_id=coach.team_id).aggregate(Avg('score')),
                'players': player_serializer.data
            }
        else:
            content = 'This Coach user is not authorized to view this team'

        return content


class PlayerService():
    @staticmethod
    def get_player_stats_for_coach(coachUser, player_id=None):
        coach = Coach.objects.get(user_id=coachUser.id)
        player = Player.objects.get(id=player_id)
        team_id = player.team_id
        if player_id and team_id == coach.team_id:
            players = Player.objects.get(id=coach.team_id)
            player_serializer = PlayerUserSerializer(players)
            content = {
                'average_score': PlayerStats.objects.filter(id=player_id).aggregate(Avg('score')),
                'players': player_serializer.data
            }
        else:
            content = 'This Coach user is not authorized to view this team'

        return content

    @staticmethod
    def get_top_players_for_coach(user, team_id=None):
        content = 'test'
        user_id = user.id
        coaches_team_id = None

        if user.role == User.COACH:
            coach = Coach.objects.get(user_id=user.id)
            coaches_team_id = coach.team_id

        # admin or coach of that team could access
        if user.role == User.ADMIN or (
                coaches_team_id and coaches_team_id == team_id):
            team_players = Player.objects.filter(team_id=team_id)
            # all_players = Player.objects.all()
            top_players_in_the_team = []
            player_avg_list = []
            for player in team_players:
                player_avg_list.append(
                    PlayerStats.objects.filter(id=player.id).aggregate(Avg('score')).get('score__avg'))

            percentile_90_avg = numpy.percentile(player_avg_list, 90)

            for team_player in team_players:
                avg = PlayerStats.objects.filter(id=team_player.id).aggregate(Avg('score')).get(
                    'score__avg')
                print(avg)
                if percentile_90_avg <= avg:
                    top_player_dto = TopPlayer(team_player.user.first_name, team_player.user.last_name, avg)
                    top_players_in_the_team.append(top_player_dto)
            serializer_top_players = TopPlayerSerializer(top_players_in_the_team, many=True)
            # content = serializers.serialize('json', top_players_in_the_team)
            # serializer = serializers(top_players_in_the_team, many=True)

            content = {
                'players': serializer_top_players.data,
                '90th percentile average': percentile_90_avg,
            }

        else:
            content = 'This user is not authorized to view this team'

        return content
