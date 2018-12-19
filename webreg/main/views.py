from django.views.generic.base import  RedirectView
from django.contrib.sites.shortcuts import get_current_site
from main.models import SiteConfig


class MainView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        site = get_current_site(self.request)
        return site.siteconfig.login_url












