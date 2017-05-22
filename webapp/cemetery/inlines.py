from django.contrib.admin import TabularInline

from .models import OwnershipReceipt, Maintenance, Operation,  Payment, Construction, Authorization


class CustomInline(TabularInline):
    extra = 1
    show_change_link = True

class OwnershipReceiptInline(CustomInline):
    model = OwnershipReceipt

class MaintenanceInline(CustomInline):
    model = Maintenance

# TODO make the textarea smaller intially, and move the note to the last position
class OperationInline(CustomInline):
    model = Operation

class ConstructionInline(CustomInline):
    model = Construction

class AuthorizationInline(CustomInline):
    model = Authorization

class PaymentInline(CustomInline):
    model = Payment
