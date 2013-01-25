from django import template
from open_ricostruzione.utils.moneydate import moneyfmt

register = template.Library()

@register.filter(name='italianize')
def italianize(value):
    return moneyfmt(value,2,"",".",",")