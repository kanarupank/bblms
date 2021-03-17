from django.contrib import admin
from .models import User, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats

# Register your models here.

admin.site.register(User)
admin.site.register(UserStats)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Coach)
admin.site.register(PlayerStats)
admin.site.register(TeamStats)
