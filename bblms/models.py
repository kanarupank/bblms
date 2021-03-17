from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.

# create customize User extended from Django's AbstractUser user model
class User(AbstractUser):
    # names instead of number?
    ADMIN = 1
    COACH = 2
    PLAYER = 3

    ROLE_CHOICES = [
        (COACH, 'Coach'),
        (PLAYER, 'Player'),
        (ADMIN, 'Admin'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, default=PLAYER, verbose_name='type of role')  # defaulting to least privileges user
    # can create Role model separately and add ManyToMany if user has more than one role


class Team(models.Model):
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return self.team_name


class Game(models.Model):
    L = 'L'
    Q = 'Q'
    S = 'S'
    F = 'F'
    ROUNDS_CHOICES = [
        (L, 'League'),
        (Q, 'Quarter Final'),
        (S, 'Semi Final'),
        (F, 'Final')
    ]

    team_one = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_one')
    team_two = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_two')
    team_one_score = models.IntegerField()
    team_two_score = models.IntegerField()
    winner = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='winner')
    date = models.DateField(verbose_name='game date')
    round = models.CharField(default=Q, max_length=1, choices=ROUNDS_CHOICES)


class Coach(models.Model):
    user = models.OneToOneField(User(), on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Player(models.Model):
    user = models.OneToOneField(User(), on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    height = models.DecimalField(max_digits=4, decimal_places=2)


class UserStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(
        verbose_name='login date time', default=timezone.now)
    logout_time = models.DateTimeField(verbose_name='logout date time')


class PlayerStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()


class TeamStats(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='team')
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='game')
    score = models.IntegerField()
