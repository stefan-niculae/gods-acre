# -*- coding: utf-8 -*-

from django.db import models
from datetime import date


#
# Utils
#


# TODO can't i make this an abstract class that inherits models.Model?
def fields_and_values(model):
    res = ''
    fields = model._meta.fields

    for idx, f in enumerate(fields):
        if f.name == 'id':
            res += '#'
        else:
            res += f.name + ' '

        try:
            value = str(getattr(model, f.name))
        except AttributeError:
            value = '-'

        res += value
        if idx < len(fields) - 1:
            res += '; '

    return res


# Abstract class for deeds, receipts & autorizations
class NrYear(models.Model):
    # todo constraint each class that derives this has a unique nr/date combination
    number = models.IntegerField()
    date = models.DateField(default=date.today)  # todo warn if date too far from current year

    def __str__(self):
        return '{0}/{1}'.format(self.number, self.date.year)


#
# Actual Models
#


class Spot(models.Model):
    parcel = models.CharField(max_length=10)
    row = models.CharField(max_length=10)
    column = models.CharField(max_length=10)
    note = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        # todo make this more reatable (dashes, no PRC)
        return '#{0} P{1} R{2} C{3}'.format(self.id, self.parcel, self.row, self.column)

    def identif(self):
        """
        :return: list of identifing data about this spot
        """
        return [self.id, self.parcel, self.row, self.column]

    def most_recent_deed_up_to(self, year):
        return self.ownership_deeds.filter(date__lte=date(year, 12, 31)).order_by('-date')[0]


#
# Ownership part
#

class OwnershipDeed(NrYear):
    # todo make it not possible to enter a deed without an owner having it as the deed
    spots = models.ManyToManyField(Spot, related_name='ownership_deeds')
    # todo warn if the most recent deed on this spot has the same owner as the one entered

    def remote_spot(self):
        # todo a deed can have multiple spots!!!! which one do we chose?
        return self.spots.all()[0]


class OwnershipReceipt(NrYear):
    # todo constraint can't give a receipt for two deeds on the same spot
    # todo warn if the deed's date is too far away from the receipt's date
    ownership_deed = models.ForeignKey(OwnershipDeed, related_name='receipts')
    value = models.FloatField()


class Owner(models.Model):
    ownership_deeds = models.ManyToManyField(OwnershipDeed, related_name='owners')
    first_name = models.CharField(max_length=25)  # todo input only letters
    last_name = models.CharField(max_length=25)   # todo capitalize each word entered on a name field
    phone = models.CharField(max_length=15, null=True, blank=True)  # todo regex validation for this

    def __str__(self):
        return fields_and_values(self)

    def identif(self):
        """
        :return: identifing data about this person, as a list
        """
        return [self.first_name, self.last_name]

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def phone_display(self):
        return '0{0} {1} {2}'.format(self.phone[0:3], self.phone[3:6], self.phone[6:9])


#
# Construction part
#

class ConstructionAuthorization(NrYear):
    # todo constraint authorization date after deed date
    # todo constraint can't have more than one authorization per year per spot
    spots = models.ManyToManyField(Spot, related_name='construction_authorizations')


class ConstructionCompany(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return fields_and_values(self)


class Construction(models.Model):
    # todo warn on a new construction on a spot that has an ownership deed older than 6 months after the constr authorization
    # todo warn if there is already a border/tomb on the same spot
    BORDER = 'brdr'
    TOMB = 'tomb'
    CONSTRUCTION_TYPES = (
        (BORDER, 'bordură'),
        (TOMB, 'cavou'),
    )
    type = models.CharField(max_length=4, choices=CONSTRUCTION_TYPES, default=BORDER)

    # TODO add constraint owner builder and construction company can't BOTH be null, or BOTH not null

    # todo add constraint owner_builder must be one of the owners
    owner_builder = models.ForeignKey(Owner, null=True, blank=True)  # todo (also add a preference to show 'Regie Proprie' or the actual name of the builder)
    construction_company = models.ForeignKey(ConstructionCompany, null=True, blank=True)  # todo aren't the company/builder supposed to be one on one?
    construction_authorization = models.ForeignKey(ConstructionAuthorization, related_name='constructions')

    def __str__(self):
        return fields_and_values(self)

    def remote_spot(self):
        spots = self.construction_authorization.spots.all()
        # todo an auth can be given to multiple fields, which one do we chose to represent the construction in the table?
        return spots[0]

    def constructor(self):
        if self.owner_builder is not None:
            return self.owner_builder.full_name()
        else:
            return self.construction_company.name


#
# Operations part
#

class Operation(models.Model):
    spot = models.ForeignKey(Spot, related_name='operations')  # todo show how many there are buried when adding a new operation
    date = models.DateField(default=date.today)  # todo warn if date is in the future

    BURIAL = 'bral'
    EXHUMATION = 'exhm'
    OPERATION_TYPES = (
        (BURIAL, 'înhumare'),
        (EXHUMATION, 'dezhumare'),
    )
    type = models.CharField(max_length=4, choices=OPERATION_TYPES, default=BURIAL)

    first_name = models.CharField(max_length=25)  # todo warn if there is an exhumation of a person that wasn't buried on that spot
    last_name = models.CharField(max_length=25)
    note = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return fields_and_values(self)

    # person should have been a model... this is not DRY
    def full_name(self):
        return self.first_name + ' ' + self.last_name


#
# Maintenance part
#

class MaintenanceLevel(models.Model):
    spot = models.ForeignKey(Spot)
    year = models.IntegerField()  # todo warn if year > 1950 or year < current year + 1

    KEPT = 'kept'
    UNKEPT = 'ukpt'
    MAINTENENCE_LEVELS = (
        (KEPT, 'întreținut'),
        (UNKEPT, 'neîntreținut'),
    )
    description = models.CharField(max_length=4, choices=MAINTENENCE_LEVELS, default=KEPT)

    def __str__(self):
        return '\'{0}:{1}{2}'.format(int(self.year) % 100,
                                     self.spot.id,
                                     '+' if self.description == self.KEPT else '-')

    class Meta:
        unique_together = ('spot', 'year')


#
# Contributions part
#

class ContributionReceipt(NrYear):
    # todo add constraint: a single receipt with the same nr/year per spot
    # todo add constraint: date afte deed date
    pass


class YearlyPayment(models.Model):
    # todo add constraint: only one payment per year per spot
    # todo add constraint: year after or equal to deed date
    # todo warn if there are holes in the payments line (they must come one after another)
    spot = models.ForeignKey(Spot)
    receipt = models.ForeignKey(ContributionReceipt)
    year = models.IntegerField()
    value = models.IntegerField() # TODO make this a float

    def __str__(self):
        return fields_and_values(self)
