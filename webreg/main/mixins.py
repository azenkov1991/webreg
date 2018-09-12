from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
from main.models import SiteConfig


class ProfileRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated and have profile.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            site = get_current_site(request)
            self.login_url = site.siteconfig.login_url
        except SiteConfig.DoesNotExist as e:
            raise ImproperlyConfigured("Нет настройки для сайта " + site.domain) from e
        if not request.user.is_authenticated or \
           not request.user_profile:
            return self.handle_no_permission()
        return super(ProfileRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProfileRequiredMixinForApi(AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated and have profile.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or \
           not request.user_profile:
            return HttpResponse(status=403)
        return super(ProfileRequiredMixinForApi, self).dispatch(request, *args, **kwargs)
