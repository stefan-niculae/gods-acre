from django.db import models
from django.utils import timezone


# Abstract class for deeds, receipts & autorizations
class NrYear(models.Model):
    # TODO each class that derives this has a unique nr/date combination
    number = models.IntegerField()
    date = models.DateField(default=timezone.now())


# Loc de veci
class Spot(models.Model):
    parcel = models.CharField(max_length=10)    # parcela
    row = models.CharField(max_length=10)       # rand
    column = models.CharField(max_length=10)    # coloana (loc)


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


#
# Construction part
#

# Autorizatie de constructie
class ConstructionAuthorization(NrYear):
    spots = models.ManyToManyField(Spot)


# Firma de constructii
class ConstructionCompany(models.Model):
    name = models.CharField(max_length=50)


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
