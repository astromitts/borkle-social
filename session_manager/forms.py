from django.forms import (
    ModelForm,
    PasswordInput,
    CharField,
    HiddenInput,
    IntegerField,
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from session_manager.models import SessionManager
from session_manager.utils import special_chars

def _get_password_errors(clean_password):
    has_alpha = False
    has_number = False
    has_special = False
    pw_errors = []
    if len(clean_password) < 8:
        pw_errors.append('<li>Must be at least 8 characters.</li>')
    for char in clean_password:
        if char.isalpha():
            has_alpha = True
        if char.isnumeric():
            has_number = True
        if char in special_chars:
            has_special = True
    if not has_alpha:
        pw_errors.append('<li>Must contain at least one letter.</li>')
    if not has_number:
        pw_errors.append('<li>Must contain at least one number.</li>')
    if not has_special:
        pw_errors.append('<li>Must contain at least one special character ({}).</li>'.format(', '.join(special_chars)))
    return pw_errors


class CreateUserForm(ModelForm):


    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Minimum 3 characters. Letters, numbers, and underscores only.'
        self.fields['password'].help_text = 'Minimum 8 characters. Must contain at least 1 letter, 1 number and 1 special character.'

    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        widgets = {
            'password': PasswordInput(),
        }

    def clean(self):
        super(CreateUserForm, self).clean()
        data = self.cleaned_data
        errors = []

        clean_password = data['password']
        pw_errors = _get_password_errors(clean_password)
        if pw_errors:
            errors.append('Invalid password: <ul>{}</ul>'.format(''.join(pw_errors)))

        clean_username = self.cleaned_data['username']
        un_errors = []
        if len(clean_username) < 3:
            un_errors.append('<li>Must be at least 3 characters.</li>')

        un_invalid_char = False
        for char in clean_username:
            un_invalid_char = not char.isalpha() and not char.isnumeric() and char != '_'

        if un_invalid_char:
            un_errors.append('<li>Letters, numbers, and underscores only, please.</li>')

        user_exists = SessionManager.get_user_by_username(username=clean_username)
        if user_exists:
            un_errors.append('<li>A user with this username already exists.</li>')

        if un_errors:
            errors.append('Invalid username: <ul>{}</ul>'.format(''.join(un_errors)))

        if errors:
            raise ValidationError(mark_safe('<br />'.join(errors)))
        return data


class ResetPasswordForm(ModelForm):
    user_id = CharField(widget=HiddenInput())
    class Meta:
        model = User
        fields = ['password', 'user_id']
        widgets = {
            'password': PasswordInput(),
            'user_id': HiddenInput()
        }

    def clean(self):
        super(ResetPasswordForm, self).clean()
        data = self.cleaned_data
        errors = []
        clean_password = data['password']
        pw_errors = _get_password_errors(clean_password)
        if pw_errors:
            error_message = 'Invalid password: <ul>{}</ul>'.format(''.join(pw_errors))
            raise ValidationError(mark_safe(error_message))
        return data

class LoginUserNameForm(ModelForm):
    username_or_email = CharField(required=True)
    class Meta:
        model = User
        fields = ['username_or_email',]


class LoginUserPasswordForm(ModelForm):
    user_id = IntegerField(required=True, widget=HiddenInput())
    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': PasswordInput(),
            'user_id': HiddenInput(),
        }


class LoginUserTokenForm(ModelForm):
    user_id = IntegerField(required=True, widget=HiddenInput())
    login_token = CharField(required=True)
    class Meta:
        model = User
        fields = ['login_token']
        widgets = {
            'user_id': HiddenInput(),
        }
