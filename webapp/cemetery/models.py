from datetime import date
from typing import Optional

from django.db.models import Model, ForeignKey, TextField, IntegerField, CharField, \
    ManyToManyField, FloatField, BooleanField, DateField, Sum, Max
from django.contrib.auth.models import User

from .validators import name_validator
from .utils import display_head_tail_summary

"""
Mixins
"""

class Annotatable(Model):
    note = TextField(blank=True, null=True)

    class Meta:
        abstract = True


class NrYear(Model):
    """
    For deeds, receipts and authorizations
    """
    number = IntegerField()
    year   = IntegerField(default=date.today().year)
    # todo warn if date too far from current year

    class Meta:
        abstract = True
        unique_together = ('number', 'year')
        ordering = ['number', 'year']

    def __str__(self):
        return f'{self.number}/{self.year}'


"""
Spot - the central entity
"""

class Spot(Model):
    parcel  = CharField(max_length=5)  # TODO regex only alphanumeric
    row     = CharField(max_length=5)
    column  = CharField(max_length=5)

    class Meta:
        unique_together = ('parcel', 'row', 'column')  # they uniquely identify the spot
        ordering = ['parcel', 'row', 'column']

    def __str__(self):
        return f'{self.parcel}-{self.row}-{self.column}'

    # TODO add warning if more than one deed is active for a spot
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

    # @property
    # def ownership_receipts(self):
    #     # The receipt-spot relation goes through a deed
    #     deed = self.active_deeds.first()
    #     if not deed:
    #         return
    #     return deed.receipts

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

        # TODO red if bigger than 7
        return f'{smallest_unkept_year} ({years_difference} year{"s" if years_difference > 1 else ""})'

    @property
    def last_operation(self):  # -> Optional[Operation]: no forward declaration so this can't be hinted conveniently
        return self.operations.order_by('date').first()

    @property
    def last_paid_year(self):
        aggregation = self.payments.aggregate(Max('year'))
        return aggregation['year__max']


"""
Ownership
"""

class Deed(NrYear):
    spots = ManyToManyField(Spot, related_name='deeds')

    OWNER_DEAD = 'o'
    DONATED    = 'd'
    LOST       = 'l'
    CANCEL_REASON_CHOICES = [
        (OWNER_DEAD, 'owner dead'),
        (DONATED,    'donated'),
        (LOST,       'lost')
    ]
    # TODO when the name of the owner is the one in a burial operation, offer a suggestion to modify this
    # TODO add css to differentiate it from active ones
    cancel_reason = CharField(max_length=1, choices=CANCEL_REASON_CHOICES, blank=True, null=True)

    # class Meta:
    # TODO ask if this is true?
    #     unique_together = ('year', 'spot')


class OwnershipReceipt(NrYear):
    # todo warn if the deed's date is too far away from the receipt's date
    deed  = ForeignKey(Deed, related_name='receipts')
    value = FloatField()

    @property
    def spots(self):
        # The receipt-spot relation goes through a deed
        return self.deed.spots

    @property
    def owners(self):
        # The receipt-owner relation goes through a deed
        return self.deed.owners


class Owner(Model):
    name    = CharField(max_length=100, unique=True, validators=[name_validator])
    phone   = CharField(max_length=15,  null=True, blank=True)  # TODO regex validation
    address = CharField(max_length=250, null=True, blank=True)
    deeds   = ManyToManyField(Deed, related_name='owners', blank=True)

    class Meta:
        ordering = ['name']

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


"""
Operations
"""

class Operation(Annotatable):
    BURIAL     = 'b'
    EXHUMATION = 'e'
    TYPE_CHOICES = [
        (BURIAL,     'burial'),
        (EXHUMATION, 'exhumation')
    ]
    type = CharField(max_length=1, choices=TYPE_CHOICES, default=BURIAL)
    # TODO warning if exhumation is not the same as one buried
    name = CharField(max_length=100, validators=[name_validator])
    spot = ForeignKey(Spot, related_name='operations')
    date = DateField(default=date.today)  # TODO warn if date is too far from current

    # TODO show how many there are currently burried when adding a new operation

    class Meta:
        ordering = ['date', 'spot']

    def __str__(self):
        return f"{self.type.upper()}: {self.spot} in '{self.date:%y}"


"""
Constructions
"""

class Company(Model):
    """
    Construction company
    """
    # No title-casing or restricting characters,
    # this is not a person's name, a company can be written in any way
    name = CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name

    @property
    def n_constructions(self):
        return self.constructions.count()


class Construction(Model):
    TOMB   = 't'
    BORDER = 'b'
    TYPE_CHOICES = [
        (TOMB,   'tomb'),
        (BORDER, 'border')
    ]
    # TODO warn if there is already a construction on the same spot
    type          = CharField(max_length=1, choices=TYPE_CHOICES)
    spots         = ManyToManyField(Spot)
    company       = ForeignKey(Company, blank=True, null=True)
    owner_builder = ForeignKey(Owner,   blank=True, null=True)
    # TODO warn if owner entered is not one in spots.deeds.owners

    class Meta:
        default_related_name = 'constructions'
        # TODO ask about unique
        # unique_together = ('type', 'spots')
        ordering = ['type']  # TODO spots to ordering?

    def __str__(self):
        [first_spot], more = display_head_tail_summary(self.spots.all(), head_length=1)
        return f'{self.type.upper()} on {first_spot} {more}'

    @property
    def authorization_spots(self):
        # Construction - spot relation goes through an authorization
        if not self.authorizations:
            return
        return Spot.objects.filter(authorizations__in=self.authorizations.all())


class Authorization(NrYear):
    # Construction authorization
    spots        = ManyToManyField(Spot,    related_name='authorizations')
    construction = ForeignKey(Construction, related_name='authorizations', blank=True, null=True)
    # TODO warn if construction.spots differ from spots


"""
Payments
"""

class Payment(Model):
    year = IntegerField()  # TODO warn if year too far away from current year, or ASK how it relates to deed
    spot = ForeignKey(Spot, related_name='payments')

    class Meta:
        # there cannot be multiple payments in the same year for a spot
        # (there can be multiple receipts)
        unique_together = ('year', 'spot')
        ordering = ['year', 'spot']

    def __str__(self):
        return f'{self.year} for {self.spot}'

    @property
    def owners(self):
        # The payment-owners relation goes through a spot and a deed
        # TODO this should be the owner for THIS year, not all previous and future ones
        return Owner.objects.filter(deeds__spots=self.spot)

    @property
    def total_value(self):
        aggregation = self.receipts.aggregate(Sum('value'))
        return aggregation['value__sum']


class PaymentReceipt(NrYear):
    value    = FloatField()
    payments = ManyToManyField(Payment, related_name='receipts')
    # TODO warn if is already another receipt for the same payment, and link to it

    @property
    def spots(self):
        return Spot.objects.filter(payments__in=self.payments.all())

    @property
    def owners(self):
        # TODO only the owner(s) at the time, not all past and future
        return Owner.objects.filter(deeds__spots__payments__in=self.payments.all())

    @property
    def payments_years(self):
        # .order_by is required to make .distinct work correctly since Meta::ordering is defined for Payments
        return self.payments.order_by().values_list('year', flat=True).distinct()


"""
Maintenance
"""

class Maintenance(Model):
    year = IntegerField()  # TODO warn if year too far away from current year
    spot = ForeignKey(Spot, related_name='maintenances')
    kept = BooleanField()

    class Meta:
        unique_together = ('year', 'spot')  # only one entry in the table for the spot
        ordering = ['year', 'spot']

    def __str__(self):
        return f'{self.spot} in {self.year}'

    @property
    def owners(self):
        # The maintenance-owner relation goes through a spot and a deed
        # TODO this should be the owner for THIS year, not all previous and future ones
        return Owner.objects.filter(deeds__spots__maintenances=self)
