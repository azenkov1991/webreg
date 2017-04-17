from datetime import datetime
from django import template

register = template.Library()

@register.filter
def short_day_week(date):
    return ['пн', 'вт', 'ср' , 'чт', 'пт', 'сб', 'вс'][date.weekday()]




