from django.contrib.sites.shortcuts import get_current_site
from django.db.models import ObjectDoesNotExist
from main.models import UserProfile


class AddUserProfileMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            site = get_current_site(request)
            request.user_profile = UserProfile.objects.get(site_id=site.id, user_id=request.user.id)
        except ObjectDoesNotExist:
            request.user_profile = None
        response = self.get_response(request)
        return response
