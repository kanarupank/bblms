from rest_framework import serializers
from .models import User, User_Stat, Game, Team, Player, Coach, Player_Stat, Team_Stat


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('user_id', 'team_id', 'height')


class PlayerUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Player
        fields = ('user', 'team_id', 'height')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'team_name')


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ('user_id', 'team_id')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('team_one', 'team_two', 'team_one_score',
                  'team_two_score', 'winner', 'date', 'round')
