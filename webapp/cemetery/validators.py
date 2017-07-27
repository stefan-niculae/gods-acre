from datetime import date
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _

MIN_YEAR = 1950
MAX_YEAR = 2100

MIN_DATE = date(day=1, month=1, year=MIN_YEAR)
MAX_DATE = date(day=1, month=1, year=MAX_YEAR)


# NrYear
number_validator = MinValueValidator(0)
year_validators  = [
    MinValueValidator(MIN_YEAR, _(f'Must be after {MIN_YEAR}')),
    MaxValueValidator(MAX_YEAR, _(f'Must be before {MAX_YEAR}')),
]


"""
Spot possibilities:
  A-1-2
  A-1a-2
  A-1bis-2
  A2-2-3
numbers are assumed to be up to 4 digits length (ie: 0-9999) 
"""
parcel_validator = RegexValidator(r'^[A-Z]\d{,4}?$',
                                  _('A letter followed by an optional number'))
row_validator    = RegexValidator('^\d{,4}([A-Z]|bis)?$',
                                  _('A number optionally followed by a letter or "bis"'))
column_validator = RegexValidator(r'^\d{,4}$',
                                  _('A number up to 4 digits long'))

# Receipt
payment_value_validator = MinValueValidator(0, _('A payment value cannot be negative'))

# FIXME: for now, (?u)\w is substituted for [a-zA-Z- ] with re.U to handle diacritics
name_validator = RegexValidator(r'^(((?u)\w)|[ -]){2,}$',
                                _('At least two letters, spaces or dashes (-)'))

# eg: 0712345678
romanian_phone_validator = RegexValidator(r'^0?7\d{8}$',
                                          _('Start with 07 or 7, followed by eight digits'))
address_validator = RegexValidator(r'^(((?u)\w)|[ -\.]){2,}$',
                                   _('At least two letters, digits, spaces, periods (.) or dashes (-)'))
city_validator = RegexValidator(r'^(((?u)\w)|[ -]){2,}$',
                                _('At least two letters, spaces or dashes (-)'))

date_validators = [
    MinValueValidator(MIN_DATE, _(f'Must be after {MIN_YEAR}')),
    MaxValueValidator(MAX_DATE, _(f'Must be before {MAX_YEAR}')),
]
