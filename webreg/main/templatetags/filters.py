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
def get_range(total_pages, page_number):
    if total_pages < 7:
        return [{'points': False,
                 'page': index + 1} for index in range(total_pages)]
    else:
        left_edge = page_number - 3
        right_edge = page_number + 3
        if (page_number + 3) > total_pages:
            right_edge = total_pages
            left_edge = total_pages - 6
        if (page_number - 3) < 1:
            left_edge = 1
            right_edge = 7
        result = [{'points': False,
                   'page': index} for index in range(left_edge, right_edge +1)]
        return result


@register.filter
def date_gt(date1, date2=None):
    if not date2:
        date2 = datetime.date.today()
    return date1 > date2



