from typing import Optional, Tuple, Dict, Callable, Any, List

from copy import deepcopy
from collections import namedtuple
from itertools import zip_longest
from functools import partial
import logging

import numpy as np
import pandas as pd

from django.forms.models import model_to_dict

from .models import Spot, Operation, Deed, OwnershipReceipt, Owner, Construction, Authorization, Company, PaymentUnit, \
    PaymentReceipt, Maintenance
from .utils import reverse_dict, filter_dict, show_dict, map_dict, identity
from .display_helpers import entity_tag, title_case
from .parsing_helpers import year_shorthand_to_full, parse_nr_year, keep_only, parse_date


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
Parsing logic components
"""

def natural_getsert(model) -> Callable:  # takes a django model
    """ getsert = get or insert; natural = using natural key """
    def handler(identifier: Optional[str]):  # returns an entity
        if identifier is None:
            return None

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


def relational_get(model, fields: Dict[str, Any], relational_keys: [str]):
    """ find the entity that has the given `fields` (even for relational fields) """
    try:
        query_fields = {(k + '__in' if k in relational_keys else k): v for k, v in fields.items()}
        entities = model.objects.filter(**query_fields)
    except Exception as e:
        raise ValueError(f'Filter by {{{show_dict(fields)}}}: {e}')

    if len(entities) != 1:  # don't use get as it throws an error on multiple matches, but it is in fact not an error
        return None

    entity = entities[0]
    lengths_equal = all(getattr(entity, f).count() == len(fields[f]) for f in fields)  # __in can return partials
    if not lengths_equal:
        return None

    return entity


def relational_get_or_create(model, fields: Dict[str, Any], relational_keys: [str], defaults=Dict[str, Any]):
    entity = relational_get(model, fields, relational_keys)
    if entity:
        return entity

    # create it now
    entity = model(**filter_dict(fields, relational_keys, inverse=True), **defaults)
    for key in relational_keys:
        entity[key] = fields[key]
    entity.save()
    return entity


def multiple(single_parser: Callable, separator: str=',', at_least_one=False) -> Callable:
    """ makes a parser that works on a single element work on a list of elements, split by a separator """
    def handler(inp: Optional[str]) -> Optional[List]:  # returns an entity
        if inp is None:
            if at_least_one:
                raise ValueError('Expected at least one element for multiple parsing')
            return []
        return [single_parser(elem) for elem in str(inp).split(separator)]
    return handler


def translate(dictionary: Dict[str, str], default=None):
    def handler(string: Optional[str]) -> str:
        try:
            return dictionary[string]
        except KeyError:
            if string is None:  # no value entered
                return default
            raise ValueError(f'Wrong value: {string} is not one of {", ".join(dictionary.keys())}')
    return handler


def get_or_create_and_save(model, **kwargs):
    entity, created_now = model.objects.get_or_create(**kwargs)
    if created_now:
        entity.save()
    return entity


"""
Model-specific functions
"""

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

def prepare_payment_receipt_fields(parsed_fields: Dict[str, Any]) -> Dict[str, Any]:
    """ takes keys: receipt_id, spots, years, values
        returns keys: number, year, units """
    number, year = parsed_fields['receipt_id']

    spots  = parsed_fields['spots']
    years  = parsed_fields['years']
    values = parsed_fields['values']

    if len(spots) != len(years):
        # there can be a single spot mentioned and multiple years
        # eg: a13 | 14,15 | 20,30 ~> a13,a13 | 14,15 | 20,30
        if len(spots) != 1:
            raise ValueError(f'More than one spot ({len(spots)}) entered, but only ({len(years)}) years')
        [spot] = spots
        spots = [spot] * len(years)

    if len(values) != len(years):
        # there can be a single value mentioned but multiple years
        # a13,a13 | 14,15 | 30 ~> a13,a13 | 14,15 | 30,30
        if len(values) != 1:
            raise ValueError(f'More than one value ({len(spots)}) entered, but only ({len(years)}) years')
        [value] = values
        values = [value] * len(years)

    units = [get_or_create_and_save(PaymentUnit, spot=s, year=y, defaults=dict(value=v))
             for s, y, v in zip(spots, years, values)]
    return {
        'number': number,
        'year':   year,
        'units':  units,
    }


"""
Composing parsing bits
"""

ModelMetadata = namedtuple('ModelMetadata',
                           'model sheet_name column_renames field_parsers prepare_fields '
                           'identifying_fields relational_fields')
"""
    model (django.db.models.Model): class of the resulting object
    sheet_name (str): excel sheet name
    column_renames (dict<str: str>): code_field_name: excel_column_name
    field_parsers (dict<str: str -> Any>): type of the field - an entry for a field takes the cell content and 
        produces a value (eg: title-cased name, spot object from its textual representation)
    identifying_fields ([str]): fields that should be present in `get_or_create` args, others instead in defaults kwarg
        eg: name Owner (but not address or phone)
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

construction_type_translations = {
    'cavou':   Construction.TOMB,
    'bordura': Construction.BORDER,
}

MODELS_METADATA = [
    ModelMetadata(
        model=Operation,
        sheet_name='Operatii',
        column_renames={
          'type':     'Tip',
          'deceased': 'Decedat',
          'spot':     'Loc veci',
          'date':     'Data',
          'exhumation_written_report': 'Exhumare PV',
          'remains_brought_from':      'Adus oseminte din',
        },
        field_parsers={
          'type':     translate(operation_type_translations, default=Operation.BURIAL),
          'deceased': title_case,  # clean it because it's identifying and will be used for querying
          'spot':     natural_getsert(Spot),
          'date':     parse_date,  # clean it because it's identifying and will be used for querying
          'exhumation_written_report': identity,
          'remains_brought_from':      identity
        },
        prepare_fields=identity,
        identifying_fields={'type', 'deceased', 'spot', 'date'},
        relational_fields=set(),
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
            'cancel_reason': 'Motiv anulare',
        },
        field_parsers={
            'deed_id':       parse_nr_year,
            'spots':         multiple(natural_getsert(Spot), at_least_one=True),
            'receipt_ids':   multiple(parse_nr_year),
            'values':        multiple(float),
            'owners':        multiple(natural_getsert(Owner)),
            'cancel_reason': translate(deed_cancel_reason_translations),
        },
        prepare_fields=prepare_deed_fields,
        identifying_fields={'number', 'year'},
        relational_fields={'spots', 'owners', 'receipts'},
    ),

    ModelMetadata(
        model=Owner,
        sheet_name='Proprietari',
        column_renames={
            'name':     'Nume',
            'address':  'Adresa',
            'city':     'Localitate',
            'phone':    'Telefon',
        },
        field_parsers={
            'name':     title_case,  # clean it because it's identifying and will be used for querying
            'address':  identity,
            'city':     identity,
            'phone':    partial(keep_only, condition=str.isdigit),
        },
        prepare_fields=identity,
        identifying_fields={'name'},
        relational_fields=set(),
    ),

    ModelMetadata(
        model=Construction,
        sheet_name='Constructii',
        column_renames={
            'type':           'Tip',
            'spots':          'Locuri veci',
            'authorizations': 'Autorizatii',
            'owner_builder':  'Constructor proprietar',
            'company':        'Companie',
        },
        field_parsers={
            'type':           translate(construction_type_translations),
            'spots':          multiple(natural_getsert(Spot), at_least_one=True),
            'authorizations': multiple(natural_getsert(Authorization)),
            'owner_builder':  natural_getsert(Owner),
            'company':        natural_getsert(Company),
        },
        prepare_fields=identity,
        identifying_fields={'type', 'spots'},
        relational_fields={'spots', 'authorizations', 'company', 'owner_builder'},
    ),

    ModelMetadata(
        model=PaymentReceipt,
        sheet_name='Contributii',
        column_renames={
            'receipt_id': 'Chitanta',
            'spots':      'Locuri veci',
            'years':      'Ani',
            'values':     'Sume platite',
        },
        field_parsers={
            'receipt_id': parse_nr_year,
            'spots':      multiple(natural_getsert(Spot), at_least_one=True),
            'years':      multiple(year_shorthand_to_full, at_least_one=True),
            'values':     multiple(float, at_least_one=True),
        },
        prepare_fields=prepare_payment_receipt_fields,
        identifying_fields={'number', 'year'},
        relational_fields={'units'},
    )

]

RowFeedback = namedtuple('RowFeedback', 'status info additional')
"""
    status (str):       fail            | add / duplicate
    info (str):         failure cause   | entity link
    additional (str):   exception       | fields as dict
"""

def entity2dict_str(entity) -> str:
    d = model_to_dict(entity)
    return '{' + show_dict(d) + '}'

def parse_row(row, metadata) -> Tuple[str, str, str]:
    model = metadata.model
    model_name = model.__name__

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
        identif_rel = metadata.identifying_fields & metadata.relational_fields  # identifying and relational
        identif_items = filter_dict(prepared_fields, metadata.identifying_fields)
        identif_non_rel_items = filter_dict(identif_items, metadata.relational_fields, inverse=True)

        if not identif_rel:
            # non identifiable and non relational
            safe_defaults = filter_dict(prepared_fields,
                                        metadata.identifying_fields | metadata.relational_fields, inverse=True)
            entity, created_now  = model.objects.get_or_create(**identif_items, defaults=safe_defaults)

        else:  # model has identifying and relational fields
            identif_rel_items = filter_dict(prepared_fields, identif_rel)
            entity = relational_get(model, identif_rel_items, metadata.relational_fields)
            if not entity:  # there is not an entity that matches exactly the relational fields
                entity = model(**identif_non_rel_items)
                entity.save()
                created_now = True
            else:
                created_now = False

    except Exception as error:
        info = f'Get/create {model_name} with init {{{show_dict(identif_items)}}}'
        return 'fail', info, repr(error)

    if not created_now:  # entity already existed
        for field, value in prepared_fields.items():
            try:
                setattr(entity, field, value)
            except Exception as error:
                info = f'Update on duplicate "{field}": {{value}}'
                return 'fail', info, repr(error)

        try:
            entity.save()
        except Exception as error:
            info = f'Save after updating fields on found-duplicate {entity}'
            return 'fail', info, repr(error)
        return 'duplicate', entity_tag(entity), entity2dict_str(entity)

    # 4. save the entity
    try:
        entity.save()
    except Exception as error:
        info = f'Save {model_name}: {entity}'
        return 'fail', info, repr(error)

    # 5. set relational fields
    for field in metadata.relational_fields:
        try:
            setattr(entity, field, prepared_fields[field])
        except Exception as error:
            info = f'Set relational field {field}: {prepared_fields[field]}'
            return 'fail', info, repr(error)
    try:
        entity.save()
    except Exception as error:
        info = f'Save after setting relational fields on {entity}'
        return 'fail', info, repr(error)

    # finally success
    return 'add', entity_tag(entity), entity2dict_str(entity)


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
