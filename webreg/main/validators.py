from datetime import date
from django.core.exceptions import ValidationError


def oms_polis_number_validation(num):
    def check_sum(num):
        sm = 0
        numlen = len(num)
        for i in range(0, numlen):
            index = numlen - i - 1
            p = int(num[index])
            if not index % 2:
                p *= 2
                if p > 9:
                    p -= 9
            sm += p
        if not sm % 10:
            return True
        return False
    if len(num) not in (6, 7, 9, 16):
        raise ValidationError('Полис неправильной длины')
    if len(num) == 16 and not check_sum(num):
        raise ValidationError('Неправильный номер полиса. Контрольныя сумма не совпадает')


def birth_date_validation(date_birth):
    if date_birth <= date(year=1900, month=12, day=31):
        raise ValidationError('Некорректная дата')


def mobile_phone_validation(phone):
    if not phone.startswith('+7'):
        raise ValidationError('Телефон должен начинаться на +7')
    elif len(phone) != 18:
        raise ValidationError('Неверный формат телефона')
    return phone.translate({ord('('):None,
                            ord(')'):None,
                            ord('-'):None,
                            ord(' '): None})

