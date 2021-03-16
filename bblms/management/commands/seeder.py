from django.core.management.base import BaseCommand
import random
from django_seed import Seed
from bblms.models import User, User_Stat, Game, Team, Player, Coach, Player_Stat, Team_Stat
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.hashers import make_password

# python manage.py seeder --mode=refresh

""" Clear all data and creates addresses """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'


class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('done.')


def run_seed(self, mode):
    """ Seed database based on mode
    :param mode: refresh / clear
    :return:
    """
    seeder = Seed.seeder()
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return

    create_teams(seeder)
    create_user(seeder)
    create_coach(seeder)
    create_player(seeder)
    create_qualifier_games(seeder)
    create_quarter_final_games(seeder)
    create_semi_final_games(seeder)
    create_final_game(seeder)

    user_stat(seeder)
    team_stat()
    # player_stat()


def clear_data():
    """Deletes all the table data"""
    Team.objects.all().delete()
    Game.objects.all().delete()
    User.objects.all().delete()


def create_teams(seeder):
    for i in range(16):
        team = Team(team_name=seeder.faker.name())
        team.save()


def create_user(seeder):
    password = make_password('admin')

    # create a admin site user
    user = User(
        username='admin',
        password=password,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        role=1)
    user.save()

    # create 16 coach
    password = make_password('coach')
    for i in range(1, 17):
        user = User(
            username='coach' + str(i),
            password=password,
            is_staff=False,
            is_superuser=False,
            email=seeder.faker.safe_email(),
            first_name=seeder.faker.first_name(),
            last_name=seeder.faker.last_name(),
            role=2)
        user.save()

    # create 160 players
    password = make_password('player')
    for i in range(1, 161):
        user = User(
            username='player' + str(i),
            password=password,
            is_staff=False,
            is_superuser=False,
            email=seeder.faker.safe_email(),
            first_name=seeder.faker.first_name(),
            last_name=seeder.faker.last_name(),
            role=3)
        user.save()


def create_coach(seeder):
    users = User.objects.filter(role=2)
    teams = Team.objects.all()
    for i in range(0, len(users)):
        coach = Coach(
            team_id=teams[i].id,
            user_id=users[i].id)
        coach.save()


def create_player(seeder):
    users = User.objects.filter(role=3)
    teams = Team.objects.all()
    count = 0
    for i in range(0, len(teams)):
        limit = count + 10
        for j in range(count, limit):
            player = Player(
                team_id=teams[i].id,
                user_id=users[j].id,
                height=seeder.faker.random_int())
            player.save()
        count += 10


def create_qualifier_games(seeder):
    teams = Team.objects.all()
    create_game(seeder, teams, Game.L)


def create_quarter_final_games(seeder):
    games = Game.objects.filter(round=Game.L)
    teams = []
    for game in games:
        print(game.winner)
        teams.append(game.winner)
    create_game(seeder, teams, Game.Q)


def create_semi_final_games(seeder):
    games = Game.objects.filter(round=Game.Q)
    teams = []
    for game in games:
        print(game.winner)
        teams.append(game.winner)
    create_game(seeder, games, Game.S)


def create_final_game(seeder):
    games = Game.objects.filter(round=Game.S)
    teams = []
    for game in games:
        print(game.winner)
        teams.append(game.winner)
    create_game(seeder, games, Game.F)


def create_game(seeder, teams, round):
    # skipping the real world practice
    # in Semi for example: 1 vs 4 and 2 vs 3
    # match-up the teams randomly based on their order
    teams_one = teams[1::2]  # odd indexes
    teams_two = teams[0::2]  # even indexes

    for i in range(len(teams_one)):
        team_one_score = seeder.faker.random_int(min=0, max=100)  # random scores between 0 and 100
        team_two_score = seeder.faker.random_int(min=0, max=100)

        # assume if it's a tie then the team_one is the winner
        winner = teams_one[i] if team_one_score >= team_two_score else teams_two[
            i]

        team_one_id = teams_one[i].id  # if round == Game.L else teams_one[i].winner_id
        team_two_id = teams_two[i].id  # if round == Game.L else teams_two[i].winner_id
        winner_id = winner.id  # if round == Game.L else winner.winner_id

        game = Game(
            team_one_id=team_one_id,
            team_two_id=team_two_id,
            team_one_score=team_one_score,
            team_two_score=team_two_score,
            winner_id=winner_id,
            round=round,
            date=seeder.faker.date_time_this_decade(before_now=True, after_now=False, tzinfo=None))

        game.save()


def user_stat(seeder):
    users = User.objects.all()

    for user in users:
        for i in range(seeder.faker.random_int(min=1, max=10, step=1)):
            stat = User_Stat(user_id=user.id,
                             login_time=seeder.faker.date_time_this_month(
                                 before_now=True, after_now=False, tzinfo=timezone.utc),
                             logout_time=seeder.faker.date_time_this_month(
                                 before_now=False, after_now=True, tzinfo=timezone.utc)
                             )
            stat.save()


def team_stat():
    teams = Team.objects.all()

    for team in teams:
        scores = Game.objects.filter(
            Q(team_one_id=team.id) | Q(team_two_id=team.id))
        for team_score in scores:
            team_id = team_score.team_one_id if team_score.team_one_id == team.id else team_score.team_two_id
            game_score = team_score.team_one_score if team_score.team_one_id == team.id else team_score.team_two_score
            team_one_stat = Team_Stat(
                score=game_score, game_id=team_score.id, team_id=team_id)
            team_one_stat.save()

            # team_two_stat = Team_Stat(score=team_score.guest_score, game_id=team_score.id, team_id=team_score.guest_id)
            # team_two_stat.save()
            # self.stdout.write(self.style.SUCCESS('Stat saved for Game # %s ' % team_score.id))

# def player_stat():
#     stats = Team_Stat.objects.all()

#     for team_stat in stats:
#         # this should not be used in production, however this is dummy data to whatever gets jobs done for now
#         players = Player.objects.filter(team_id=team_stat.team_id).order_by('?')[:5]
#         player_scores = generate_random_player_score(5, team_stat.score)

#         for i in range(len(players)):
#             player_stat = Player_Stat(score=player_scores[i], game_id=team_stat.game_id, player_id=players[i].id)
#             player_stat.save()


# def generate_random_player_score(n, total):
#     import random
#     dividers = sorted(random.sample(range(1, total), n - 1))
#     return [a - b for a, b in zip(dividers + [total], [0] + dividers)]
