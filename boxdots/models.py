from django.db import models
from bogames.models import DataGame, DataGamePlayer
import json


class BoxDotDataGame(DataGame):

    @property
    def _default_game_data(self):
        total_tiles = 7 * 6
        return {
            'placedTilesCount': 0,
            'totalTiles': total_tiles,
            'placedTiles': [],
            'winner': '',
            'loser': '',
            'winningCoordinates': []
        }

    def update_board(self, xpos, ypos, gameplayer_id):
        new_placed_tiles = self.data.get('placedTiles', [])

        new_placed_tiles.append(
            {
                'x': xpos,
                'y': ypos,
                'filledById': gameplayer_id,
            }
        )
        self.data['placedTilesCount'] = len(new_placed_tiles)
        self.data['placedTiles'] = new_placed_tiles
        self.save()

    def advance_player(self, player1, player2):
        if player1.data['isCurrentPlayer'] is True:
            player1.data['isCurrentPlayer'] = False
            player2.data['isCurrentPlayer'] = True
        else:
            player1.data['isCurrentPlayer'] = True
            player2.data['isCurrentPlayer'] = False

        player1.save()
        player2.save()

    def end_game(self, winning_coordinates, winner, loser):
        winner.data['status'] = 'won'
        winner.save()
        loser.data['status'] = 'lost'
        loser.save()

        winning_coordinates_unique = []
        for coord in winning_coordinates:
            if not coord in winning_coordinates_unique:
                winning_coordinates_unique.append(coord)

        self.meta['gameStatus'] = 'over'
        self.data['winner'] = winner.player.username
        self.data['loser'] = loser.player.username
        self.data['winningCoordinates'] = winning_coordinates_unique
        self.save()

    def draw_game(self):
        for gp in self.gameplayer_set.all():
            gp.data['status'] = 'lost'
            gp.save()
        self.meta['gameStatus'] = 'over'
        self.save()


class GamePlayer(DataGamePlayer):
    game = models.ForeignKey(BoxDotDataGame, on_delete=models.CASCADE)

    @property
    def _default_data(self):
        default_data = super(GamePlayer, self)._default_data()
        default_data.update({
            'placedTiles': [],
            'winningTiles': [],
        })
        return default_data
