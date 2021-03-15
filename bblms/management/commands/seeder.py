from django.core.management.base import BaseCommand
import random
from django_seed import Seed
from bblms.models import User, User_Stat, Game, Team, Player, Coach, Player_Stat, Team_Stat
from django.utils import timezone
from django.db.models import Q

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
    create_qualifier_game(seeder)
    create_semi_final_game(seeder)
    create_final_game(seeder)
    create_winner(seeder)

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
    names = [seeder.faker.unique.user_name() for i in range(500)]

    password = 'admin'
    # create a admin site user
    user = User(
        username='admin',
        password=password,
        is_staff=True,
        is_superuser=True,
        is_active=True)
    user.save()

    # create 10 admin
    for i in range(0, 10):
        user = User(
            username=names[i],
            password=password,
            is_staff=True,
            email=seeder.faker.safe_email(),
            first_name=seeder.faker.first_name(),
            last_name=seeder.faker.last_name(),
            role=1)
        user.save()

    # create 16 coach
    password = 'coach'
    for i in range(20, 36):
        user = User(
            username=names[i],
            password=password,
            is_staff=True,
            email=seeder.faker.safe_email(),
            first_name=seeder.faker.first_name(),
            last_name=seeder.faker.last_name(),
            role=2)
        user.save()

    # create 200 players
    password = 'player'
    for i in range(50, 300):
        user = User(
            username=names[i],
            password=password,
            is_staff=True,
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


def create_qualifier_game(seeder):
    teams = Team.objects.all()
    create_game(seeder, teams, 'Q')


def create_semi_final_game(seeder):
    games = Game.objects.filter(round='Q')
    create_game(seeder, games, 'S')


def create_final_game(seeder):
    games = Game.objects.filter(round='S')
    create_game(seeder, games, 'F')


def create_winner(seeder):
    games = Game.objects.filter(round='F')
    create_game(seeder, games, 'W')


def create_game(seeder, teams, round):
    # match-up the teams based on their order
    hosts = teams[1::2]  # odd indexes
    guests = teams[0::2]  # even indexes

    for i in range(len(hosts)):
        host_team_score = seeder.faker.random_int(min=0, max=100)
        guest_team_score = seeder.faker.random_int(min=0, max=100)
        winner = hosts[i] if host_team_score > guest_team_score else guests[i]

        # lets simplify things so easy to read
        host_team_id = hosts[i].id if round == 'Q' else hosts[i].winner_id
        guest_team_id = guests[i].id if round == 'Q' else guests[i].winner_id
        winner_id = winner.id if round == 'Q' else winner.winner_id

        # populate SF teams

        game = Game(
            host_team_id=host_team_id,
            guest_team_id=guest_team_id,
            host_team_score=host_team_score,
            guest_team_score=guest_team_score,
            winner_id=winner_id,
            round=round,
            date=seeder.faker.date_time_this_decade(before_now=True, after_now=False, tzinfo=None))

        game.save()


def user_stat(seeder):
    users = User.objects.all()

    for user in users:
        for i in range(seeder.faker.random_int(min=1, max=10, step=1)):
            stat = User_Stat(user_id=user.id,
                             login_time=seeder.faker.date_time_this_month(before_now=True, after_now=False,
                                                                          tzinfo=timezone.utc),
                             logout_time=seeder.faker.date_time_this_month(before_now=False, after_now=True,
                                                                           tzinfo=timezone.utc)
                             )
            stat.save()


def team_stat():
    teams = Team.objects.all()

    for team in teams:
        scores = Game.objects.filter(Q(host_team_id=team.id) | Q(guest_team_id=team.id))
        for team_score in scores:
            team_id = team_score.host_team_id if team_score.host_team_id == team.id else team_score.guest_team_id
            game_score = team_score.host_team_score if team_score.host_team_id == team.id else team_score.guest_team_score
            # add host stat
            host_stat = Team_Stat(score=game_score, game_id=team_score.id, team_id=team_id)
            host_stat.save()

            # add guest stat
            # guest_stat = Team_Stat(score=team_score.guest_score, game_id=team_score.id, team_id=team_score.guest_id)
            # guest_stat.save()
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

def generate_random_player_score(n, total):
    import random
    dividers = sorted(random.sample(range(1, total), n - 1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]
