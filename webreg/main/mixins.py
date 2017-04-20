from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponse

class ProfileRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated and have profile.
    """
    def dispatch(self, request, *args, **kwargs):
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
