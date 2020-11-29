from django.contrib import admin
from django.conf import settings

from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import session_manager.views as session_views
import bogames.views as base_views

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('', base_views.LandingPage.as_view(), name='bogames_landingpage'),
    path('register/', session_views.CreateUserView.as_view(), name='session_manager_register'),
    path('login/', session_views.LoginUserView.as_view(), name='session_manager_login'),
    path('logout/', session_views.LogOutUserView.as_view(), name='session_manager_logout'),
    path('resetpassword/', session_views.ResetPasswordWithTokenView.as_view(), name='session_manager_token_reset_password'),
    path('profile/resetpassword/', session_views.ResetPasswordFromProfileView.as_view(), name='session_manager_profile_reset_password'),
    path('session/', session_views.Index.as_view(), name='session_manager_index'),
]

if 'borkle' in settings.INSTALLED_APPS:
    import borkle.views as borkle_app_views
    import borkle.api_views as borkle_api_views

    borkle_urls = [
        path('borkle/', borkle_app_views.Dashboard.as_view(), name='borkle_dashboard'),
        path('borkle/about/', TemplateView.as_view(template_name='borkle/about.html'), name='borkle_about'),
        # path('borkle/dashboard/refresh/', borkle_app_views.Dashboard.as_view(), name='borkle_dashboard_refresh'),
        path('borkle/dashboard/api/', borkle_app_views.DashboardApi.as_view(), name='borkle_dashboard_api'),
        path('borkle/scorechart/', TemplateView.as_view(template_name='borkle/score_chart.html'), name='borkle_score_chart'),
        path('borkle/startgame/', borkle_app_views.InitializeGame.as_view(), name='borkle_initialize_game'),
        path('borkle/startgame/distributed', borkle_app_views.InitializeDistributedGame.as_view(), name='borkle_initialize_distributed_game'),
        path('borkle/startgame/practice/', borkle_app_views.InitializeLocalGame.as_view(), name='borkle_initialize_local_game'),
        path('borkle/game/<str:game_uuid>/history/', borkle_api_views.GameBoardApiVersion.as_view(), name='borkle_game_history'),
        path('borkle/game/<str:game_uuid>/leave/', borkle_app_views.LeaveGame.as_view(), name='borkle_leave_game'),
        path('borkle/game/<str:game_uuid>/play/', borkle_api_views.GameBoardApiVersion.as_view(), name='borkle_game_board'),
        path('borkle/game/<str:game_uuid>/api/<str:api_target>/', csrf_exempt(borkle_api_views.GameStatusApi.as_view()), name='borkle_game_api'),
        path('borkle/game/<str:game_uuid>/cancel/', borkle_app_views.CancelGame.as_view(), name='borkle_game_cancel'),
        path('borkle/game/<str:game_uuid>/join/', borkle_app_views.JoinGame.as_view(), name='borkle_game_accept_invitation_link'),
        path('borkle/game/<str:game_uuid>/decline/', base_views.DeclineGameView.as_view(), name='borkle_game_decline_invitation_link'),
    ]

    urlpatterns = urlpatterns + borkle_urls

if 'boatfight' in settings.INSTALLED_APPS:
    import boatfight.views as boatfight_views

    boatfight_urls = [
        path('boatfight/', boatfight_views.Dashboard.as_view(), name='boatfight_dashboard'),
        path('boatfight/dashboard/api/', boatfight_views.DashboardApi.as_view(), name='boatfight_dashboard_api'),
        path('boatfight/startgame/', csrf_exempt(boatfight_views.InitializeGame.as_view()), name='boatfight_start'),
        path('boatfight/game/<str:game_uuid>/leave/', boatfight_views.LeaveGame.as_view(), name='boatfight_leave_game'),
        path('boatfight/game/<str:game_uuid>/cancel/', boatfight_views.CancelGame.as_view(), name='boatfight_game_cancel'),
        path('boatfight/game/<str:game_uuid>/join/', boatfight_views.JoinGame.as_view(), name='boatfight_game_accept_invitation_link'),
        path('boatfight/game/<str:game_uuid>/play/', csrf_exempt(boatfight_views.GameBoard.as_view()), name='boatfight_game'),
        path('boatfight/game/<str:game_uuid>/api/<str:api_target>/', csrf_exempt(boatfight_views.BoatFightApi.as_view()), name='boatfight_api'),
        path('borkle/game/<str:game_uuid>/decline/', base_views.DeclineGameView.as_view(), name='boatfight_game_decline_invitation_link'),

    ]

    urlpatterns = urlpatterns + boatfight_urls
