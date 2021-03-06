"""django_project_root URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views import defaults as default_views
from django.conf.urls.static import static
from main.urls import apiurlpatterns as mainapiurlpatterns
from main.urls import urlpatterns as main_urlpatterns
from patient_writer.urls import apiurlpatterns as patient_writer_apiurlpatterns

apiurlpatterns = mainapiurlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^pwriter/', include('patient_writer.urls', namespace="patient_writer")),
    url(r'^infomat_writer/', include('infomat_writer.urls', namespace="infomat_writer")),
    url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'api/', include(apiurlpatterns)),
    url(r'api/pwriter/', include(patient_writer_apiurlpatterns))
] + main_urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]

