from django import forms
from django.contrib.auth.forms import UsernameField, AuthenticationForm as DjangoAuthenticationForm


class AuthenticationForm(DjangoAuthenticationForm):
    username = UsernameField(
        label="Пользователь",
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': ''}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
    )

    error_messages = {
        'invalid_login': "Неверное имя пользователя или пароль",
        'inactive': "Аккаунт неактивен",
    }


