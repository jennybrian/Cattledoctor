from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = {
            'invalid_login': 'Incorrect username or password. Please try again.',
            'inactive': 'This account is inactive. Please contact support.',
            'required': 'This field is required.',
        }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is None:
            raise forms.ValidationError(
                {'username': 'Please enter your username'}
            )
        if password is None:
            raise forms.ValidationError(
                {'password': 'Please enter your password'}
            )

        return super().clean()