from django.contrib import admin
from borkle.models import Game, GamePlayer, Turn, ScoreSet

admin.site.register(Game)
admin.site.register(GamePlayer)
admin.site.register(Turn)
admin.site.register(ScoreSet)
