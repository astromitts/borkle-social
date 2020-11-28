from django.contrib import admin
from boatfight.models import BoatFightGame, GamePlayer, BoatPlacement, Turn


admin.site.register(BoatFightGame)
admin.site.register(GamePlayer)
admin.site.register(BoatPlacement)
admin.site.register(Turn)
