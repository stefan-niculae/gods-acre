from typing import Optional, Tuple, Union
import logging
from collections import namedtuple
from itertools import zip_longest
from enum import Enum

import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
from django.db.utils import IntegrityError

from .models import Spot, Operation, Deed, OwnershipReceipt, Owner
from .utils import title_case, year_shorthand_to_full, reverse_dict, filter_dict, show_dict


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_nr_year(identifier: str) -> Tuple[int, int]:
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
    """
    number, year = identifier.split('/')
    return int(number), year_shorthand_to_full(year)


def get_or_create_spot(identifier: str):
    identifier = identifier.strip().upper()
    parcel, row, column = identifier.split('-')

    try:
        # retrieve by natural key
        return Spot.objects.get_by_natural_key(parcel, row, column)
    except Spot.DoesNotExist:
        # create if it doesn't exist
        spot = Spot(parcel=parcel, row=row, column=column)
        spot.save()
        return spot

def get_or_create_ownership_receipt(identifier: str, value: Union[str, float]):
    number, year = parse_nr_year(identifier)

    try:
        return OwnershipReceipt.objects.get_by_natural_key(number, year)
    except OwnershipReceipt.DoesNotExist:
        receipt = OwnershipReceipt(number=number, year=year, value=value)
        receipt.save()
        return receipt


def get_or_create_owner(name: str):
    # TODO: dry get_or_create_by_natural_key?
    name = title_case(name)
    try:
        return Owner.objects.get_by_natural_key(name=name)
    except Owner.DoesNotExist:
        owner = Owner(name=name)
        owner.save()
        return owner


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
        int_arg = int(str_arg.replace("'", ""))    # to be able to convert '17
        int_arg = year_shorthand_to_full(int_arg)  # to correctly assess 17 as the year 2017 instead of day 17
        str_arg = str(int_arg)
    except ValueError:
        pass  # it's ok if it's not an int

    return parse(str_arg,
                 dayfirst=True,  # for ambiguities like `10.10.1994`
                 default=datetime(year=2000, month=1, day=1))   # when only the year is given, set to Jan 1st


class ParsingStatus(Enum):
    ADDED   = 1
    EXISTED = 2
    FAILED  = 3


def parse_operation_type(inp: Optional[str]):
    translations = {
        'inhumare': Operation.BURIAL,
        'exhumare': Operation.EXHUMATION,
    }
    return translations.get(inp, Operation.BURIAL)

def as_is(x):
    """ identity function """
    return x


def parse_operation(df: pd.DataFrame):
    n_successful = 0

    for index, row in df.iterrows():

        # TODO DRY message system, show to user the rows that couldn't be converted on import page

        # create the entity (if it doesn't already exist)
        try:
            operation, created_now = Operation.objects.get_or_create(
                type=type_, name=name, spot=spot, date=date, note=note)

            if created_now:
                operation.save()
                logger.info(f'Successfully saved operation <{operation}>.')
            else:
                logger.debug(f'Operation already existed <{operation}>.')
            n_successful += 1
        except IntegrityError:
            logger.warning(f'Failed to save operation. Skipping: \n{row}', exc_info=True)
            continue

    return n_successful


def parse_deed(df: pd.DataFrame):
    n_successful = 0

    df.cancel_reason.rename({
        'donat':              Deed.DONATED,
        'proprietar decedat': Deed.OWNER_DEAD,
        'pierdut':            Deed.LOST,
    }, inplace=True)

    for index, row in df.iterrows():
        cancel_reason = row.cancel_reason

        try:
            number, year = parse_nr_year(row.deed)
        except (AttributeError, TypeError):
            logger.warning(f'{index} couldnt parse nr/yr {row.deed}')
            continue
        spots = map(get_or_create_spot, row.spots.split(','))

        # TODO surround with try/catch
        if row.receipts is None:
            receipt_identifiers = []
        else:
            try:
                receipt_identifiers = row.receipts.split(',')
            except AttributeError:
                logger.warning(f'{index} couldnt parse receipt identifiers {row.receipts}')
                continue

        if row.values_ is None:
            values = []
        else:
            values = str(row.values_).split(',')

        if len(receipt_identifiers) > 0 or len(values) > 0:
            receipt_tuples = zip_longest(receipt_identifiers, values)
        else:
            receipt_tuples = []
        receipts = map(get_or_create_ownership_receipt, list(receipt_tuples))

        # TODO surround with try/catch
        if row.owners is None:
            owners = []
        else:
            owners = map(get_or_create_owner, row.owners.split(','))

        # TODO DRY
        try:
            # print(number, year, list(spots), cancel_reason, list(receipts), list(owners), sep='\n'+'>'*5)
            deed, created_now = Deed.objects.get_or_create(
                number=number, year=year, cancel_reason=cancel_reason)

            if created_now:
                deed.spots = spots
                deed.receipts = receipts
                deed.owners = owners
                deed.save()
                logger.info(f'Successfully saved deed <{deed}>.')

                n_successful += 1
            else:
                logger.info(f'Deed already existed <{deed}>.')
        except:
            logger.warning(f'{index} Failed to save deed. Skipping: \n{row}', exc_info=True)
            continue

    return n_successful


ModelMetadata = namedtuple('ModelMetadata', 'sheet_name column_renames field_parsers prepare_fields post_save_fields')
"""
    model: django.db.models.Model (class of the resulting object)
    sheet_name: str (excel sheet name)
    column_renames: dict<str: str> (code_field_name: excel_column_name)
    field_parsers:  dict<str: str -> Any> (the type of the field)
    prepare_fields: dict<str: Any> -> dict<str: Any> (how to change the fields values/keys to fit the model's __init__)
    post_save_fields: [str] (fields that need to be assigned after a the object received its pk)
"""

#
MODELS_METADATA = [
    # spot
    # # deed
    # ModelMetadata(sheet_name='Acte concesiune',
    #               column_renames={
    #                   'Act': 'deed',
    #                   'Locuri Veci': 'spots',
    #                   'Chitante': 'receipts',
    #                   'Valori': 'values_',
    #                   'Proprietari': 'owners',
    #                   'Motiv anulare': 'cancel_reason'
    #               },
    #               parse_function=parse_deed)
    # owner
    # construction

    # operation
    ModelMetadata(
        model=Operation,
        sheet_name='Operatii',
        column_renames={
          'type': 'Tip',
          'name': 'Nume',
          'spot': 'Loc veci',
          'date': 'Data',
          'note': 'Nota',
        },
        field_parsers={
          'type': parse_operation_type,
          'note': as_is,
          'spot': get_or_create_spot,
          'name': title_case,
          'date': parse_date
        },
        prepare_fields=as_is,
        post_save_fields=[],
    )

    # payment
    # maintenance
]


def parse_file(file):

    for metadata in MODELS_METADATA:
        sheet = pd.read_excel(file, sheetname=metadata.sheet_name)
        sheet = sheet.rename(columns=reverse_dict(metadata.column_renames))  # translate
        sheet = sheet.replace({np.nan: None})  # mostly not numerical data: None is easier to work with

        for index, row in sheet.iterrows():
            print(f'Parsing sheet {metadata.sheet_name}')

            # 1. parse fields
            parsed_fields = {}
            for field, parser in metadata.field_parsers.items():
                try:
                    parsed_fields[field] = parser(row[field])
                except Exception as e:
                    # TODO dry exception
                    # TODO sent to front-end
                    print(f'[Row {index + 2}] failed to parse column "{metadata.column_renames(field)}" ({field}). '
                          f'Error was {type(e).__name__}: {str(e)}. '
                          f'Skipping row'
                          )
                    continue  # TODO continue outer loop

            # 2. prepare the parsed fields
            try:
                prepared_fields = metadata.prepare_fields(parsed_fields)
            except Exception as e:
                print(f'[Row {index + 2}] failed to prepare the parsed fields {show_dict(parsed_fields)}. ' 
                      f'Error was {type(e).__name__}: {str(e)}. '
                      f'Skipping row'
                      )
                continue

            # 3. use the prepared fields to build the model
            try:
                # create the entity (if it doesn't already exist)
                fields_for_init = filter_dict(prepared_fields, metadata.post_save_fields, inverse=True)
                entity, created_now = metadata.model.objects.get_or_create(**fields_for_init)
            except Exception as e:
                print(f'[Row {index + 2}] failed to get/create {metadata.model.__name__} with init {show_dict(fields_for_init)}. '
                      f'Error was {type(e).__name__}: {str(e)}. '
                      f'Skipping row'
                      )
                continue

            if created_now:
                try:
                    entity.save()
                except Exception as e:
                    print(
                        f'[Row {index + 2}] failed to save {entity}. '  # TODO check if this provides enough info
                        f'Error was {type(e).__name__}: {str(e)}. '
                        f'Skipping row'
                        )

                for field in metadata.post_save_fields:
                    try:
                        setattr(entity, field, prepared_fields[field])
                    except Exception as e:
                        print(
                            f'[Row {index + 2}] failed add field {field} ({prepared_fields[field]}) post save'
                            f'Error was {type(e).__name__}: {str(e)}. '
                            f'Skipping row'
                            )
                        continue

                print(f'[Row {index + 2}] successfully added: {entity}')
            else:
                print(f'[Row {index + 2}] {metadata.model.__name__} already existed: {entity}')

        print(f'Done parsing sheet {metadata.sheet_name}')

    return -1, -1


if __name__ == '__main__':
    import doctest
    doctest.testmod()
