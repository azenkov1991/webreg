from datetime import datetime
from django import template

register = template.Library()


@register.filter
def short_day_week(date):
    return ['пн', 'вт', 'ср' , 'чт', 'пт', 'сб', 'вс'][date.weekday()]


@register.filter
def day_week(date):
    return ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье'][date.weekday()]




