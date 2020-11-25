from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import session_manager.views as session_views
import borkle.views as app_views
import borkle.api_views as api_views

handler404 = app_views.handler404
handler500 = app_views.handler500

urlpatterns = [
    path('accounts/', include('allauth.urls')),
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
    path('game/<str:game_uuid>/history/', api_views.GameBoardApiVersion.as_view(), name='game_history'),
    path('game/<str:game_uuid>/leave/', app_views.LeaveGameView.as_view(), name='leave_game'),
    path('game/<str:game_uuid>/play/', api_views.GameBoardApiVersion.as_view(), name='game_board'),
    path('game/<str:game_uuid>/api/<str:api_target>/', csrf_exempt(api_views.GameStatusApi.as_view()), name='game_api'),
    path('game/<str:game_uuid>/cancel/', app_views.CancelGameView.as_view(), name='game_cancel'),
    path('game/<str:game_uuid>/join/', app_views.JoinGameView.as_view(), name='game_accept_invitation_link'),
    path('game/<str:game_uuid>/decline/', app_views.DeclineGameView.as_view(), name='game_decline_invitation_link'),
    path('game/<str:game_uuid>/status/', app_views.GameStatusView.as_view(), name='game_status'),
    path('.well-known/acme-challenge/lCzY3y0gpnyq4kLsq772c6QAQT7WAqPl8Pdzu81xJFk', app_views.ssl, name='ssl_cert')
]
