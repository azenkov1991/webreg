from django.conf.urls import url
from main.api.timetable import SpecialistsFreeCells, SpecialistAllCells
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout, password_reset


apiurlpatterns = [
    url(r'timetable/free/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/free/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/(\d{1,4})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistAllCells.as_view())
]


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^accounts/login', login, {'template_name': "account/login.html",
                                    'extra_context': {'redirect_field_value': '/',
                                                      'redirect_field_name': 'next'}}, name="account_login"),
    url(r'^accounts/logout', logout, {'template_name': "account/logout.html"}, name="account_logout"),
    url(r'^accounts/password-reset', password_reset, {'template_name': "account/password_reset_.html"},
        name="account_reset_password")
]
