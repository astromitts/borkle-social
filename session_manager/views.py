from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect, resolve_url
from django.template import loader
from django.views import View
from django.urls import reverse

from urllib.parse import urlparse

from session_manager.forms import (
    CreateUserForm,
    LoginUserNameForm,
    LoginUserPasswordForm,
    LoginUserTokenForm,
    ResetPasswordForm,
)

from session_manager.models import SessionManager, UserToken


class CreateUserView(View):
    """ Views for a new user registration
    """
    def setup(self, request, *args, **kwargs):
        super(CreateUserView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/register.html')
        self.context = {}

    def get(self, request, *args, **kwargs):
        form = CreateUserForm()
        self.context.update({
            'form': form,
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            if SessionManager.user_exists(email=request.POST['email']):
                messages.error(request, 'A user with this email address already exists.')
                self.context.update({
                    'form': form,
                })
                return HttpResponse(self.template.render(self.context, request))
            else:
                user = SessionManager.create_user(
                    email=request.POST['email'],
                    username=request.POST['username'],
                    password=request.POST['password']
                )
                messages.success(request, 'Registration complete! Please log in to continue.')
                return redirect(reverse('session_manager_login'))
        else:
            self.context.update({
                'form': form,
            })
            return HttpResponse(self.template.render(self.context, request))


class LoginUserView(View):
    """ Views for logging in an existing user
    """
    def setup(self, request, *args, **kwargs):
        super(LoginUserView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/login.html')
        self.context = {}

    def get(self, request, *args, **kwargs):
        # check if a login token was provided
        if request.GET.get('token') and request.GET.get('user'):
            token, token_error_message = UserToken.get_token(token=request.GET['token'], username=request.GET['user'], token_type='login')
            if token:
                if token.is_valid:
                    # a valid token/user combination was given, so log in and delete the token
                    login(request, token.user)
                    request.session['user_is_authenticated'] = True
                    request.session['user_id'] = token.user.pk
                    # messages.success(request, 'Log in successful.')
                    token.delete()
                    return redirect(reverse('bogames_landingpage'))
                else:
                    # provided token was found, but it is expired
                    # clean up the token
                    token.delete()
                    messages.error(request, 'Token is expired.')
            else:
                # no matching token was found for provided user/token
                messages.error(request, token_error_message)

        # no token was provided, or it was invalid, so just present the login form
        form = LoginUserNameForm()
        self.context.update({
            'form': form,
            'form_step': 1
        })
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        # we should only get here if they submitted the form instead of a token in the URL
        # standard Django form handling here
        if 'password' in request.POST:
            form = LoginUserPasswordForm(request.POST)
            if form.is_valid():
                user = SessionManager.get_user_by_id(request.POST['user_id'])
                if SessionManager.check_password(user, request.POST['password']):
                    login(request, user)
                    request.session['user_is_authenticated'] = True
                    # messages.success(request, 'Log in successful.')
                    if request.session.get('login_redirect_from'):
                        return redirect(request.session['login_redirect_from'])
                    return redirect(reverse(settings.LOGIN_SUCCESS_REDIRECT))
                else:
                    messages.error(request, 'Password incorrect.')
            else:
                messages.error(request, 'Something went wrong. Please correct errors below.')

        elif 'send_token' in request.POST:
            user = SessionManager.get_user_by_id(request.session['user_id'])
            token = UserToken(
                user=user,
                token_type='login',
            )
            token.save()
            token.send_login_email()
            messages.success(
                request,
                'An email has been sent to {} containing a temporary log in token. It will expire in 24 hours.'.format(user.email)
            )
            form = LoginUserTokenForm(initial={'user_id': user.pk})
            self.context.update({'form_step': 2})
        elif 'login_token' in request.POST:
            token, token_error_message = UserToken.get_token(
                token=request.POST['login_token'],
                username=SessionManager.get_user_by_id(request.session['user_id']).username,
                token_type='login'
            )
            if token:
                if token.is_valid:
                    # a valid token/user combination was given, so log in and delete the token
                    login(request, token.user)
                    request.session['user_is_authenticated'] = True
                    request.session['user_id'] = token.user.pk
                    # messages.success(request, 'Log in successful.')
                    token.delete()
                    return redirect(reverse('bogames_landingpage'))
                else:
                    # provided token was found, but it is expired
                    # clean up the token
                    token.delete()
                    messages.error(request, 'Token is expired.')
            else:
                messages.error(request, 'Token not found. Perhaps you already used it?')
            return redirect(reverse('session_manager_login'))
        else:
            form = LoginUserNameForm(request.POST)
            self.context.update({'form_step': 1})
            if form.is_valid():
                if '@' in request.POST['username_or_email']:

                    user = SessionManager.get_user_by_email(username=request.POST['username_or_email'])
                else:
                    user = SessionManager.get_user_by_username(username=request.POST['username_or_email'])

                if not user:
                    messages.error(request, error_reason)
                    self.context.update({
                        'form': form,
                    })
                    messages.error(request, 'Something went wrong. Please correct errors below.')
                else:
                    request.session['user_id'] = user.pk
                    form = LoginUserPasswordForm(initial={'user_id': user.pk})
                    self.context.update({'form_step': 2})

        self.context.update({
            'form': form,
        })
        return HttpResponse(self.template.render(self.context, request))


class ResetPasswordWithTokenView(View):
    def setup(self, request, *args, **kwargs):
        super(ResetPasswordWithTokenView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/generic_form.html')
        self.context = {}
        # get the token and error message, needed for both GET and POST
        self.token, self.token_error_message = UserToken.get_token(
            token=request.GET.get('token'),
            username=request.GET.get('user'),
            token_type='reset'
        )

    def get(self, request, *args, **kwargs):
        # If we find a valid token, show the reset form with the user's ID passed to it
        if self.token:
            if self.token.is_valid:
                form = ResetPasswordForm(initial={'user_id': self.token.user.id})
                self.context.update({'form': form})
            else:
                messages.error(request, 'Token is expired.')
        else:
            messages.error(request, self.token_error_message)
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        # if a valid token was given and the form is valid, reset user's password
        # and redirect to login
        if self.token:
            if self.token.is_valid:
                if form.is_valid():
                    user = SessionManager.get_user_by_id(request.POST['user_id'])
                    user.set_password(request.POST['password'])
                    user.save()
                    messages.success(request, 'Password reset. Please log in to continue.')
                    self.token.delete()
                    return redirect(reverse('session_manager_login'))
            else:
                messages.error(request, 'Token is expired.')
        else:
            messages.error(request, self.token_error_message)
        self.context.update({'form': form})
        return HttpResponse(self.template.render(self.context, request))


class ResetPasswordFromProfileView(View):
    def setup(self, request, *args, **kwargs):
        super(ResetPasswordFromProfileView, self).setup(request, *args, **kwargs)
        self.template = loader.get_template('session_manager/reset_password.html')
        self.context = {}
        self.user = request.user

    def get(self, request, *args, **kwargs):
        form = ResetPasswordForm(initial={'user_id': self.user.id})
        self.context.update({'form': form})
        return HttpResponse(self.template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = self.request.user
            user.set_password(request.POST['password'])
            user.save()
            messages.success(request, 'Your password has been reset. Please log in again to continue.')
            request.logout(user)
            return redirect(reverse('session_manager_login'))
        self.context.update({'form': form})
        return HttpResponse(self.template.render(self.context, request))


class LogOutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        request.session['user_is_authenticated'] = False
        request.session['user_id'] = None
        request.session['player_id'] = None

        messages.success(request, 'Logged out.')
        return redirect(reverse('session_manager_login'))


class Index(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('session_manager/index.html')
        return HttpResponse(template.render({}, request))
