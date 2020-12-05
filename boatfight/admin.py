from django.contrib import admin
from boatfight.models import (
    BoatFightGame,
    GamePlayer,
    Turn,
    Boat,
    GamePlayerBoard,
)


admin.site.register(BoatFightGame)
admin.site.register(GamePlayer)
admin.site.register(Turn)
admin.site.register(Boat)
admin.site.register(GamePlayerBoard)
