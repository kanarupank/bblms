from django.db.models import Avg

from .models import User, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats
from .serializers import TeamSerializer, UserSerializer, GameSerializer, PlayerSerializer, PlayerUserSerializer, \
    TeamPlayerSerializer


class TeamsService():
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
