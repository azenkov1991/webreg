from django import forms
from django.contrib.auth.forms import UsernameField, AuthenticationForm as DjangoAuthenticationForm
from main.models import UserProfile

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

class UserProfileForm(forms.ModelForm):
    def clean(self):
        if self._errors:
            return self.cleaned_data

        users = self.cleaned_data['user']
        site = self.cleaned_data['site']
        # для каждого пользователя и сайта убедится в уникальности определения UserProfile
        for user in users:
            try:
                user_profile = UserProfile.objects.get(site=site, user=user)
                if self.instance.id and self.instance.id!=user_profile.id:
                    raise forms.ValidationError("Для пользователя %s и сайта %s уже существует профиль id=%s " %
                                     (user, site, user_profile.id))
            except UserProfile.DoesNotExist:
                pass





