from django.contrib.admin import TabularInline
from jet.admin import CompactInline

from .models import OwnershipReceipt, Maintenance, Operation,  Payment, Construction, Authorization


class SmallInline(TabularInline):
    extra = 1
    show_change_link = True

class LargeInline(CompactInline):  # yeah, the name they chose, "Compact", can lead to confusion
    extra = 1
    show_change_link = True


class OwnershipReceiptInline(SmallInline):
    model = OwnershipReceipt

class MaintenanceInline(SmallInline):
    model = Maintenance

class OperationInline(LargeInline):
    model = Operation

class ConstructionInline(SmallInline):
    model = Construction

class AuthorizationInline(SmallInline):
    model = Authorization

class PaymentInline(SmallInline):
    model = Payment
