from django.core.management.base import BaseCommand
from django_seed import Seed
from bblms.models import UserBBLMS, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.hashers import make_password

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

    # create games and player statistics
    create_qualifier_games(seeder)
    create_quarter_final_games(seeder)
    create_semi_final_games(seeder)
    create_final_game(seeder)

    user_stat(seeder)
    team_stat()


def clear_data():
    """Deletes all the table data"""
    Team.objects.all().delete()
    Game.objects.all().delete()
    UserBBLMS.objects.all().delete()


def create_teams(seeder):
    for _ in range(16):
        team = Team(team_name=seeder.faker.name())
        team.save()


def create_user(seeder):
    password = make_password('admin')

    # create a admin site user
    user = UserBBLMS(
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
        user = UserBBLMS(
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
        user = UserBBLMS(
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
    users = UserBBLMS.objects.filter(role=2)
    teams = Team.objects.all()
    for i in range(0, len(users)):
        coach = Coach(
            team_id=teams[i].id,
            user_id=users[i].id)
        coach.save()


def create_player(seeder):
    users = UserBBLMS.objects.filter(role=3)
    teams = Team.objects.all()
    count = 0
    for i in range(0, len(teams)):
        limit = count + 10
        for j in range(count, limit):
            player = Player(
                team_id=teams[i].id,
                user_id=users[j].id,
                height=seeder.faker.random_int(min=1, max=10))  # assigning integer for height for now
            player.save()
        count += 10


def create_qualifier_games(seeder):
    teams = Team.objects.all()
    create_game(seeder, teams, Game.L)


def create_quarter_final_games(seeder):
    games = Game.objects.filter(round=Game.L)
    teams = []
    for game in games:
        teams.append(game.winner)
    create_game(seeder, teams, Game.Q)


def create_semi_final_games(seeder):
    games = Game.objects.filter(round=Game.Q)
    teams = []
    for game in games:
        teams.append(game.winner)
    create_game(seeder, games, Game.S)


def create_final_game(seeder):
    games = Game.objects.filter(round=Game.S)
    teams = []
    for game in games:
        teams.append(game.winner)
    create_game(seeder, games, Game.F)


def create_game(seeder, teams, round):
    # skipping the real world practice
    # in Semi for example: 1 vs 4 and 2 vs 3
    # match-up the teams randomly based on their order
    teams_one = teams[1::2]  # odd indexes
    teams_two = teams[0::2]  # even indexes

    for i in range(len(teams_one)):
        team_one_id = teams_one[i].id
        team_two_id = teams_two[i].id
        team_one_players = Player.objects.filter(team_id=team_one_id)
        team_two_players = Player.objects.filter(team_id=team_two_id)
        team_one_player_stats, team_one_score = create_player_stat(seeder, team_one_players)
        team_two_player_stats, team_two_score = create_player_stat(seeder, team_two_players)

        # assume if it's a tie then the team_one is the winner
        winner = teams_one[i] if team_one_score >= team_two_score else teams_two[i]
        winner_id = winner.id
        game = Game(
            team_one_id=team_one_id,
            team_two_id=team_two_id,
            team_one_score=team_one_score,
            team_two_score=team_two_score,
            winner_id=winner_id,
            round=round,
            date=seeder.faker.date_time_this_decade(before_now=True, after_now=False, tzinfo=None))

        game.save()
        save_player_stat(team_one_player_stats, game)
        save_player_stat(team_two_player_stats, game)


def save_player_stat(player_status, game):
    for player_stat in player_status:
        player_stat.game = game
        player_stat.save()


def create_player_stat(seeder, team_players):
    player_stats = []
    team_score = 0
    for team_player in team_players:
        team_one_player_score = seeder.faker.random_int(min=0, max=30)
        team_score += team_one_player_score
        player_stat = PlayerStats(
            player=team_player,
            score=team_one_player_score)
        player_stats.append(player_stat)

    return player_stats, team_score


def user_stat(seeder):
    users = UserBBLMS.objects.all()

    for user in users:
        for _ in range(seeder.faker.random_int(min=1, max=10, step=1)):
            stat = UserStats(user_id=user.id,
                             login_time=seeder.faker.date_time_this_month(
                                 before_now=True, after_now=False, tzinfo=timezone.utc),
                             logout_time=seeder.faker.date_time_this_month(
                                 before_now=False, after_now=True, tzinfo=timezone.utc)
                             )
            stat.save()


def team_stat():
    teams = Team.objects.all()

    for team in teams:
        games = Game.objects.filter(
            Q(team_one_id=team.id) | Q(team_two_id=team.id))
        for game in games:
            team_id = game.team_one_id if game.team_one_id == team.id else game.team_two_id
            game_score = game.team_one_score if game.team_one_id == team.id else game.team_two_score
            team_stat_ = TeamStats(
                score=game_score, game_id=game.id, team_id=team_id)
            team_stat_.save()
