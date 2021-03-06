from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout, password_reset
from main.api.timetable import SpecialistsFreeCells, SpecialistAllCells
from main.forms import AuthenticationForm
from main.views import MainView

apiurlpatterns = [
    url(r'timetable/free/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/free/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/(\d{1,4})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistAllCells.as_view())
]


urlpatterns = [
    url(r'^$', MainView.as_view(), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^accounts/login', login, {'template_name': "account/login.html",
                                    'authentication_form': AuthenticationForm,
                                    'extra_context': {'redirect_field_value': '/',
                                                      'redirect_field_name': 'next'}}, name="account_login"),
    url(r'^accounts/logout', logout, {'template_name': "account/logout.html",
                                      'extra_context': {'redirect_field_value': '/',
                                                        'redirect_field_name': 'next'}
                                      }, name="account_logout"),
]

