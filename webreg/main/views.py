from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.views.generic import TemplateView
import datetime


class TimeTableView(TemplateView):
    template_name = "timetable/test.html"

class SpecialistRowView(TemplateView):
    template_name = "timetable/specialist_row.html"
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        today = datetime.datetime.today()
        dates = []
        times = [
            {
                "text": "12:45",
                "end": "13:00",
                "color": "red"
            },
            {
                "text": "12:45",
                "end": "13:00",
                "color": "blue"
            },
            {
                "text": "12:45",
                "end": "13:00",
                "color": "green"
            },
            {
                "text": "12:45",
                "end": "13:00",
                "color": "yellow"
            },
        ]

        for i in range(0,14):
            date = today + datetime.timedelta(i)
            dates.append({
                'date': date,
                'times': times
            })
        context['dates'] = dates

        return self.render_to_response(context)









