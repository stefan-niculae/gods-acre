from django import template

register = template.Library()


# todo make fisa individuala active even on /loc/10, not just on /loc
@register.simple_tag
def active_page(request, view_name):
    from django.core.urlresolvers import resolve, Resolver404
    if not request:
        return ""
    try:
        return "active" if resolve(request.path_info).url_name == view_name else ""
    except Resolver404:
        return ""


@register.filter(name='zip')
def zip_lists(a, b):
    """
    the lists a and b can be now traversed simultaneously
    """
    return zip(a, b)

@register.filter
def contains(word, letter):
    return letter in str(word)