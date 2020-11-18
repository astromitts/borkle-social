from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, JsonResponse

from session_manager.views import AuthenticatedView
from django.views import View

from borkle.forms import InitializeGameForm, InitializePracticeGameForm

from borkle.models import Player, Game, GamePlayer, ScoreSet


def error_is_on_missing_game(path):
    path_parts = path.split('/')
    if path_parts[1] == 'game':
        game_uuid = path_parts[2]
        game = Game.objects.filter(uuid=game_uuid).first()
        return not game
    return False

def handler404(request, exception):
    if error_is_on_missing_game(request.path_info):
        return render(request, 'borkle/errors/game_not_found.html', status=404)
    return render(request, 'borkle/errors/404.html', status=404)


def handler500(request):
    if error_is_on_missing_game(request.path_info):
        return render(request, 'borkle/errors/game_not_found.html', status=404)
    return render(request, 'borkle/errors/500.html', status=500)


class BorkleBaseView(AuthenticatedView):
    def setup(self, request, *args, **kwargs):
        super(BorkleBaseView, self).setup(request, *args, **kwargs)
        self.player = Player.get_or_create(user=self.request.user)
        if 'game_uuid' in kwargs:
            self.game = Game.objects.filter(uuid=kwargs['game_uuid']).first()
            if self.game:
                self.gameplayer = GamePlayer.objects.filter(game=self.game, player=self.player).first()
                if self.game.status == 'active':
                    self.is_current_player = self.player == self.game.current_player.player
                else:
                    self.is_current_player = False
            else:
                raise Exception('Game Not Found')


class BorkleProtectedGameView(BorkleBaseView):
    def setup(self, request, *args, **kwargs):
        super(BorkleProtectedGameView, self).setup(request, *args, **kwargs)
        if not self.gameplayer:
            return self.handle_no_permission()


class BorkleProtectedTurnView(BorkleProtectedGameView):
    def setup(self, request, *args, **kwargs):
        super(BorkleProtectedTurnView, self).setup(request, *args, **kwargs)

        if not self.is_current_player:
            return self.handle_no_permission()


class Dashboard(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('about'))
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
        template = loader.get_template('borkle/generic_form.html')
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
            return redirect(reverse('dashboard'))

        template = loader.get_template('borkle/generic_form.html')
        context = {
            'form': form,
            'form_header': 'Start a game!'
        }
        return HttpResponse(template.render(context, request))


class InitializeLocalGame(BorkleBaseView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/generic_form.html')
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
        form = InitializePracticeGameForm(request.POST)
        if form.is_valid():
            num_players = 1
            max_score = int(request.POST['how_many_points_are_you_playing_to'])
            if max_score < 1:
                max_score = 100
            game, game_player = Game.create(max_score=max_score, invited_players=[], initial_player=self.player, code_name_prefix='practice')
            game.get_status()
            return redirect(reverse('game_board', kwargs={'game_uuid': game.uuid}))

        template = loader.get_template('borkle/generic_form.html')
        context = {
            'form': form,
            'form_header': 'Start a practice game!'
        }
        return HttpResponse(template.render(context, request))


class JoinGameView(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        self.player.join_game(self.game)
        return redirect(reverse('dashboard'))


class DeclineGameView(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        self.player.decline_game(self.game)
        return redirect(reverse('dashboard'))


class CancelGameView(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        if self.game.created_by == self.player:
            self.game.delete()
        else:
            messages.error(request, 'Permission denied. Contact game owner for help.')
        return redirect(reverse('dashboard'))


class GameStatusView(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        context = {
            'game': self.game
        }
        game_status = self.game.get_status()
        if game_status == 'active':
            template = loader.get_template('borkle/game_waiting_players.html')
        else:
            template = loader.get_template('borkle/game_waiting_players.html')
        return HttpResponse(template.render(context, request))


class GameCheckForChange(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        last_action_count = int(request.GET.get('initial_action_count', '0'))
        game_status = self.game.get_status()
        game_history_url = reverse('game_history', kwargs={'game_uuid': self.game.uuid})
        return JsonResponse(
            {
                'changed': last_action_count < self.game.action_count,
                'status': game_status,
                'game_history_url': game_history_url
            }
        )


class GameOverHistory(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        winners = self.game.winner
        context = {
            'game': self.game,
            'history': self.game.turn_history,
            'winners': winners,
            'is_tie': len(winners) > 1,
        }
        template = loader.get_template('borkle/game_history.html')
        return HttpResponse(template.render(context, request))


class GameBoard(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        if self.game.status == 'over':
            return redirect(reverse('game_history', kwargs={'game_uuid': self.game.uuid}))
        else:
            game_history_redirect = None

        context = {
            'game': self.game,
            'player': self.player,
            'gameplayer': self.gameplayer,
            'is_owner': self.game.created_by == self.player,
            'is_current_player': self.is_current_player,
            'rolled_dice': self.game.current_player.rolled_dice,
        }
        game_status = self.game.get_status()
        if 'gameboard' in request.path:
            template = loader.get_template('borkle/gameboard_includes/gameboard.html')
        else:
            context.update({'autorefresh': not self.is_current_player})
            template = loader.get_template('borkle/game.html')
        return HttpResponse(template.render(context, request))


class GameRollDice(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/gameboard_includes/diceboard.html')
        active_roll = False
        can_undo = True
        if '/roll/' in self.request.path:
            active_roll = True
            can_undo = False
            if self.is_current_player:
                self.gameplayer.roll_dice()
                if not self.game.current_player.current_turn.has_score:
                    self.gameplayer.current_turn.borkle()

        if self.game.current_player.current_turn:
            has_score = self.game.current_player.current_turn.has_score
            scoresets = self.game.current_player.current_turn.scoreset_set.order_by('-pk').all()
        else:
            has_score = False
            scoresets = []
        context = {
            'game': self.game,
            'rolled_dice': self.game.current_player.rolled_dice,
            'is_current_player': self.is_current_player,
            'has_score': has_score,
            'scoresets': scoresets,
            'borkle': not has_score,
            'active_roll': active_roll,
            'can_undo': can_undo,
            'initial_action_count': self.game.action_count,
        }
        return HttpResponse(template.render(context, request))


class GameScoreBoard(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/gameboard_includes/scoreboard.html')
        context = {
            'game': self.game,
            'gameplayer': self.gameplayer,
        }
        return HttpResponse(template.render(context, request))


class GameTurnBoard(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('borkle/gameboard_includes/historyboard.html')

        context = {
            'game': self.game,
            'history': self.game.turn_history
        }
        return HttpResponse(template.render(context, request))


class GameAdvancePlayer(BorkleProtectedTurnView):
    def get(self, request, *args, **kwargs):
        self.game.advance_player()
        return redirect(reverse('game_board', kwargs={'game_uuid': self.game.uuid}))


class CheckScoreSelection(BorkleProtectedTurnView):

    def post(self, request, *args, **kwargs):
        dice_value_fields = []
        for field in request.POST.keys():
            if field.startswith('rolled_dice'):
                dice_value_fields.append(field)
        has_score = self.game.current_player.current_turn.check_score(dice_value_fields)
        return JsonResponse({'has_score': has_score})


class MakeScoreSelection(BorkleProtectedTurnView):

    def post(self, request, *args, **kwargs):
        dice_value_fields = []
        for field in request.POST.keys():
            if field.startswith('rolled_dice'):
                dice_value_fields.append(field)
        self.game.current_player.current_turn.make_selection(dice_value_fields)
        return JsonResponse({'success': True})


class UndoScoreSelection(BorkleProtectedTurnView):
    def get(self, request, *args, **kwargs):
        score_selection = self.game.current_player.current_turn.undo_score_selection(kwargs['selection_id'])
        return JsonResponse({'success': True})

class CheckPlayerStatus(BorkleProtectedGameView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'is_current_player': self.is_current_player})
