from django.contrib import admin
from .models import UserBBLMS, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats

# Register your models here.

admin.site.register(UserBBLMS)
admin.site.register(UserStats)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Coach)
admin.site.register(PlayerStats)
admin.site.register(TeamStats)
