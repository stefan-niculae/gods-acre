from typing import Optional, Tuple, Dict, Callable, Any, List
from copy import deepcopy
import logging
from collections import namedtuple
from itertools import zip_longest

import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime

from .models import Spot, Operation, Deed, OwnershipReceipt, Owner
from .utils import title_case, year_shorthand_to_full, reverse_dict, filter_dict, show_dict, map_dict, parse_nr_year


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def natural_getsert(model) -> Callable:  # takes a django model
    """ getsert = get or insert; natural = using natural key """
    def handler(identifier: str):  # returns an entity
        # prepare the natural key into a dict that can be passed to __init__
        natural_key = model.objects.prepare_natural_key(identifier)

        try:
            # retrieve by natural key
            entity = model.objects.get_by_natural_key(**natural_key)
        except model.DoesNotExist:
            # create if it doesn't exist
            entity = model(**natural_key)
            entity.save()
        return entity

    return handler

def multiple(single_parser: Callable, separator: str=',', required=False) -> Callable:
    """ makes a parser that works on a single element work on a list of elements, split by a separator """
    def handler(inp: Optional[str]) -> Optional[List]:  # returns an entity
        if inp is None:
            if required:
                raise ValueError('Expected at least one element for multiple parsing')
            return []
        return [single_parser(elem) for elem in str(inp).split(separator)]
    return handler

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

def translate(dictionary: Dict[str, str], default=None):
    def handler(string: Optional[str]) -> str:
        try:
            return dictionary[string]
        except KeyError:
            if string is None:  # no value entered
                return default
            raise ValueError(f'Wrong value: {string} is not one of {", ".join(dictionary.keys())}')
    return handler

def as_is(x):
    """ identity function """
    return x

def prepare_deed_fields(parsed_fields: Dict[str, Any]) -> Dict[str, Any]:
        """ takes keys: deed_id, spots, receipts_ids, values, owners, cancel_reason 
            returns keys: number, year, cancel_reason, spots, owners, receipts """
        number, year = parsed_fields['deed_id']

        receipt_ids = parsed_fields['receipt_ids']
        values      = parsed_fields['values']
        if len(values) > len(receipt_ids):  # make sure there no more than one value per receipt id
            raise ValueError(f'More values ({len(values)} than receipts ({len(receipt_ids)})')
        receipts = [OwnershipReceipt.objects.get_or_create(
                        number=nr, year=yr, defaults={'value': val})[0]  # returns entity, created_now
                    for (nr, yr), val in zip_longest(receipt_ids, values)]  # missing values will be None

        return {
            'number':        number,
            'year':          year,
            'cancel_reason': parsed_fields['cancel_reason'],
            'spots':         parsed_fields['spots'],
            'owners':        parsed_fields['owners'],
            'receipts':      receipts,
        }

ModelMetadata = namedtuple('ModelMetadata',
                           'model sheet_name column_renames field_parsers prepare_fields relational_fields')
"""
    model (django.db.models.Model): class of the resulting object
    sheet_name (str): excel sheet name
    column_renames (dict<str: str>): code_field_name: excel_column_name
    field_parsers (dict<str: str -> Any>): type of the field - an entry for a field takes the cell content and 
        produces a value (eg: title-cased name, spot object from its textual representation)
    prepare_fields (dict<str: Any> -> dict<str: Any>): change the fields values/keys to fit the model's __init__ -
        takes dict of {input_field: parsed_value} and transforms it into {model_field: value} (eg: combine values and
        receipt_identifiers into receipts or split deed_identifier into number and year) 
    relational_fields ([str]): fields that need to be assigned after a the object received its pk (eg: owners for deed)
"""

operation_type_translations = {
    'inhumare':     Operation.BURIAL,
    'dezhumare':    Operation.EXHUMATION,
}

deed_cancel_reason_translations = {
    'proprietar decedat': Deed.OWNER_DEAD,
    'donat':              Deed.DONATED,
    'pierdut':            Deed.LOST,
}

MODELS_METADATA = [
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
          'type': translate(operation_type_translations, default=Operation.BURIAL),
          'note': as_is,
          'spot': natural_getsert(Spot),
          'name': title_case,
          'date': parse_date
        },
        prepare_fields=as_is,
        relational_fields=[],
    ),

    ModelMetadata(
        model=Deed,
        sheet_name='Acte concesiune',
        column_renames={
            'deed_id':       'Act',
            'spots':         'Locuri veci',
            'receipt_ids':   'Chitante',
            'values':        'Valori',
            'owners':        'Proprietari',
            'cancel_reason': 'Motiv anulare'
        },
        field_parsers={
            'deed_id':       parse_nr_year,
            'spots':         multiple(natural_getsert(Spot), required=True),
            'receipt_ids':   multiple(parse_nr_year),
            'values':        multiple(float),
            'owners':        multiple(natural_getsert(Owner)),
            'cancel_reason': translate(deed_cancel_reason_translations)
        },
        prepare_fields=prepare_deed_fields,
        relational_fields=['spots', 'owners', 'receipts'],
    ),

]

RowFeedback = namedtuple('RowFeedback', 'status info additional')
"""
    status (str):       fail            | add           | duplicate
    info (str):         failure cause   | model name    | model name
    additional (str):   exception       | model repr    | model repr
"""

def parse_row(row, metadata) -> Tuple[str, str, str]:
    model_name = metadata.model.__name__

    # 1. parse fields
    parsed_fields = {}
    for field, parser in metadata.field_parsers.items():
        try:
            parsed_fields[field] = parser(row[field])
        except Exception as error:
            info = f'Parse column "{field}": {row[field]}'
            return 'fail', info, repr(error)  # repr instead of str to get the exception type as well

    # 2. prepare the parsed fields
    try:
        prepared_fields = metadata.prepare_fields(parsed_fields)
    except Exception as error:
        info = f'Prepare the parsed fields {{{show_dict(parsed_fields)}}}'
        return 'fail', info, repr(error)

    # 3. use the prepared fields to build the model
    try:
        # create the entity (if it doesn't already exist)
        fields_for_init = filter_dict(prepared_fields, metadata.relational_fields, inverse=True)
        entity, created_now = metadata.model.objects.get_or_create(**fields_for_init)
    except Exception as error:
        info = f'Get/create {model_name} with init {{{show_dict(fields_for_init)}}}'
        return 'fail', info, repr(error)

    if not created_now:  # entity already existed
        return 'duplicate', model_name, entity

    # 4. save the entity
    try:
        entity.save()
    except Exception as error:
        info = f'Save {metadata.model.__name}: {entity}'  # TODO check if this provides enough info
        return 'fail', info, repr(error)

    # 5. set relational fields
    for field in metadata.relational_fields:
        try:
            setattr(entity, field, prepared_fields[field])
        except Exception as error:
            info = f'Add post save field {field}: {prepared_fields[field]}'
            return 'fail', info, repr(error)

    # finally success
    return 'add', model_name, entity


def parse_sheet(file, metadata) -> [RowFeedback]:
    sheet = pd.read_excel(file, sheetname=metadata.sheet_name)
    sheet = sheet.rename(columns=reverse_dict(metadata.column_renames))  # translate
    sheet = sheet.replace({np.nan: None})  # mostly not numerical data: None is easier to work with

    return [RowFeedback(*parse_row(row, metadata)) for _, row in sheet.iterrows()]

def status_counts(feedbacks: [RowFeedback]) -> Dict[str, int]:
    statuses = [f.status for f in feedbacks]
    return {status: statuses.count(status) for status in ['fail', 'duplicate', 'add']}

def parse_file(file):
    # send a copy of the file because the document gets consumed after reading a sheet
    feedbacks = {metadata.sheet_name: parse_sheet(deepcopy(file), metadata) for metadata in MODELS_METADATA}
    return feedbacks, map_dict(feedbacks, status_counts)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
