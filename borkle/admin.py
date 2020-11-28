from django.contrib import admin
from borkle.models import Turn, ScoreSet, BorkleGame, GamePlayer


admin.site.register(Turn)
admin.site.register(ScoreSet)
admin.site.register(BorkleGame)
admin.site.register(GamePlayer)
