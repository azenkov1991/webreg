import threading
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import ObjectDoesNotExist
from main.models import UserProfile


class AddUserProfileMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            site = get_current_site(request)
            request.user_profile = UserProfile.objects.get(site_id=site.id, user__id=request.user.id)
        except ObjectDoesNotExist:
            request.user_profile = None
        response = self.get_response(request)
        return response


class GlobalRequestMiddleware(object):
    _threadmap = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._threadmap[threading.get_ident()] = request
        response = self.get_response(request)
        try:
            del self._threadmap[threading.get_ident()]
        except KeyError:
            pass

        return response

    @classmethod
    def get_current_request(cls):
        return cls._threadmap.get(threading.get_ident(), None)

    @classmethod
    def get_current_session(cls):
        request = cls.get_current_request()
        if request:
            return request.session
        else:
            return None

    def process_exception(self, request, exception):
        try:
            del self._threadmap[threading.get_ident()]
        except KeyError:
            pass

