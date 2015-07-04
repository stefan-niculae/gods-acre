from django.db import models


#
# Utils
#


# TODO can't i make this an abstract class that inherits models.Model?
def fields_and_values(model):
    res = '('
    for f in model._meta.fields:
        res += f.name + ' '
        try:
            value = str(getattr(model, f.name))
        except:
            value = '-'

        res += value
        res += '; '
    res += ')'
    return res


# Abstract class for deeds, receipts & autorizations
class NrYear(models.Model):
    # TODO each class that derives this has a unique nr/date combination
    number = models.IntegerField()
    date = models.DateField()   # TODO make this default to today

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
        return fields_and_values(self)


#
# Ownership part
#

# Act de concesiune
class OwnershipDeed(NrYear):
    spots = models.ManyToManyField(Spot)


# Chitanta concesiune
class OwnershipReceipt(NrYear):
    value = models.FloatField()


# Concesionar
class Owner(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)

    def __str__(self):
        return fields_and_values(self)


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

    BURIAL = 'bral'
    EXHUMATION = 'exhm'
    OPERATION_TYPES = (
        (BURIAL, 'bordura'),
        (EXHUMATION, 'cavou'),
    )
    type = models.CharField(max_length=4, choices=OPERATION_TYPES, default=BURIAL)

    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    notes = models.CharField(max_length=250)

    def __str__(self):
        return fields_and_values(self)


#
# Maintenance part
#

# Intretinere
class MaintenenceLevel(models.Model):
    spot = models.ForeignKey(Spot)
    year = models.IntegerField()

    KEPT = 'kept'
    UNKEPT = 'ukpt'
    MAINTENENCE_LEVELS = (
        (KEPT, 'intretinut'),
        (UNKEPT, 'neintretinut'),
    )
    description = models.CharField(max_length=4, choices=MAINTENENCE_LEVELS, default=KEPT)

    def __str__(self):
        return fields_and_values(self)


#
# Contributions part
#

class ContributionReceipt(NrYear):
    def total_value(self):
        value = 0
        # TODO summation of all yearly payments that have this as the receipt
        return value


# Plata pe an
class YearlyPayment(models.Model):
    spot = models.ForeignKey(Spot)
    receipt = models.ForeignKey(ContributionReceipt)
    year = models.IntegerField()
    value = models.IntegerField()

    def __str__(self):
        return fields_and_values(self)
