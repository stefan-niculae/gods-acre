from django import template
from django.forms.widgets import CheckboxInput

register = template.Library()

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
