from django.conf.urls import url
from main.api.timetable import SpecialistsFreeCells, SpecialistAllCells


apiurlpatterns = [
    url(r'timetable/free/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/free/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/(\d{1,4})$', SpecialistsFreeCells.as_view()),
    url(r'timetable/(\d{1,4})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$', SpecialistAllCells.as_view())
]


