import datetime
from django import template

register = template.Library()


@register.filter
def short_day_week(date):
    return ['пн', 'вт', 'ср' , 'чт', 'пт', 'сб', 'вс'][date.weekday()]


@register.filter
def day_week(date):
    return ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье'][date.weekday()]


@register.filter
def get_range(value, number):
    if value < 7:
        return [{'points': False,
                 'page': index + 1} for index in range(value)]
    else:
        result = [{'points': False,
                   'page': index} for index in filter(lambda item: 1 <= item <= value, range(number-3, number+3))]
        return result


@register.filter
def date_gt(date1, date2=None):
    if not date2:
        date2 = datetime.date.today()
    return date1 > date2



