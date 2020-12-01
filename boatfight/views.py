from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.views import View
from django.template import loader
from django.http import HttpResponse, JsonResponse

from boatfight.forms import InitializeGameForm

from bogames.models import Player
from bogames.views import (
    DashboardBase,
    DashboardApiBase,
    DeclineGameView,
    BoGameBase,
    JoinGameView,
    CancelGameView,
    LeaveGameView,
)

from boatfight.models import (
    SHIPS,
    BoatFightGame,
    GamePlayer,
    BoatPlacement,
    Turn,
)

class BoatFightBaseView(BoGameBase):
    def setup(self, request, *args, **kwargs):
        super(BoatFightBaseView, self).setup(request, *args, **kwargs)
        self.game_path = 'boatfight_game'
        self.cancel_path = 'boatfight_game_cancel'
        self.join_path = 'boatfight_game_accept_invitation_link'
        self.decline_path = 'boatfight_game_decline_invitation_link'
        self.dashboard_refresh_url = 'boatfight_dashboard_api'
        self.start_game_path = 'boatfight_start'
        self.dashboard_path = 'boatfight_dashboard'
        self.template_base = 'boatfight/base.html'
        self.gamePlayerClass = GamePlayer

        if request.user.is_authenticated:
            self.player = Player.get_or_create(user=self.request.user)
            request.session['player_id'] = self.player.pk
            if 'game_uuid' in kwargs:
                try:
                    self.game = BoatFightGame.objects.filter(uuid=kwargs['game_uuid']).first()
                except ValidationError:
                    self.game = None

                if self.game:
                    self.gameplayer = GamePlayer.objects.filter(game=self.game, player=self.player).first()
                    self.boatfighter = GamePlayer.objects.get(player=self.player, game=self.game)
                    self.opponent = self.game.gameplayer_set.exclude(player=self.boatfighter.player).first()
                    self.boatplacement = BoatPlacement.objects.filter(player=self.boatfighter).first()
                    if self.game.status == 'active' and self.game.all_players_ready:
                        if not self.game.current_player:
                            self.game.start_game()
                        self.is_current_player = self.player == self.game.current_player.player
                        self.current_player = self.game.current_player
                    else:
                        self.is_current_player = False
                        self.current_player = None


class Dashboard(DashboardBase):
    def setup(self, request, *args, **kwargs):
        super(BorkleDashboard, self).setup(request, *args, **kwargs)
        self.refresh_url = reverse('borkle_dashboard_api')


class DashboardApi(BoatFightBaseView, DashboardApiBase):
    pass

class InitializeGame(BoatFightBaseView):
    def setup(self, request, *args, **kwargs):
        super(InitializeGame, self).setup(request, *args, **kwargs)
        self.formClass = InitializeGameForm
        self.template = loader.get_template('bogames/generic_form.html')

    def get(self, request, *args, **kwargs):
        form = self.formClass(
            initial={
                'initializing_player_id': self.player.pk
            }
        )
        context = {
            'form': form,
            'form_header': 'Start a boat fight!'
        }
        return HttpResponse(self.template.render(context, request))

    def post(self, request, *args, **kwargs):
        form = self.formClass(request.POST)
        if form.is_valid():
            players = [
                self.player,
                Player.get_by_username(request.POST['opponent'])
            ]
            game = BoatFightGame.initialize_game(players, GamePlayer)
            game.game_type = request.POST['game_type']
            game.created_by = self.player
            game.save()
            return redirect(reverse('boatfight_game', kwargs={'game_uuid': game.uuid}))
        context = {
            'form': form,
            'form_header': 'Start a boat fight!'
        }
        return HttpResponse(self.template.render(context, request))

class JoinGame(BoatFightBaseView, JoinGameView):
    pass


class CancelGame(BoatFightBaseView, CancelGameView):
    pass


class LeaveGame(BoatFightBaseView, LeaveGameView):
    pass


class DeclineGame(BoatFightBaseView, DeclineGameView):
    pass


class Dashboard(BoatFightBaseView, DashboardBase):
    def setup(self, request, *args, **kwargs):
        super(Dashboard, self).setup(request, *args, **kwargs)


class DashboardApi(BoatFightBaseView, DashboardApiBase):
    pass

class GameBoard(BoatFightBaseView):
    def get(self, request, *args, **kwargs):
        if self.boatplacement:
            template = loader.get_template('boatfight/boatfight.html')
            self.game.set_status()
            available_shots = self.boatfighter.available_shots
            context = {
                'x_axis': range(1, 11),
                'y_axis': range(1, 11),
                'boats_to_place': SHIPS,
                'available_shots': available_shots,
                'game': self.game,
                'player': self.player,
                'opponent': self.opponent,
                'placement_orientations': {
                    'longship': self.boatplacement.longship_orientation,
                    'knarr': self.boatplacement.knarr_orientation,
                    'karve': self.boatplacement.karve_orientation,
                    'kraken': self.boatplacement.kraken_orientation,
                    'faering': self.boatplacement.faering_orientation,
                }
            }
        else:
            template = loader.get_template('boatfight/boatfight_placement_board.html')
            context = {
                'x_axis': range(1, 11),
                'y_axis': range(1, 11),
                'boats_to_place': SHIPS,
                'game': self.game,
                'player': self.player,
                'opponent': self.opponent
            }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        boat_placement_data = {field: int(value) for field, value in request.POST.items()}
        boat_placement_data.update({'player_id': self.boatfighter.pk})
        boat_placement = BoatPlacement(**boat_placement_data)
        boat_placement.save()
        self.boatfighter.status = 'ready'
        self.boatfighter.save()
        if self.game.all_players_ready:
            self.game.start_game()

        return JsonResponse({
            'status': 'success',
        })


class BoatFightApi(BoatFightBaseView):
    def _player(self, player):
        return {
            'playerName': player.username,
            'isCurrentPlayer': player.is_current_player and self.game.all_players_ready,
            'availableShots': player.available_shots
        }

    def _opponent(self):
        return self._player(self.opponent)

    def get(self, request, *args, **kwargs):
        data = {
            'isCurrentPlayer': self.is_current_player,
            'player': self._player(self.boatfighter),
            'opponent': self._opponent(),
            'gameStatus': self.game.status,
            'gameType': self.game.game_type,
        }

        self.game.set_status()
        if self.game.status == 'over':
            data['winner'] = self.game.winner.username,

        if kwargs['api_target'] == 'boardsetup':
            data['boats'] = {}
            for boat_type, boat_meta in SHIPS.items():
                data['boats'][boat_type] = {'positions': []}
                for i in range(1, boat_meta.units + 1):
                    xfield = '{}_{}_x'.format(boat_type, i)
                    yfield = '{}_{}_y'.format(boat_type, i)
                    position = {
                        'xPos': getattr(self.boatplacement, xfield),
                        'yPos': getattr(self.boatplacement, yfield)
                    }
                    data['boats'][boat_type]['positions'].append(position)

            if self.game.all_players_ready:
                data['sunkShips'] = self.opponent.boatplacement.get_sunk_ships()
            else:
                data['sunkShips'] = {}

        elif kwargs['api_target'] == 'gamestatus':
            default_shots = {
                'hits': [],
                'misses': [],
                'sunk': []
            }
            if self.opponent.has_boatplacement and self.boatfighter.has_boatplacement:
                opponent_shots = self.boatfighter.boatplacement.get_opponent_shots(self.opponent)
                player_shots = self.boatfighter.boatplacement.get_player_shots(self.opponent)
            else:
                opponent_shots = default_shots
                player_shots = default_shots
            if self.game.all_players_ready or self.opponent.status == 'conceded':
                data['opponentShots'] = opponent_shots
                data['playerShots'] = player_shots
                data['sunkShips'] = self.opponent.boatplacement.get_sunk_ships()
            else:
                data['opponentShots'] = default_shots
                data['playerShots'] = default_shots
                data['sunkShips'] = {}
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        if kwargs['api_target'] == 'fire':
            post_data = {field: int(value) for field, value in request.POST.items()}
            self.boatfighter.current_turn.update(post_data)
            hits = self.opponent.boatplacement.check_hits(post_data)
            hit_data = {field: 'hit' for field in hits}
            self.boatfighter.current_turn.update(hit_data)
            self.boatfighter.end_turn()
            self.opponent.start_turn()
            data = {
                'status': 'success'
            }
        return JsonResponse(data)
