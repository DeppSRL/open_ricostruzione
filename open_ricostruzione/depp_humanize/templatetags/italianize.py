# -*- coding: utf-8 -*-

'''
this template filter transforms cypher numbers in the Italian format for money:
 ex. 91.234.333,22 (for Euro)
'''



from django import template
from open_ricostruzione.utils.moneydate import moneyfmt

register = template.Library()

@register.filter(name='italianize')
def italianize(value):
    return moneyfmt(value,2,"",".",",")