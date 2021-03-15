from django.contrib import admin
from .models import User, User_Stat, Game, Team, Player, Coach, Player_Stat, Team_Stat

# Register your models here.

admin.site.register(User)
admin.site.register(User_Stat)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Coach)
admin.site.register(Player_Stat)
admin.site.register(Team_Stat)
