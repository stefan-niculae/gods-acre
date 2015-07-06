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
        except:
            value = '-'

        res += value
        if idx < len(fields) - 1:
            res += '; '

    return res


# Abstract class for deeds, receipts & autorizations
class NrYear(models.Model):
    # TODO each class that derives this has a unique nr/date combination
    number = models.IntegerField()
    date = models.DateField(default=date.today)  # todo date must be less or equal to now

    def __str__(self):
        return '{0}/{1}'.format(self.number, self.date.year)

#
# Actual Models
#


# Loc de veci
class Spot(models.Model):
    parcel = models.CharField(max_length=10)    # parcela
    row = models.CharField(max_length=10)       # rand
    column = models.CharField(max_length=10)    # coloana (loc)

    def __str__(self):
        return '#{0} p{1}r{2}c{3}'.format(self.id, self.parcel, self.row, self.column)

    def identif(self):
        """
        :return: identifing data about this spot, as a list
        """
        return [self.id, self.parcel, self.row, self.column]


#
# Ownership part
#

# Act de concesiune
class OwnershipDeed(NrYear):
    spots = models.ManyToManyField(Spot, related_name='ownership_deeds')


# Chitanta concesiune
class OwnershipReceipt(NrYear):
    ownership_deed = models.ForeignKey(OwnershipDeed)
    value = models.FloatField()


# Concesionar
class Owner(models.Model):
    ownership_deed = models.ForeignKey(OwnershipDeed)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)

    def __str__(self):
        return fields_and_values(self)

    def identif(self):
        """
        :return: identifing data about this person, as a list
        """
        return [self.first_name, self.last_name]


#
# Construction part
#

# Autorizatie de constructie
class ConstructionAuthorization(NrYear):
    spots = models.ManyToManyField(Spot)


# Firma de constructii
class ConstructionCompany(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return fields_and_values(self)


class Construction(models.Model):
    BORDER = 'brdr'
    TOMB = 'tomb'
    CONSTRUCTION_TYPES = (
        (BORDER, 'bordura'),
        (TOMB, 'cavou'),
    )
    type = models.CharField(max_length=4, choices=CONSTRUCTION_TYPES, default=BORDER)

    # TODO owner builder and construction company can't BOTH be null, or BOTH not null
    owner_builder = models.ForeignKey(Owner, null=True)
    construction_company = models.ForeignKey(ConstructionCompany, null=True)

    def __str__(self):
        return fields_and_values(self)


#
# Operations part
#

# Operatie
class Operation(models.Model):
    spot = models.ForeignKey(Spot)
    date = models.DateField(default=date.today)  # todo date ?must be less or equal to now

    BURIAL = 'bral'
    EXHUMATION = 'exhm'
    OPERATION_TYPES = (
        (BURIAL, 'inhumare'),
        (EXHUMATION, 'dezhumare'),
    )
    type = models.CharField(max_length=4, choices=OPERATION_TYPES, default=BURIAL)

    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    note = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return fields_and_values(self)
    #todo add constraint how many can be buried at once


#
# Maintenance part
#

# Intretinere
class MaintenanceLevel(models.Model):
    spot = models.ForeignKey(Spot)
    year = models.IntegerField()  # add constraint over ?1950, under curr_year + 1

    KEPT = 'kept'
    UNKEPT = 'ukpt'
    MAINTENENCE_LEVELS = (
        (KEPT, 'intretinut'),
        (UNKEPT, 'neintretinut'),
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
    # todo add constraint a single receipt with the same nr/year per spot
    def total_value(self):
        # TODO summation of all yearly payments that have this as the receipt
        pass


# Plata pe an
class YearlyPayment(models.Model):
    spot = models.ForeignKey(Spot)
    receipt = models.ForeignKey(ContributionReceipt)
    year = models.IntegerField()
    value = models.IntegerField()

    def __str__(self):
        return fields_and_values(self)
