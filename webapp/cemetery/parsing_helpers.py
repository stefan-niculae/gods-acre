from typing import Optional, Tuple, Callable

from .display_helpers import year_shorthand_to_full


def parse_nr_year(identifier: Optional[str]) -> Optional[Tuple[int, int]]:
    """
    >>> parse_nr_year('1/17')
    1, 2017

    >>> parse_nr_year('10/17')
    10, 2017

    >>> parse_nr_year('10/2017')
    10, 2017

    >>> parse_nr_year('10/94')
    1, 1994

    >>> parse_nr_year('10/1994')
    1, 1994

    >>> parse_nr_year(None)
    """
    if identifier is None:
        return None
    number, year = identifier.split('/')
    return int(number), year_shorthand_to_full(year)


def keep_only(x: Optional[str], condition: Callable[[str], bool]) -> Optional[str]:
    """
    >>> keep_only('0712 345 789', str.isdigit)
    '0712345789'
    """
    if x is None:
        return None
    return ''.join(filter(condition, x))
