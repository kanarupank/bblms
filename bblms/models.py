from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.

# create customize User extended from Django's AbstractUser user model


class User(AbstractUser):
    ADMIN = '1'
    COACH = '2'
    PLAYER = '3'

    ROLE_CHOICES = [
        (COACH, 'Coach'),
        (PLAYER, 'Player'),
        (ADMIN, 'Admin'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, default=PLAYER, verbose_name='type of role')
    # You can create Role model separately and add ManyToMany if user has more than one role


class Team(models.Model):
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return self.team_name


class Game(models.Model):
    Q = 'Q'
    S = 'S'
    F = 'F'
    W = 'W'

    ROUNDS_CHOICES = [
        (Q, 'Quarter Final'),
        (S, 'Semi Final'),
        (F, 'Final'),
        (W, 'Winner')
    ]

    host_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='host')
    guest_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='guest')
    host_team_score = models.IntegerField()
    guest_team_score = models.IntegerField()
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
    height = models.IntegerField()


class Team_Stat(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='team')
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='game')
    score = models.IntegerField()


class User_Stat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(
        verbose_name='login date time', default=timezone.now)
    logout_time = models.DateTimeField(verbose_name='logout date time')


class Player_Stat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
