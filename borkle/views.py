from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, JsonResponse

from session_manager.views import AuthenticatedView
from django.views import View

from borkle.forms import InitializeGameForm, InitializePracticeGameForm
from borkle.models import Player, Game, GamePlayer, ScoreSet
from borkle.utils import get_dice_image_path


class BorkleBaseView(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(BorkleBaseView, self).setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.player = Player.get_or_create(user=self.request.user)
            request.session['player_id'] = self.player.pk
            if 'game_uuid' in kwargs:
                try:
                    self.game = Game.objects.filter(uuid=kwargs['game_uuid']).first()
                except ValidationError:
                    self.game = None

                if self.game:
                    self.gameplayer = GamePlayer.objects.filter(game=self.game, player=self.player).first()
                    if self.game.status == 'active':
                        self.is_current_player = self.player == self.game.current_player.player
                    else:
                        self.is_current_player = False


class BorkleProtectedTurnView(BorkleBaseView):
    def setup(self, request, *args, **kwargs):
        super(BorkleProtectedTurnView, self).setup(request, *args, **kwargs)

        if not self.is_current_player:
            return self.handle_no_permission()


class Dashboard(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        if 'refresh' in request.path:
            template = loader.get_template('borkle/dashboard_includes/dashboard.html')
        else:
            template = loader.get_template('borkle/dashboard.html')
        context = {
            'player': self.player,
        }
        return HttpResponse(template.render(context, request))


class InitializeGame(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/start_game_landing_page.html')
        context = {}
        return HttpResponse(template.render(context, request))


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

            game, game_player = Game.create(max_score=max_score, invited_players=invited_players, initial_player=self.player)
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
            game, game_player = Game.create(
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


class JoinGameView(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        self.player.join_game(self.game)
        return redirect(reverse('borkle_game_board', kwargs={'game_uuid': self.game.uuid}))


class DeclineGameView(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        self.player.decline_game(self.game)
        return redirect(reverse('borkle_dashboard'))


class CancelGameView(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        if self.game.created_by == self.player:
            if request.GET.get('src', '') == 'game':
                cancel_url = reverse('borkle_game_board', kwargs={'game_uuid': self.game.uuid})
            else:
                cancel_url = reverse('borkle_dashboard')

            template = loader.get_template('borkle/confirm_action.html')
            context = {
                'cancel_url': cancel_url,
                'form_header': 'Are you sure you want to cancel the game?'
            }
            return HttpResponse(template.render(context, request))
        else:
            messages.error(request, 'Permission denied. Contact game owner for help.')

    def post(self, request, *args, **kwargs):
        if self.game.created_by == self.player:
            messages.success(request, 'Game cancelled.')
            self.game.delete()
        else:
            messages.error(request, 'Permission denied. Contact game owner for help.')
        return redirect(reverse('borkle_dashboard'))


class LeaveGameView(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/confirm_action.html')
        context = {
            'cancel_url': reverse('borkle_game_board', kwargs={'game_uuid': self.game.uuid}),
            'form_header': 'Are you sure you want to leave the game?'
        }
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        self.game.boot_player(self.gameplayer)
        messages.success(request, 'Successfully left game.')
        if self.game.gameplayer_set.count() == 0:
            self.game.delete()
        return redirect(reverse('borkle_dashboard'))
