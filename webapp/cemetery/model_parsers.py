from math import isnan

import pandas as pd
from fuzzyparsers import parse_date
from django.db.utils import IntegrityError

from .models import Spot, Deed, Owner, Construction, Payment, Operation, Maintenance
from .utils import title_case


def _parse_spot(row):
    # TODO
    pass


def _parse_deed(row):
    # TODO
    pass


def _parse_owner(row):
    # TODO
    pass


def _parse_construction(row):
    # TODO
    pass


def _get_or_create_spot(identifier: str):
    parcel, row, column = identifier.split('-')

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

        # TODO DRY message system + logger
        try:
            name  = title_case(coalesce_nan(row.name_))
        except TypeError as err:
            print(f'Failed to parse name of row #{index} (message: {err}). Skipping row.')
            n_failed += 1
            continue

        try:
            # TODO make sure it parses dates consisting of year only
            date  = parse_date(coalesce_nan(row.date))
        except (ValueError, TypeError, NotImplementedError) as err:
            print(f'Failed to parse date of row #{index} (message: {err}). Skipping row.')
            n_failed += 1
            continue

        note  = coalesce_nan(row.note)


        # TODO check if it already exists
        try:
            Operation(type=type_, name=name, spot=spot, date=date, note=note).save()
        except IntegrityError as err:
            print(f'Failed to save row #{index} (message: {err}). Skipping row.')
            n_failed += 1
            continue


    n_successful = len(df) - n_failed
    return n_successful, n_failed


def _parse_payment(row):
    # TODO
    pass


def _parse_maintenance(row):
    # TODO
    pass


# TODO namedtuple goodness
# triplet of sheet name, renamed columns and parsing function
MODELS_METADATA = [
    # # spot
    # {},  # TODO
    #
    # # deed
    # {},  # TODO
    #
    # # owner
    # {},  # TODO
    #
    # # construction
    # {},  # TODO

    # operation
    ('Operatii', {
        'Tip': 'type',
        'Nume': 'name_',
        'Loc veci': 'spot',
        'Data': 'date',
        'Nota': 'note',
    }, _parse_operation)

    # # payment
    # {},  # TODO
    #
    # # maintenance
    # {},  # TODO
]


def parse_file(file):
    total_successful = total_failed = 0

    for sheet_name, renamed_columns, parsing_function in MODELS_METADATA:
        df = pd.read_excel(file, sheetname=sheet_name).rename(columns=renamed_columns)
        n_successful, n_failed = parsing_function(df)

        print(f'Done parsing sheet {sheet_name}: {n_successful} successful and {n_failed} failed rows')
        total_successful += n_successful
        total_failed += total_failed

    return total_successful, total_failed
