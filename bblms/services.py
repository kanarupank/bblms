import numpy
from django.db.models import Avg

from .dtos import TopPlayerDto
from .messages import USER_NOT_AUTHORIZED
from .models import UserBBLMS, Team, Player, Coach, PlayerStats, TeamStats
from .serializers import TeamSerializer, PlayerUserSerializer, \
    TeamPlayerSerializer, TopPlayerSerializer, PlayerSerializer


class TeamService():
    @staticmethod
    def get_team_stats(user, team_id=None):
        content = USER_NOT_AUTHORIZED;
        if user.role == UserBBLMS.COACH:
            coach = Coach.objects.get(user_id=user.id)
            # if team id doesn't match then not authorize to view
            if (team_id and coach.team_id == team_id) or team_id == None:
                team = Team.objects.get(id=coach.team_id)
                team_serializer = TeamSerializer(team)
                players = Player.objects.filter(team_id=coach.team_id)
                player_serializer = TeamPlayerSerializer(players, many=True)
                content = {
                    'team': team_serializer.data,
                    'average_score': TeamStats.objects.filter(team_id=coach.team_id).aggregate(Avg('score')),
                    'players': player_serializer.data
                }
        elif user.role == UserBBLMS.ADMIN:
            if team_id:
                team = Team.objects.get(id=team_id)
                team_serializer = TeamSerializer(team)
                players = Player.objects.filter(team_id=team_id)
                player_serializer = TeamPlayerSerializer(players, many=True)
                content = {
                    'team': team_serializer.data,
                    'average_score': TeamStats.objects.filter(team_id=team_id).aggregate(Avg('score')),
                    'players': player_serializer.data
                }
            else:
                team = Team.objects.all()
                team_serializer = TeamSerializer(team, many=True)
                content = {
                    'team': team_serializer.data,
                }
            return content


class PlayerService():
    @staticmethod
    def get_player_stats_for_coach(coach_user, player_id=None):
        coach = Coach.objects.get(user_id=coach_user.id)
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
        """ Returns the list of users within the team whose scores are above the 90th percentile"""
        coaches_team_id = None
        if user.role == UserBBLMS.COACH:
            coach = Coach.objects.get(user_id=user.id)
            coaches_team_id = coach.team_id

        # admin or coach of that team could access
        if user.role == UserBBLMS.ADMIN or (
                coaches_team_id and coaches_team_id == team_id):
            team_players = Player.objects.filter(team_id=team_id)
            # all_players = Player.objects.all() # initially assumed across all teams
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
                    top_player_dto = TopPlayerDto(team_player.user.first_name, team_player.user.last_name, avg)
                    top_players_in_the_team.append(top_player_dto)
            serializer_top_players = TopPlayerSerializer(top_players_in_the_team, many=True)
            content = {
                'players': serializer_top_players.data,
                '90th percentile average': percentile_90_avg,
            }

        else:
            content = USER_NOT_AUTHORIZED

        return content
