from typing import Optional, Dict
from datetime import date
from math import fabs

from django.utils.translation import ugettext_lazy as _
from django.db.models import Model, ForeignKey, TextField, IntegerField, CharField, \
    ManyToManyField, FloatField, BooleanField, DateField, Sum, Max, Manager
from django.db.models.signals import pre_save

from .display_helpers import head_plus_more, initials, year_to_shorthand, title_case, entity_tag, show_head_links, NBSP
from .parsing_helpers import parse_nr_year, keep_only, year_shorthand_to_full, parse_date
from .validators import number_validator, year_validators, parcel_validator, row_validator, column_validator, \
    payment_value_validator, name_validator, romanian_phone_validator, address_validator, city_validator, date_validators
from .utils import class_name


DISTANT_DATE_THRESHOLD = 10  # year(s)


# translations
ON_TRANS  = _('on')
FOR_TRANS = _('for')
IN_TRANS  = _('in')

optional = {'blank': True, 'null': True}  # to be passed in field definitions as additional kwargs


# make .save() automatically call .full_clean()
def validate_model(sender, **kwargs):
    """ https://djangosnippets.org/snippets/2319/ """
    if 'raw' in kwargs and not kwargs['raw']:
        kwargs['instance'].full_clean()
pre_save.connect(validate_model, dispatch_uid='validate_models')


"""
Abstract models
"""

class Annotatable(Model):
    note = TextField(**optional)

    class Meta:
        abstract = True

class WarningModel(Model):
    """ model that can self-diagnose warnings """
    def diagnose_warnings(self, only_related_to=None):
        """ should be called after the model is saved. 
            yields tuples of message (str), emitting entity (django.db.Model).
            watch out for circular warnings! """
        yield from []  # ie: nothing

    class Meta:
        abstract = True


class ModelWithYear(WarningModel):
    year   = IntegerField(default=date.today().year, validators=year_validators, verbose_name=_('year'))

    class Meta:
        abstract = True
    
    def clean_fields(self, exclude=None):
        self.year = year_shorthand_to_full(self.year)
        super(ModelWithYear, self).clean_fields(exclude)

    def diagnose_warnings(self, only_related_to=None):
        years = self.year - date.today().year
        distance = int(fabs(years))
        if distance > DISTANT_DATE_THRESHOLD:
            yield _(f'the year {self.year} is {distance} years from today'), self


class NrYearManager(Manager):
    @staticmethod
    def prepare_natural_key(identifier: str) -> Dict[str, int]:
        """ should be called before `get_by_natural_key` or `__init__` """
        number, year = parse_nr_year(identifier)
        return {'number': number, 'year': year}

    def get_by_natural_key(self, number, year):
        return self.get(number=number, year=year)

class NrYear(ModelWithYear):
    """
    For deeds, receipts and authorizations
    """
    number = IntegerField(validators=[number_validator], verbose_name=_('number'))

    objects = NrYearManager()

    class Meta:
        abstract = True
        unique_together = ('number', 'year')
        ordering = ['number', 'year']

    def natural_key(self):
        return self.number, self.year

    def __str__(self):
        return f'{self.number}/{year_to_shorthand(self.year, leading_apostrophe=False)}'


"""
Spot - the central entity
"""

class SpotManager(Manager):
    @staticmethod
    def prepare_natural_key(identifier: str) -> Dict[str, str]:
        """ should be called before `get_by_natural_key` or `__init__` """
        parcel, row, column = identifier.strip().upper().split('-')
        return {'parcel': parcel, 'row': row, 'column': column}

    def get_by_natural_key(self, parcel, row, column):
        return self.get(parcel=parcel, row=row, column=column)

class Spot(WarningModel):
    parcel  = CharField(max_length=5, validators=[parcel_validator], verbose_name=_('parcel'))
    row     = CharField(max_length=7, validators=[row_validator],    verbose_name=_('row'))
    column  = CharField(max_length=4, validators=[column_validator], verbose_name=_('column'))

    objects = SpotManager()

    class Meta:
        unique_together = ('parcel', 'row', 'column')  # they uniquely identify the spot
        ordering = ['parcel', 'row', 'column']
        verbose_name = _('Spot')
        verbose_name_plural = _('Spots')

    def natural_key(self):
        return self.parcel, self.row, self.column

    def __str__(self):
        return f'{self.parcel}-{self.row}-{self.column}'  # non-breaking space

    @property
    def active_deeds(self):
        """
        A deed is active if its cancel_reason is null
        each spot should have no more and no less than ONE active deed at a time
        it should, but it can have multiple -- which should be corrected by the administrator
        """
        return self.deeds.filter(cancel_reason__isnull=True)

    @property
    def active_owners(self):
        # The owner-spot relation goes through a deed
        # there is supposed to be only one active deed per spot
        deed = self.active_deeds.first()
        if not deed:
            return
        return deed.owners

    @property
    def shares_deed_with(self):
        """
        Other spots this shares the deed with 
        """
        deed = self.active_deeds.first()
        if not deed:
            return
        return deed.spots.exclude(id=self.id)

    @property
    def shares_authorization_with(self):
        """
        Other spots that are on the same authorizations as this one
        """
        return Spot.objects.filter(authorizations__in=self.authorizations.all())\
            .distinct().exclude(id=self.id)

    @property
    def unkept_since(self) -> Optional[str]:
        """
        Smallest unkept year which is preceded by a kept year.
        
        
        eg: 
            2013 - unkept
            2014 - kept
            2015 - kept
            2016 - unkept
            2017 - unkept
        -> 2016
                
            2015 - unkept
            2016 - kept
            2017 - kept
        -> None

            2015 - unkept
            2016 - kept
            2017 - unkept
        -> 2017


            2016 - unkept
            2017 - unkept
        -> 2016
        
            2016 - kept
            2017 - kept
        -> None
        
            2017 - kept
        -> None
        
            2017 - unkept
        -> 2017
        """

        maintenances = self.maintenances.order_by('-year')  # from largest year to smallest
        if not maintenances:
            return

        smallest_unkept_year = None
        for maintenance in maintenances:
            if maintenance.kept:  # stop going any further back if we found a year kept
                break
            smallest_unkept_year = maintenance.year  # otherwise, keep going and remembering this as the smallest unkept

        if not smallest_unkept_year:
            return

        years_difference = date.today().year - smallest_unkept_year

        return f'{smallest_unkept_year} ({years_difference} year{"s" if years_difference > 1 else ""})'

    @property
    def last_operation(self):  # -> Optional[Operation]: no forward declaration so this can't be hinted conveniently
        return self.operations.order_by('date').first()

    @property
    def last_paid_year(self) -> int:
        aggregation = self.payments.aggregate(Max('year'))
        return aggregation['year__max']
    _last_paid_year = last_paid_year

    def clean_fields(self, exclude=None):
        self.parcel = self.parcel.upper()
        self.row = self.row.upper()
        if 'BIS' in self.row:
            self.row = self.row.lower()
        # called last because the regex patterns expect uppercase numbers
        # but lowercase may be entered before calling .upper()
        super(Spot, self).clean_fields(exclude)

    def diagnose_warnings(self, only_related_to=None):
        if not only_related_to or class_name(only_related_to) == 'Deed':
            if self.active_deeds.count() > 1:
                deeds_links = show_head_links(self.active_deeds, head_length='all')
                yield _(f'more than one active deed: {deeds_links}'), self

        if not only_related_to or class_name(only_related_to) == 'Construction':
            constructions = self.constructions.all()
            constructions_links = show_head_links(constructions, head_length='all')
            if len(constructions) > 2:
                yield _(f'more than two constructions: {constructions_links}'), self
            if len(constructions) == 2 and constructions[0].type == constructions[1].type:
                yield _(f'two  constructions of the same type: {constructions_links}'), self


"""
Ownership
"""

class Deed(NrYear):
    spots = ManyToManyField(Spot, related_name='deeds', verbose_name=_('spots'))
    # note: a spot can have multiple deeds in the same year so we can't enforce unique(spot, year)

    OWNER_DEAD = 'o'
    DONATED    = 'd'
    LOST       = 'l'
    CANCEL_REASON_CHOICES = [
        (OWNER_DEAD, _('owner dead')),
        (DONATED,    _('donated')),
        (LOST,       _('lost'))
    ]
    cancel_reason = CharField(max_length=1, choices=CANCEL_REASON_CHOICES, **optional, verbose_name=_('cancel reason'))

    class Meta:
        verbose_name = _('Deed')
        verbose_name_plural = _('Deeds')

    @property
    def is_active(self) -> bool:
        return self.cancel_reason is None

    def diagnose_warnings(self, only_related_to=None):
        if only_related_to is None:
            for spot in self.spots.all():
                yield from spot.diagnose_warnings(only_related_to=self)


class OwnershipReceipt(NrYear):
    deed  = ForeignKey(Deed, related_name='receipts', **optional, verbose_name=_('deed'))
    value = FloatField(**optional, validators=[payment_value_validator], verbose_name=_('value'))

    class Meta:
        verbose_name = _('Ownership Receipt')
        verbose_name_plural = _('Ownership Receipts')

    @property
    def spots(self):
        # The receipt-spot relation goes through a deed
        if not self.deed:
            return None
        return self.deed.spots

    @property
    def owners(self):
        # The receipt-owner relation goes through a deed
        if not self.deed:
            return None
        return self.deed.owners


class OwnerManager(Manager):
    @staticmethod
    def prepare_natural_key(identifier: str) -> Dict[str, str]:
        return {'name': title_case(identifier)}

    def get_by_natural_key(self, name):
        return self.get(name=name)

class Owner(WarningModel):
    name    = CharField(max_length=100, unique=True, validators=[name_validator],           verbose_name=_('name'))
    phone   = CharField(max_length=15,  **optional,  validators=[romanian_phone_validator], verbose_name=_('phone'))
    address = CharField(max_length=250, **optional,  validators=[address_validator],        verbose_name=_('address'))
    city    = CharField(max_length=50,  **optional,  validators=[city_validator],           verbose_name=_('city'))
    deeds   = ManyToManyField(Deed, related_name='owners', blank=True, verbose_name=_('deeds'))

    objects = OwnerManager()

    class Meta:
        ordering = ['name']
        verbose_name = _('Owner')
        verbose_name_plural = _('Owners')

    def natural_key(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def spots(self):
        # The owner-spot relation goes through a deed
        return Spot.objects.filter(deeds__owners=self)

    @property
    def receipts(self):
        # The spot-receipt relation goes through a deed
        return OwnershipReceipt.objects.filter(deed__owners=self)

    def clean_fields(self, exclude=None):
        self.name    = title_case(self.name)
        self.address = title_case(self.address)
        self.city    = title_case(self.city)
        self.phone = keep_only(self.phone, str.isdigit)
        super(Owner, self).clean_fields(exclude)


"""
Operations
"""

class Operation(WarningModel):
    BURIAL     = 'b'
    EXHUMATION = 'e'
    TYPE_CHOICES = [
        (BURIAL,     _('burial')),
        (EXHUMATION, _('exhumation'))
    ]
    TYPE_SYMBOLS = {
        BURIAL:     '↓',
        EXHUMATION: '↑',
    }
    type = CharField(max_length=1, choices=TYPE_CHOICES, default=BURIAL, verbose_name=_('type'))
    deceased = CharField(max_length=100,     validators=[name_validator], **optional, verbose_name=_('deceased'))
    date     = DateField(default=date.today, validators=date_validators, verbose_name=_('date'))
    spot     = ForeignKey(Spot, related_name='operations', verbose_name=_('spot'))
    exhumation_written_report = CharField(max_length=20, **optional, verbose_name=_('exhumation written report'))
    remains_brought_from      = CharField(max_length=50, **optional, verbose_name=_('remains brought from'))

    class Meta:
        ordering = ['date', 'spot']
        verbose_name = _('Operation')
        verbose_name_plural = _('Operations')

    def __str__(self):
        display_initials = initials(self.deceased) if self.deceased else ''
        return f"'{self.date:%y}: {self.spot} {Operation.TYPE_SYMBOLS[self.type]} {display_initials}"

    def clean_fields(self, exclude=None):
        self.deceased = title_case(self.deceased)
        self.date = parse_date(self.date)
        super(Operation, self).clean_fields(exclude)


"""
Constructions
"""

class CompanyManager(Manager):
    @staticmethod
    def prepare_natural_key(identifier: str) -> Dict[str, str]:
        return {'name': title_case(identifier)}

    def get_by_natural_key(self, name):
        return self.get(name=name)

class Company(WarningModel):
    """
    Construction company
    """
    # No title-casing or restricting characters,
    # this is not a person's name, a company can be written in any way
    name = CharField(max_length=250, unique=True, verbose_name=_('name'))  # no validator?

    objects = CompanyManager()

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def natural_key(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def n_constructions(self):
        return self.constructions.count()

    def clean_fields(self, exclude=None):
        self.name = title_case(self.name)
        super(Company, self).clean_fields(exclude)


class Construction(WarningModel):
    TOMB   = 't'
    BORDER = 'b'
    TYPE_CHOICES = [
        (TOMB,   _('tomb')),
        (BORDER, _('border'))
    ]
    TYPE_SYMBOLS = {
        TOMB:   'T',
        BORDER: 'B',
        None:   '?',
    }
    type          = CharField(max_length=1, choices=TYPE_CHOICES, **optional, verbose_name=_('type'))
    spots         = ManyToManyField(Spot, verbose_name=_('spots'))
    company       = ForeignKey(Company, **optional, verbose_name=_('company'))
    owner_builder = ForeignKey(Owner,   **optional, related_name='constructions_built', verbose_name=_('owner builder'))

    class Meta:
        default_related_name = 'constructions'
        # unique_together = ('type', 'spots')  # can't unique m2m
        ordering = ['type']  # FIXME add spots to ordering (as it is in the str)
        verbose_name = _('Construction')
        verbose_name_plural = _('Constructions')

    def __str__(self):
        if not self.spots:
            first_spot, more = '?', ''
        else:
            [first_spot], more = head_plus_more(self.spots.all(), head_length=1)
        return f'{Construction.TYPE_SYMBOLS[self.type]} {ON_TRANS} {first_spot}{more}'

    @property
    def authorization_spots(self):
        # Construction - spot relation goes through an authorization
        if not self.authorizations:
            return
        return Spot.objects.filter(authorizations__in=self.authorizations.all())

    def diagnose_warnings(self, only_related_to=None):
        if (only_related_to is None or only_related_to == Owner) and self.owner_builder:
            active_owners = Owner.objects.filter(deeds__isnull=False, deeds__cancel_reason__isnull=True)
            if not active_owners.filter(id=self.owner_builder.id).exists():
                # owners_links = show_head_links(active_owners, "all")  # FIXME django.core.exceptions.ValidationError: {'session_key': ['Session with this Session key already exists.']} when including it in the message
                yield _(f'owner builder {entity_tag(self.owner_builder)} is not one of the owners'), self

        if only_related_to is None or class_name(only_related_to) == 'Authorization':
            if not self.authorizations:
                yield _(f'no authorizations'), self
            else:
                spots_without_authorization = self.spots.exclude(id__in=self.authorization_spots)
                if spots_without_authorization:
                    links = show_head_links(spots_without_authorization, 'all')
                    yield _(f'spots without authorization: {links}'), self

        if only_related_to is None or only_related_to == Owner or class_name(only_related_to) == 'Authorization':
            if self.owner_builder and self.company:
                yield _(f'both owner builder {entity_tag(self.owner_builder)} and company {entity_tag(self.company)}'), self
            if not self.owner_builder and not self.company:
                yield _('neither owner builder nor company')

        if only_related_to is None:
            for spot in self.spots.all():
                yield from spot.diagnose_warnings(only_related_to=self)


class Authorization(NrYear):
    # Construction authorization
    spots        = ManyToManyField(Spot,    related_name='authorizations', verbose_name=_('spots'))
    construction = ForeignKey(Construction, related_name='authorizations', **optional, verbose_name=_('construction'))

    class Meta:
        verbose_name = _('Authorization')
        verbose_name_plural = _('Authorizations')


"""
Payments
"""
class PaymentReceipt(NrYear):
    class Meta:
        verbose_name = _('Payment Receipt')
        verbose_name_plural = _('Payment Receipts')

    @property
    def spots(self):
        return Spot.objects.filter(payments__in=self.units.all())

    @property
    def owners(self):
        return Owner.objects.filter(deeds__spots__payments__in=self.units.all())

    @property
    def units_years(self):
        # .order_by is required to make .distinct work correctly since Meta::ordering is defined for Payments
        return self.units.order_by().values_list('year', flat=True).distinct()

    @property
    def total_value(self):
        aggregation = self.units.aggregate(Sum('value'))
        return aggregation['value__sum']


class PaymentUnit(ModelWithYear):
    """ one unit is for a single year-spot combination. one receipt can have multiple units """
    spot    = ForeignKey(Spot, related_name='payments', verbose_name=_('spot'))
    # expected value for this year, for this spot
    value   = FloatField(**optional, validators=[payment_value_validator], verbose_name=_('value'))
    receipt = ForeignKey(PaymentReceipt, related_name='units', **optional, verbose_name=_('receipt'))

    class Meta:
        # there cannot be multiple payments in the same year for a spot
        # (there can be multiple receipts)
        unique_together = ('year', 'spot')
        ordering = ['year', 'spot']
        verbose_name = _('Payment Unit')
        verbose_name_plural = _('Payment Units')

    def __str__(self):
        return f'{self.spot} {FOR_TRANS} {year_to_shorthand(self.year)}'

    @property
    def owners(self):
        # The payment-owners relation goes through a spot and a deed
        # FIXME this should be the owner for THIS year, not all previous and future ones (same for Maintenance and PaymentReceipt)
        return Owner.objects.filter(deeds__spots=self.spot)


"""
Maintenance
"""

class Maintenance(ModelWithYear):
    spot = ForeignKey(Spot, related_name='maintenances', verbose_name=_('spot'))
    kept = BooleanField(verbose_name=_('kept'))

    class Meta:
        unique_together = ('year', 'spot')  # only one entry in the table for the spot
        ordering = ['year', 'spot']
        verbose_name = _('Maintenance')
        verbose_name_plural = _('Maintenances')

    def __str__(self):
        return f'{self.spot} {IN_TRANS} {year_to_shorthand(self.year)}'

    @property
    def owners(self):
        # The maintenance-owner relation goes through a spot and a deed
        return Owner.objects.filter(deeds__spots__maintenances=self)


ALL_MODELS = [
    Spot,
    Deed, OwnershipReceipt, Owner,
    Operation,
    Construction, Authorization, Company,
    PaymentUnit, PaymentReceipt,
    Maintenance,
]
