from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, JsonResponse

from django.views import View

from bogames.models import Player
from bogames.views import (
    DashboardBase,
    DashboardApiBase,
    BoGameBase,
    JoinGameView,
    CancelGameView,
    LeaveGameView,
)

from borkle.models import BorkleGame

from borkle.forms import InitializeGameForm, InitializePracticeGameForm
from borkle.models import GamePlayer, ScoreSet
from borkle.utils import get_dice_image_path


class BorkleBaseView(BoGameBase):
    def setup(self, request, *args, **kwargs):
        super(BorkleBaseView, self).setup(request, *args, **kwargs)
        self.game_path = 'borkle_game_board'
        self.cancel_path = 'borkle_game_cancel'
        self.join_path = 'borkle_game_accept_invitation_link'
        self.decline_path = 'borkle_game_decline_invitation_link'
        self.dashboard_refresh_url = 'borkle_dashboard_api'
        self.gamePlayerClass = GamePlayer

        if request.user.is_authenticated:
            self.player = Player.get_or_create(user=self.request.user)
            request.session['player_id'] = self.player.pk
            if 'game_uuid' in kwargs:
                try:
                    self.game = BorkleGame.objects.filter(uuid=kwargs['game_uuid']).first()
                except ValidationError:
                    self.game = None

                if self.game:
                    self.gameplayer = GamePlayer.objects.filter(game=self.game, player=self.player).first()
                    if self.game.status == 'active':
                        self.is_current_player = self.player == self.game.current_player.player
                        self.current_player = self.game.current_player
                    else:
                        self.is_current_player = False


class InitializeGame(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/start_game_landing_page.html')
        context = {}
        return HttpResponse(template.render(context, request))


class JoinGame(BorkleBaseView, JoinGameView):
    pass


class CancelGame(BorkleBaseView, CancelGameView):
    pass


class LeaveGame(BorkleBaseView, LeaveGameView):
    pass


class Dashboard(BorkleBaseView, DashboardBase):
    def setup(self, request, *args, **kwargs):
        super(Dashboard, self).setup(request, *args, **kwargs)


class DashboardApi(BorkleBaseView, DashboardApiBase):

    def _format_player(self, player, current_player):
        return {
            'username': player.username,
            'ready': player.ready,
            'isCurrentPlayer': player == current_player,
        }


class InitializeDistributedGame(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/generic_form.html')
        form = InitializeGameForm(
            initial={
                'how_many_points_are_you_playing_to': 10000,
                'initializing_player_id': self.player.pk
            }
        )
        context = {
            'form': form,
            'form_header': 'Start a game!'
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        form = InitializeGameForm(request.POST)
        if form.is_valid():
            num_players = 1
            max_score = int(request.POST['how_many_points_are_you_playing_to'])
            if max_score < 1:
                max_score = 100
            player_fields = ['player_1', 'player_2', 'player_3', 'player_4', 'player_5', ]
            invited_players = []
            for field in player_fields:
                if request.POST.get(field):
                    player_username = request.POST[field]
                    player = Player.get_by_username(username=player_username)
                    invited_players.append(player)

            game, game_player = BorkleGame.create(max_score=max_score, invited_players=invited_players, initial_player=self.player)
            return redirect(reverse('borkle_game_board', kwargs={'game_uuid': game.uuid}))

        template = loader.get_template('bogames/generic_form.html')
        context = {
            'form': form,
            'form_header': 'Start a game!'
        }
        return HttpResponse(template.render(context, request))


class InitializeLocalGame(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/generic_form.html')
        form = InitializePracticeGameForm(
            initial={
                'how_many_points_are_you_playing_to': 10000,
            }
        )
        context = {
            'form': form,
            'form_header': 'Start a practice game!'
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You need to log in to view that page')
            return redirect(reverse('session_manager_login'))

        form = InitializePracticeGameForm(request.POST)
        if form.is_valid():
            num_players = 1
            max_score = int(request.POST['how_many_points_are_you_playing_to'])
            if max_score < 1:
                max_score = 100
            game, game_player = BorkleGame.create(
                max_score=max_score,
                invited_players=[],
                initial_player=self.player,
                code_name_prefix='practice',
                game_type='practice'
            )
            game.get_status()
            return redirect(reverse('borkle_game_board', kwargs={'game_uuid': game.uuid}))

        template = loader.get_template('bogames/generic_form.html')
        context = {
            'form': form,
            'form_header': 'Start a practice game!'
        }
        return HttpResponse(template.render(context, request))
