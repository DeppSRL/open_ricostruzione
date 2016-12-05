# -*- coding: utf-8 -*-

'''
this template gets the css class name for the icon based on tipo immobile
'''

from django import template

register = template.Library()


@register.filter(name='css_class_name')
def css_class_name(value,):
    if value == 'altro':
        return "altro"
    elif value == 'chiese-e-beni-religiosi':
        return "chiese"
    elif value == 'cimiteri':
        return "cimiteri"
    elif value == 'edifici-pubblici':
        return "pubblici"
    elif value == 'edifici-storici-e-culturali':
        return "storici"
    elif value == 'impianti-sportivi-e-ricreativi':
        return "sportivi"
    elif value == 'infrastrutture-e-bonifiche':
        return "infrastrutture"
    elif value == 'ospedali':
        return "ospedali"
    elif value == 'scuole-e-universita':
        return "scuole"