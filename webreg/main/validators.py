from django.core.exceptions import ValidationError
from functools import reduce
def oms_polis_number_validation(number):
    def check_sum(num):
        length = len(num)
        if length == 0:
            return None
        a, b = '', ''
        for i in range(length - 2, -1, -1):
            if i % 2 == 0:
                a = a + num[i]
            else:
                b = b + num[i]
        a = int(a)
        a *= 2
        a = str(a) + b
        b = ''
        number_sum = 0
        for ch in a:
             number_sum +=  int(ch)
        b = number_sum
        a = 10 - b % 10 if b != 0 else 0
        return a

    number = str(number)
    if not ( check_sum(number) == int(number[len(number) - 1])):
        raise ValidationError('Контрольныя сумма не совпадает')
