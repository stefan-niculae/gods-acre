from django.contrib.admin import TabularInline
from jet.admin import CompactInline

from .models import OwnershipReceipt, Maintenance, Operation,  PaymentUnit, Construction, Authorization


class SmallInline(TabularInline):
    extra = 1
    show_change_link = True

class LargeInline(CompactInline):  # yeah, the name they chose, "Compact", can lead to confusion
    extra = 1
    show_change_link = True


class OwnershipReceiptInline(SmallInline):
    model = OwnershipReceipt
    # verbose_name = _('Ownership Receipt')
    # verbose_name_plural = _('Ownership Receipts')

class MaintenanceInline(SmallInline):
    model = Maintenance
    # verbose_name = _('Maintenance')
    # verbose_name_plural = _('Maintenances')

class OperationInline(LargeInline):
    model = Operation
    # verbose_name = _('Operation')
    # verbose_name_plural = _('Operations')

class ConstructionInline(SmallInline):
    model = Construction
    # verbose_name = _('Construction')
    # verbose_name_plural = _('Constructions')

class AuthorizationInline(SmallInline):
    model = Authorization
    # verbose_name = _('Authorization')
    # verbose_name_plural = _('Authorizations')

class PaymentUnitInline(SmallInline):
    model = PaymentUnit
    # verbose_name = _('Payment Unit')
    # verbose_name_plural = _('Payment Units')
