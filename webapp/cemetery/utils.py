from typing import Optional
from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


DEFAULT_HEAD_LENGTH = 2


def rev(l: list) -> list:
    """
    List reversed
    :param l: list to be reversed
    :return:  reversed list (as a list object)
    
    >>> rev([1, 2, 3])
    [3, 2, 1]
    """
    return list(reversed(l))


def add_link(model_name: str, popup: bool=True) -> str:
    """
    Link building from https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#reversing-admin-urls
    
    :param model_name: name in snake_case (with underscores) - what to build the link for
    :param popup:      whether the link should open in a popup or new page
    :return:           link to change page
    
    
    >>> add_link('model')
    '/cemetery/model/add?_to_field=id&_popup=1'
    """
    model_name = model_name.replace('_', '').lower()  # delete underscores
    # link = reverse(f'admin:cemetery_{model_name}_add')  # TODO
    link = f'/cemetery/{model_name}/add'

    link += '?_to_field=id'  # HACK: hover over add links for other models and this is what is appended
    if popup:
        link += '&_popup=1'  # HACK: see above

    return link


def change_link(model_name: str, pk) -> str:
    """
    Link building from https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#reversing-admin-urls
    
    :param model_name: name in snake_case (with underscores) - what to build the link for
    :param pk:         primary key of entity to change
    :return:           link to change page 
    """
    model_name = model_name.replace('_', '').lower()  # delete underscores
    link_name = f'admin:cemetery_{model_name}_change'
    return reverse(link_name, args=(pk,))


def display_change_link(entity) -> Optional[str]:
    """
    Creates a link to change the entity. 

    :param entity:         Django Model (or something that has .pk: int) 
    :return:               html tag for anchor
    
    eg:
    MyModel(pk=1) ->
    <a href="/cemetery/mymodel/change/1">My model #1</a>
    """
    if not entity:
        return
    link = change_link(entity.__class__.__name__, entity.pk)
    return mark_safe(f'<a href="{link}">{entity}</a>')


def display_head_tail_summary(entities, head_length: Optional[int]=None) -> (Optional[str], Optional[str]):
    """
    Show the first item. Others are shown as (+x) more
    
    :param entities:    queryset or iterable
    :param head_length: how many entities to be displayed fully
    :return:            tuple of (list of head elements, tail summary string), or (None, None) 
    
    >>> display_head_tail_summary(['abc'])
    (['abc'], '')
    
    >>> display_head_tail_summary(['abc'], head_length=1)
    (['abc'], '')
    
    >>> display_head_tail_summary(['abc'], head_length=10)
    (['abc'], '')
    
    >>> display_head_tail_summary(['abc', 'def', 'xyz'], head_length=1)
    (['abc'], '(+2)')
    
    >>> display_head_tail_summary(['abc', 'def', 'xyz'], head_length=2)
    (['abc', 'def'], '(+1)')
    
    >>> display_head_tail_summary([])
    (None, None)
    """
    if not entities:
        return None, None

    head_length = head_length or DEFAULT_HEAD_LENGTH

    tail_length = len(entities) - head_length
    tail_summary = '' if tail_length <= 0 else f'(+{tail_length})'

    return entities[:head_length], tail_summary


def display_head_links(query, head_length: Optional[int]=None) -> Optional[str]:
    """
    Links the first item and shows the others.
    
    :param query: Django query manager (or something that has .all = () -> list)
    :return:      html tag for anchor
    """
    if not query:
        return

    entities = query.all()
    head, others = display_head_tail_summary(entities, head_length)
    if not head:  # no entities
        return

    links = map(display_change_link, head)
    return ', '.join(links) + ' ' + others


def truncate(string: Optional[str], max_len: int=20) -> Optional[str]:
    """
    Caps the string to `max_len`. Inserts an ellipsis if necessary
    
    :param string:  what to truncate; if None, will return None 
    :param max_len: maximum number of characters (including ellipsis)
    :return:        truncated string
    
    >>> truncate('abc', max_len=4)
    'abc'
    
    >>> truncate('abcdxyz', max_len=4)
    'abc…'
    
    >>> truncate(None)
    """
    if not string:
        return
    max_len -= 1  # to account for the length of the ellipsis
    ellipsis_str = '…' if len(string) > max_len else ''
    return string[:max_len] + ellipsis_str


def title_case(string: Optional[str]) -> Optional[str]:
    """
    :param string: string to convert into Title Case 
    :return:       converted string
    
    >>> title_case('abc  dEf')
    'Abc Def'
    >>> title_case(None)
    None
    """
    if string is None:
        return None
    return ' '.join(word.capitalize() for word in string.split())


def year_shorthand_to_full(shorthand: int, threshold: int=50) -> int:
    """
    :param shorthand: last two digits in a year (eg: 99, 00, 15) 
    :param threshold: after what year it is considered 2000s not 1900s 
                      (eg: for 50: 51 -> 1951 but 49 -> 2049 
    :return:          full year (eg: 1999, 2000, 2015)
    
    >>> year_shorthand_to_full(99)
    1999
    >>> year_shorthand_to_full(0)
    2000
    >>> year_shorthand_to_full(15)
    2015
    >>> year_shorthand_to_full(1994)
    1994
    >>> year_shorthand_to_full(2017)
    2017
    """
    if shorthand >= 100:
        return shorthand  # not actually a shorthand

    if shorthand > threshold:
        return 1900 + shorthand
    else:
        return 2000 + shorthand

def display_date(date):
    """
    >>> display_date(datetime(year=2017, month=7, day=18))
    datetime.datetime(2017, 7, 18, 0, 0)

    >>> display_date(datetime(year=2017, month=1, day=1))
    2017
    """
    if date.month == date.day == 1:
        return date.year
    return date


if __name__ == '__main__':
    import doctest
    doctest.testmod()
