from django.conf.urls import url
from main.api.timetable import SpecialistsFreeCells


apiurlpatterns = [
    url(r'timetable/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/(\d{1,4})$', SpecialistsFreeCells.as_view()),
]


