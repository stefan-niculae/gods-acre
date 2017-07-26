from typing import Optional, Union, Tuple, Callable
from dateutil.parser import parse as dateutil_parse
from datetime import datetime


def year_shorthand_to_full(shorthand: Optional[Union[int, str]], threshold: int = 50) -> Optional[int]:
    """

    Args:
        shorthand (int | str): last two digits in a year (eg: 99, 00, 15) 
        threshold (int): after what year it is considered 2000s not 1900s  (eg: for 50: 51 -> 1951 but 49 -> 2049 

    Returns:
        year (int): full year (eg: 1999, 2000, 2015)

    Examples:
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
        >>> year_shorthand_to_full(None)
    """
    if shorthand is None:
        return None

    if type(shorthand) is str:
        shorthand = shorthand.replace("'", '')  # '17 ~> 17

    shorthand = int(shorthand)

    if shorthand >= 100:
        return shorthand  # not actually a shorthand

    if shorthand > threshold:
        return 1900 + shorthand
    else:
        return 2000 + shorthand


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


def parse_date(arg) -> Optional[datetime]:
    """
    Parse the date contained in the string

    Args:
        arg (str | int | None): what to parse 

    Returns:
        datetime: parsed datetime object

    Examples:
        >>> parse_date('1994')
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date("'94")
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date('94')
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date("'17")
        datetime.datetime(2017, 1, 1, 0, 0)

        >>> parse_date('17')  # ambiguous interpreted as year
        datetime.datetime(2017, 1, 1, 0, 0)

        >>> parse_date('24.01.1994')  # infer day first
        datetime.datetime(1994, 1, 24, 0, 0)

        >>> parse_date('01.24.1994')  # infer month first
        datetime.datetime(1994, 1, 24, 0, 0)

        >>> parse_date('05.01.1994')  # ambiguous interpreted as month first
        datetime.datetime(1994, 1, 5, 0, 0)

        >>> parse_date('18 07 2017')  # different separator
        datetime.datetime(2017, 7, 18, 0, 0)

        >>> parse_date(None)

        >>> parse_date(2017)  # ints work as well
        datetime.datetime(2017, 1, 1, 0, 0)

        >>> parse_date(94)  # ints work as well
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date('06')
        datetime.datetime(2006, 1, 1, 0, 0)

        >>> parse_date('6')
        datetime.datetime(2006, 1, 1, 0, 0)

        >>> parse_date('00')
        datetime.datetime(2000, 1, 1, 0, 0)
    """

    if arg is None:
        return None

    str_arg = str(arg)  # convert ints
    try:
        int_arg = int(str_arg.replace("'", ""))  # to be able to convert '17
        int_arg = year_shorthand_to_full(int_arg)  # to correctly assess 17 as the year 2017 instead of day 17
        str_arg = str(int_arg)
    except ValueError:
        pass  # it's ok if it's not an int

    return dateutil_parse(
        str_arg,
        dayfirst=True,  # for ambiguities like `10.10.1994`
        default=datetime(year=2000, month=1, day=1))  # when only the year is given, set to Jan 1st
