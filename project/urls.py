from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import session_manager.views as session_views
import borkle.views as app_views

handler404 = app_views.handler404
handler500 = app_views.handler500

urlpatterns = [
    path('dashboard/', app_views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/refresh/', app_views.Dashboard.as_view(), name='dashboard_refresh'),
    path('', TemplateView.as_view(template_name='borkle/about.html'), name='about'),
    path('scorechart/', TemplateView.as_view(template_name='borkle/score_chart.html'), name='score_chart'),
    path('admin/', admin.site.urls),
    path('register/', session_views.CreateUserView.as_view(), name='session_manager_register'),
    path('login/', session_views.LoginUserView.as_view(), name='session_manager_login'),
    path('logout/', session_views.LogOutUserView.as_view(), name='session_manager_logout'),
    path('resetpassword/', session_views.ResetPasswordWithTokenView.as_view(), name='session_manager_token_reset_password'),
    path('profile/resetpassword/', session_views.ResetPasswordFromProfileView.as_view(), name='session_manager_profile_reset_password'),
    path('session/', session_views.Index.as_view(), name='session_manager_index'),
    path('startgame/', app_views.InitializeGame.as_view(), name='initialize_game'),
    path('startgame/distributed', app_views.InitializeDistributedGame.as_view(), name='initialize_distributed_game'),
    path('startgame/practice/', app_views.InitializeLocalGame.as_view(), name='initialize_local_game'),
    path('game/<str:game_uuid>/history/', app_views.GameOverHistory.as_view(), name='game_history'),
    path('game/<str:game_uuid>/board/', app_views.GameBoard.as_view(), name='game_board'),
    path('game/<str:game_uuid>/board/checkplayerstatus/', app_views.CheckPlayerStatus.as_view(), name='game_board_check_player_status'),
    path('game/<str:game_uuid>/board/checkgamechanged/', app_views.GameCheckForChange.as_view(), name='game_board_check_game_changed'),
    path('game/<str:game_uuid>/board/scoreboard/', app_views.GameScoreBoard.as_view(), name='game_board_scoreboard'),
    path('game/<str:game_uuid>/board/history/', app_views.GameTurnBoard.as_view(), name='game_board_turn_history'),
    path('game/<str:game_uuid>/board/gameboard/', app_views.GameBoard.as_view(), name='game_board_refresh'),
    path('game/<str:game_uuid>/board/dice/roll/', app_views.GameRollDice.as_view(), name='game_board_roll_dice'),
    path('game/<str:game_uuid>/board/dice/selectdice/', csrf_exempt(app_views.MakeScoreSelection.as_view()), name='game_board_make_score_selection'),
    path('game/<str:game_uuid>/board/dice/checkdice/', csrf_exempt(app_views.CheckScoreSelection.as_view()), name='game_board_check_score_selection'),
    path('game/<str:game_uuid>/board/dice/undoselection/<int:selection_id>/', app_views.UndoScoreSelection.as_view(), name='game_board_undo_selection'),
    path('game/<str:game_uuid>/board/dice/', app_views.GameRollDice.as_view(), name='game_board_view_rolled_dice'),
    path('game/<str:game_uuid>/board/advanceplayer/', app_views.GameAdvancePlayer.as_view(), name='game_board_advance_player'),
    path('game/<str:game_uuid>/cancel/', app_views.CancelGameView.as_view(), name='game_cancel'),
    path('game/<str:game_uuid>/join/', app_views.JoinGameView.as_view(), name='game_accept_invitation_link'),
    path('game/<str:game_uuid>/decline/', app_views.DeclineGameView.as_view(), name='game_decline_invitation_link'),
    path('game/<str:game_uuid>/status/', app_views.GameStatusView.as_view(), name='game_status'),
]
