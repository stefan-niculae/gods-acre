import logging
from math import isnan
from collections import namedtuple

import pandas as pd
from dateutil.parser import parse
from datetime import datetime
from django.db.utils import IntegrityError

from .models import Spot, Operation
from .utils import title_case, year_shorthand_to_full

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_or_create_spot(identifier: str):
    parcel, row, column = identifier.upper().split('-')

    try:
        # retrieve by natural key
        return Spot.objects.get_by_natural_key(parcel, row, column)
    except Spot.DoesNotExist:
        # create if it doesn't exist
        spot = Spot(parcel=parcel, row=row, column=column)
        spot.save()
        return spot


def coalesce_nan(x):
    if type(x) == float and isnan(x):
        return None
    return x


def parse_date(arg):
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
        int_arg = int(str_arg.replace("'", ""))    # to be able to convert '17
        int_arg = year_shorthand_to_full(int_arg)  # to correctly assess 17 as the year 2017 instead of day 17
        str_arg = str(int_arg)
    except ValueError:
        pass  # it's ok if it's not an int

    return parse(str_arg,
                 dayfirst=True,  # for ambiguities like `10.10.1994`
                 default=datetime(year=2000, month=1, day=1))   # when only the year is given, set to Jan 1st


def _parse_operation(df: pd.DataFrame):
    n_failed = 0

    type_translation = {
        'inhumare': Operation.BURIAL,
        'exhumare': Operation.EXHUMATION,
    }

    for index, row in df.iterrows():
        # pre-process fields
        type_ = type_translation.get(row.type, Operation.BURIAL)
        spot  = _get_or_create_spot(row.spot)

        # TODO DRY message system, show to user the rows that couldn't be converted on import page
        try:
            name  = title_case(coalesce_nan(row.name_))
        except TypeError:
            logger.warning(f'Failed to parse name. Skipping: \n{row}', exc_info=True)
            n_failed += 1
            continue

        try:
            date = parse_date(coalesce_nan(row.date))
        except (ValueError, TypeError, NotImplementedError):
            logger.warning(f'Failed to parse date. Skipping: \n{row}', exc_info=True)
            n_failed += 1
            continue

        note  = coalesce_nan(row.note)

        try:
            operation, created_now = Operation.objects.get_or_create(
                type=type_, name=name, spot=spot, date=date, note=note)

            if created_now:
                operation.save()
                logger.info(f'Successfully saved as operation <{operation}>.')
            else:
                logger.debug(f'Operation already existed <{operation}>.')
        except IntegrityError:
            logger.warning(f'Failed to save operation. Skipping: \n{row}', exc_info=True)
            n_failed += 1
            continue

    n_successful = len(df) - n_failed
    return n_successful, n_failed


ModelMetadata = namedtuple('ModelMetadata', 'sheet_name column_renames parse_function')
MODELS_METADATA = [
    # spot
    # deed
    # owner
    # construction

    # operation
    ModelMetadata(sheet_name='Operatii',
                  column_renames={
                      'Tip': 'type',
                      'Nume': 'name_',
                      'Loc veci': 'spot',
                      'Data': 'date',
                      'Nota': 'note',
                  },
                  parse_function=_parse_operation)

    # payment
    # maintenance
]


def parse_file(file):
    total_successful = total_failed = 0

    for sheet_name, column_renames, parse_function in MODELS_METADATA:
        df = pd.read_excel(file, sheetname=sheet_name).rename(columns=column_renames)
        n_successful, n_failed = parse_function(df)

        logger.info(f'Done parsing sheet {sheet_name}: {n_successful} successful and {n_failed} failed rows')
        total_successful += n_successful
        total_failed += n_failed

    return total_successful, total_failed


if __name__ == '__main__':
    import doctest
    doctest.testmod()
