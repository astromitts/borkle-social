from django.contrib import admin
from bogames.models import Player, Game, ErrorLog


admin.site.register(ErrorLog)
admin.site.register(Player)
admin.site.register(Game)
