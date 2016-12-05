# -*- coding: utf-8 -*-

'''
this template filter transforms cypher numbers in the Italian format for money:
 ex. 91.234.333,22 (for Euro)
'''

from decimal import *
from django import template

from open_ricostruzione.utils.moneydate import moneyfmt

register = template.Library()


@register.filter(name='italianize')
def italianize(value, arg=2):
    if value is None or value == '':
        return
    decimal_value = Decimal(format(value, ".15g"))
    if arg == 0:
        return moneyfmt(decimal_value, arg, "", ".", "")
    else:
        return moneyfmt(decimal_value, arg, "", ".", ",")
