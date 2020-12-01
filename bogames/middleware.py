from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404

from bs4 import BeautifulSoup
from bogames.models import Game, ErrorLog


json_response_game_not_found = {
    'status': 'error',
    'message': 'Game with that ID not found'
}

json_response_player_not_in_game = {
    'status': 'error',
    'message': 'User not in this game'
}

json_response_unkown_error = {
    'status': 'error',
    'message': 'Unknown error'
}

json_response_authentication_required = {
    'status': 'error',
    'message': 'This endpoint requires authentication'
}

json_page_not_found = {
    'status': 'error',
    'message': 'Unknown API endpoint.'
}


game_not_found_error_message = "I couldn't the game you're looking for. Sorry!"
unkown_error_error_message = "Something went wrong, but I'm not sure what it is. Sorry!"
game_permission_denied_error_message = "It doesn't seem like you belong in this game. Sorry!"
page_not_found_message = "I'm not sure what page you're looking for, but this one doesn't exist. Sorry!"


unauthentication_allowed_url_names = [
    'borkle_score_chart',
    'about',
    'session_manager_login',
    'session_manager_logout',
    'session_manager_register',
    'session_manager_token_reset_password',
]


def bogames_request_validation(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        error_message = None
        status_code = 200

        is_api_request = '/api/' in request.path
        is_static_request = '/static/' in request.path
        try:
            resolved_url = resolve(request.path)
            if not resolved_url.url_name in unauthentication_allowed_url_names:
                if not request.session.get('user_is_authenticated'):
                    if is_api_request:
                        return JsonResponse(json_response_game_not_found, status=403)

                    request.session['login_redirect_from'] = request.path
                    return redirect(reverse('session_manager_login'))
                else:
                    request.session['login_redirect_from'] = None

            if resolved_url.kwargs.get('game_uuid'):
                try:
                    game = Game.objects.filter(uuid=resolved_url.kwargs['game_uuid']).first()
                    if not game:
                        if settings.ENVIRONMENT == 'prod':
                            if is_api_request:
                                return JsonResponse(json_response_game_not_found, status=404)
                            error_message = game_not_found_error_message
                            status_code = 404

                except ValidationError:
                    if is_api_request:
                        if settings.ENVIRONMENT == 'prod':
                            return JsonResponse(json_response_game_not_found, status=500)
                    if settings.ENVIRONMENT == 'prod':
                        error_message = game_not_found_error_message
                        status_code = 404

        except Resolver404:
            if settings.ENVIRONMENT == 'prod':
                if is_api_request:
                    return JsonResponse(json_page_not_found, status=403)
                error_message = page_not_found_message
                status_code = 404

        response = get_response(request)
        status_code = str(response.status_code)

        if status_code.startswith('5') or status_code.startswith('4'):
            error_message = unkown_error_error_message

        if error_message and settings.ENVIRONMENT == 'prod':
            status_code = response.status_code
            if not is_static_request:
                content = BeautifulSoup(response.content)
                summary = content.find('div', {'id': 'summary'})
                error_log = ErrorLog(
                    status_code=status_code,
                    title=str(summary.find('h1')),
                    error=str(summary),
                    source_url=request.path
                )
                error_log.save()
            context = {
                'message': error_message,
                'status_code': status_code
            }
            return render(request, 'bogames/errors/error.html', context=context, status=status_code)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
