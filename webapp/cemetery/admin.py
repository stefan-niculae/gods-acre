from django.utils.translation import pgettext_lazy, ugettext_lazy as _

from django.contrib.admin import ModelAdmin, register, site
from django.db.models import Min, Case, When, Max
from django.contrib.messages import SUCCESS
from easy import short, SimpleAdminField

from .models import Spot, Deed, OwnershipReceipt, Owner, Maintenance, Operation, PaymentUnit, PaymentReceipt, \
    Construction, Authorization, Company
from .forms import SpotForm, DeedForm, OwnerForm, AuthorizationForm, PaymentReceiptForm
from .inlines import OwnershipReceiptInline, MaintenanceInline, OperationInline, ConstructionInline, \
    AuthorizationInline, PaymentUnitInline
from .utils import rev
from .display_helpers import entity_tag, display_head_links, truncate, display_date, year_to_shorthand

"""
Site
"""

site.site_header = _("God's Acre")  # in the menus
site.site_title  = _("God's Acre")  # in the tab's title
site.index_title = _("Cemetery Administration")  # in the tab's title, for the home page
site.site_url = None  # remove the "View Site" link


class CustomModelAdmin(ModelAdmin):
    class Media:
        css = {
            # HACK
            'all': ['remove-second-breadcrumb.css']
        }


"""
Spot
"""

@register(Spot)
class SpotAdmin(CustomModelAdmin):
    # What columns the list-view has
    list_display = ['__str__', 'display_parcel', 'display_row', 'display_column',
                    'display_active_deed',
                    'display_shares_deed_with',
                    'display_owners',
                    # 'display_ownership_receipts',  removed because TMI
                    'display_operations',
                    'display_constructions',
                    'display_shares_authorizations_with',
                    'display_last_paid_year',
                    'display_unkept_since']

    # What filters are available at the top of the list-view page: "by field" combo-box
    list_filter = rev(['parcel', 'row', 'column',
                       'deeds', 'deeds__owners', 'deeds__receipts',
                       'operations__type', 'constructions__type',
                       'constructions__company'])

    search_fields = ['parcel', 'row', 'column',
                     'deeds__number', 'deeds__year',
                     'deeds__owners__name',
                     'deeds__receipts__number', 'deeds__receipts__year',
                     'operations__type', 'constructions__type',
                     'constructions__company__name']

    form = SpotForm
    inlines = [OperationInline, PaymentUnitInline, MaintenanceInline]

    def get_queryset(self, request):
        qs = super(SpotAdmin, self).get_queryset(request)
        return qs.annotate(first_operation=Min('operations'),
                           first_construction=Min('constructions'),
                           first_active_deed=Min(Case(
                               When(deeds__cancel_reason__isnull=True, then='deeds'))),
                           first_active_owner=Min(Case(
                               When(deeds__cancel_reason__isnull=True, then='deeds__owners__name'))),
                           # first_sharing_deed_spot=Min(
                           #     When(Q(deeds__spots__deeds=spot.deeds) & Q(~deeds__spots=spot)), then='deeds__spots'),
                           max_payments_year=Max('payments__year'))

    display_parcel = SimpleAdminField(lambda spot: spot.parcel, 'P', 'parcel')
    display_row    = SimpleAdminField(lambda spot: spot.row,    'R', 'row')
    display_column = SimpleAdminField(lambda spot: spot.column, 'C', 'column')

    @short(desc=_('Active Deed'), order='first_active_deed', tags=True)
    def display_active_deed(self, spot):
        return display_head_links(spot.active_deeds, 1)

    @short(desc=_('Sharing Deed'), tags=True)
    def display_shares_deed_with(self, spot):
        return display_head_links(spot.shares_deed_with)

    # @short(desc=_('Deed Receipts'), order='deeds_receipts', tags=True)
    # def display_ownership_receipts(self, spot):
    #     return display_head_links(spot.ownership_receipts)

    @short(desc=_('Active Owners'), order='first_active_owner', tags=True)
    def display_owners(self, spot):
        return display_head_links(spot.active_owners)

    @short(desc=_('Operations'), order='first_operation', tags=True)
    def display_operations(self, spot):
        return display_head_links(spot.operations, 1)

    @short(desc=_('Constructions'), order='first_construction', tags=True)
    def display_constructions(self, spot):
        return display_head_links(spot.constructions, 1)

    @short(desc=_('Sharing Auth.'), tags=True)
    def display_shares_authorizations_with(self, spot):
        return display_head_links(spot.shares_authorization_with)

    @short(desc=_('Last Paid'), order='max_payments_year')
    def display_last_paid_year(self, spot):
        return spot.last_paid_year

    @short(desc=_('Unkept Since'))
    def display_unkept_since(self, spot):
        return spot.unkept_since


"""
Ownership
"""

@register(Deed)
class DeedAdmin(CustomModelAdmin):
    form = DeedForm

    list_display = ['display_repr', 'number', 'year', 'cancel_reason',
                    'display_spots', 'display_receipts', 'display_owners']

    list_filter = rev(['number', 'year', 'cancel_reason',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column',
                       'owners',
                       'receipts'])

    search_fields = ['number', 'year', 'cancel_reason',
                     'spots__parcel', 'spots__row', 'spots__column',
                     'owners__name',
                     'receipts__number', 'receipts__year']

    inlines = [OwnershipReceiptInline]

    def get_queryset(self, request):
        qs = super(DeedAdmin, self).get_queryset(request)
        return qs.annotate(first_spot=Min('spots'),
                           first_receipt=Min('receipts'),
                           first_owner=Min('owners'))

    @short(desc=pgettext_lazy('short', 'Deed'), order='__str__')
    def display_repr(self, deed):
        return str(deed)

    @short(desc=_('Spots'), order='first_spot', tags=True)
    def display_spots(self, deed):
        return display_head_links(deed.spots)

    @short(desc=_('Receipts'), order='first_receipt', tags=True)
    def display_receipts(self, deed):
        return display_head_links(deed.receipts)

    @short(desc=_('Owners'), order='first_owner', tags=True)
    def display_owners(self, deed):
        return display_head_links(deed.owners)


@register(OwnershipReceipt)
class OwnershipReceiptAdmin(CustomModelAdmin):
    list_display = ['display_repr', 'number', 'year', 'value',
                    'display_deed', 'display_spots', 'display_owners']

    list_filter = rev(['number', 'year', 'value',
                       'deed',
                       'deed__spots', 'deed__spots__parcel', 'deed__spots__row', 'deed__spots__column'])

    search_fields = ['number', 'year', 'value',
                     'deed__year', 'deed__number',
                     'deed__spots__parcel', 'deed__spots__row', 'deed__spots__column']

    def get_queryset(self, request):
        # http://stackoverflow.com/questions/2168475/django-admin-how-to-sort-by-one-of-the-custom-list-display-fields-that-has-no-d
        qs = super(OwnershipReceiptAdmin, self).get_queryset(request)
        # Out of all the spots for this receipt's deed,
        # get the minimum one (as defined by Spot::ordering).
        # Because that the order they are shown in the cell as well
        return qs.annotate(first_spot=Min('deed__spots'),
                           first_owner=Min('deed__owners'))

    @short(desc=_('Receipt'), order='__str__')
    def display_repr(self, receipt):
        return str(receipt)

    @short(desc=pgettext_lazy('short', 'Deed'), order='deed', tags=True)
    def display_deed(self, receipt):
        return entity_tag(receipt.deed)

    @short(desc=_('Spots'), order='first_spot', tags=True)
    def display_spots(self, receipt):
        return display_head_links(receipt.spots)

    @short(desc=_('Owners'), order='first_owner', tags=True)
    def display_owners(self, receipt):
        return display_head_links(receipt.owners)


@register(Owner)
class OwnerAdmin(CustomModelAdmin):
    list_display = ['name', 'display_phone', 'display_address', 'display_city',
                    'display_spots', 'display_deeds', 'display_receipts',
                    # 'display_constructions'
                    ]

    list_filter = rev(['name', 'phone', 'address', 'city',
                       'deeds',
                       'deeds__spots', 'deeds__spots__parcel', 'deeds__spots__row', 'deeds__spots__column',
                       'constructions_built'])

    search_fields = ['name', 'phone', 'address', 'city',
                     'deeds__number', 'deeds__year',
                     'deeds__spots__parcel', 'deeds__spots__row', 'deeds__spots__column',
                     'constructions_built__type']

    form = OwnerForm
    inlines = [ConstructionInline]

    def get_queryset(self, request):
        qs = super(OwnerAdmin, self).get_queryset(request)
        return qs.annotate(first_deed=Min('deeds'),
                           first_receipt=Min('deeds__receipts'),
                           first_spot=Min('deeds__spots'),
                           # first_construction=Min('constructions_built')
                           )

    @short(desc=_('Phone'), order='phone')
    def display_phone(self, owner):
        if not owner.phone:
            return
        return f'{owner.phone[0:3]} {owner.phone[3:6]} {owner.phone[6:9]}'

    @short(desc=_('Address'), order='address')
    def display_address(self, owner):
        return truncate(owner.address)

    @short(desc=_('City'), order='city')
    def display_city(self, owner):
        return truncate(owner.city)

    @short(desc=pgettext_lazy('short', 'Deeds'), order='first_deed', tags=True)
    def display_deeds(self, owner):
        return display_head_links(owner.deeds)

    @short(desc=_('Receipts'), order='first_receipt', tags=True)
    def display_receipts(self, owner):
        return display_head_links(owner.receipts)

    @short(desc=_('Spots'), order='first_spot', tags=True)
    def display_spots(self, owner):
        return display_head_links(owner.spots)

    # @short(desc=_('Built'), order='first_construction', tags=True)
    # def display_constructions(self, owner):
    #     return display_head_links(owner.constructions_built)


"""
Operations
"""

@register(Operation)
class OperationAdmin(CustomModelAdmin):
    list_display = ['__str__', 'type', 'display_date', 'deceased', 'display_owner',
                    'display_spot', 'exhumation_written_report', 'remains_brought_from']

    date_hierarchy = 'date'

    list_filter = rev(['type', 'deceased', 'spot', 'exhumation_written_report', 'remains_brought_from',
                       'spot__parcel', 'spot__row', 'spot__column',
                       'spot__deeds__owners'])

    search_fields = ['type', 'date', 'deceased', 'note', 'exhumation_written_report', 'remains_brought_from',
                     'spot__parcel', 'spot__row', 'spot__column',
                     'spot__deeds__owners__name']

    def get_queryset(self, request):
        qs = super(OperationAdmin, self).get_queryset(request)
        # FIXME only active owners
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    @short(desc=_('Date'), order='date')
    def display_date(self, operation):
        return display_date(operation.date)

    @short(desc=_('Owner'), order='first_owner', tags=True)
    def display_owner(self, operation):
        return display_head_links(operation.spot.active_owners)

    @short(desc=_('Spot'), order='spot', tags=True)
    def display_spot(self, operation):
        return entity_tag(operation.spot)


"""
Constructions
"""

@register(Authorization)
class AuthorizationAdmin(CustomModelAdmin):
    list_display = ['__str__', 'number', 'year', 'display_spots', 'display_construction']

    list_filter = rev(['number', 'year',
                       'construction', 'construction__type',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column'])

    search_fields = ['number', 'year',
                     'construction__type',
                     'spots__parcel', 'spots__row', 'spots__column']

    form = AuthorizationForm

    @short(desc=_('Spots'), order='spots', tags=True)
    def display_spots(self, authorization):
        return display_head_links(authorization.spots)

    @short(desc=_('Construction'), order='construction', tags=True)
    def display_construction(self, authorization):
        return entity_tag(authorization.construction)


@register(Construction)
class ConstructionAdmin(CustomModelAdmin):
    list_display = ['__str__', 'type', 'display_authorizations', 'display_spots',
                    'display_owner_builder', 'display_company']

    list_filter = rev(['type', 'owner_builder', 'company',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column',
                       'authorizations'])

    search_fields = ['type', 'owner_builder__name', 'company__name',
                     'spots__parcel', 'spots__row', 'spots__column'
                     'authorizations__number', 'authorizations__year']

    inlines = [AuthorizationInline]

    @short(desc=_('Authorizations'), order='authorizations', tags=True)
    def display_authorizations(self, construction):
        return display_head_links(construction.authorizations)

    @short(desc=_('Spots'), order='authorizations__spots', tags=True)
    def display_spots(self, construction):
        return display_head_links(construction.spots)

    @short(desc=_('Owner Builder'), order='owner_builder', tags=True)
    def display_company(self, construction):
        return entity_tag(construction.company)

    @short(desc=_('Company'), order='company', tags=True)
    def display_owner_builder(self, construction):
        return entity_tag(construction.owner_builder)


@register(Company)
class CompanyAdmin(CustomModelAdmin):
    list_display = ['__str__', 'display_n_constructions', 'display_constructions']

    list_filter = rev(['name',
                       'constructions', 'constructions__type',
                       'constructions__spots',
                       'constructions__spots__parcel', 'constructions__spots__row', 'constructions__spots__column',
                       'constructions__authorizations',
                       'constructions__authorizations__number', 'constructions__authorizations__year'])

    search_fields = ['name',
                     'constructions__type',
                     'constructions__spots__parcel', 'constructions__spots__row', 'constructions__spots__column',
                     'constructions__authorizations__number', 'constructions__authorizations__year']

    inlines = [ConstructionInline]

    display_n_constructions = SimpleAdminField(lambda company: company.n_constructions, _('#Constructions'))

    @short(desc=_('Constructions'), order='constructions', tags=True)
    def display_constructions(self, company):
        return display_head_links(company.constructions, 5)


"""
Payments
"""

@register(PaymentUnit)
class PaymentUnitAdmin(CustomModelAdmin):
    list_display = ['__str__', 'year', 'display_spot', 'value',
                    'display_receipts',
                    'display_owners']

    list_filter = rev(['year', 'value',
                       'spot', 'spot__parcel', 'spot__row', 'spot__column',
                       'receipt', 'receipt__number', 'receipt__year',
                       'spot__deeds__owners'])

    search_fields = ['year', 'value',
                     'spot__parcel', 'spot__row', 'spot__column',
                     'receipt__number', 'receipt__year',
                     'spot__deeds__owners__name']

    def get_queryset(self, request):
        qs = super(PaymentUnitAdmin, self).get_queryset(request)
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    @short(desc=_('Spot'), order='spot', tags=True)
    def display_spot(self, payment):
        return entity_tag(payment.spot)

    @short(desc=_('Receipt'), order='receipt', tags=True)
    def display_receipts(self, payment):
        return entity_tag(payment.receipt)

    @short(desc=_('Owners'), order='first_owner', tags=True)
    def display_owners(self, payment):
        return display_head_links(payment.owners)


@register(PaymentReceipt)
class PaymentReceiptAdmin(CustomModelAdmin):
    list_display = ['__str__', 'number', 'display_receipt_year',
                    'total_value', 'display_payments',
                    'display_spots', 'display_payments_years',
                    'display_owners']

    list_filter = rev(['number', 'year',
                       'payments__spot', 'payments__spot__parcel', 'payments__spot__row', 'payments__spot__column',
                       'payments__spot__deeds__owners'])

    search_fields = ['number', 'year',
                     'payments__spot__parcel', 'payments__spot__row', 'payments__spot__column',
                     'payments__spot__deeds__owners__name']

    form = PaymentReceiptForm

    inlines = [PaymentUnitInline]

    def get_queryset(self, request):
        qs = super(PaymentReceiptAdmin, self).get_queryset(request)
        return qs.annotate(first_payment=Min('payments'),
                           first_spot=Min('payments__spot'),
                           first_owner=Min('payments__spot__deeds__owners'),
                           # first payment-year not the year in which the first payment was made
                           first_payment_year=Min('payments__year'))

    @short(desc=_('Payments'), order='first_payment', tags=True)
    def display_payments(self, receipt):
        return display_head_links(receipt.payments)

    @short(desc=_('Receipt Year'), order='year')
    def display_receipt_year(self, receipt):
        return receipt.year

    @short(desc=_('Spots'), order='first_spot', tags=True)
    def display_spots(self, receipt):
        return display_head_links(receipt.spots.distinct())

    @short(desc=_('Payments Years'), order='first_payment_year')
    def display_payments_years(self, receipt):
        return ', '.join(map(lambda y: "'" + year_to_shorthand(y), receipt.payments_years.all()))

    @short(desc=_('Owners'), order='first_owner', tags=True)
    def display_owners(self, receipt):
        return display_head_links(receipt.owners.distinct())


"""
Maintenance
"""

@register(Maintenance)
class MaintenanceAdmin(CustomModelAdmin):
    list_display = ['__str__', 'year', 'display_spot', 'kept',
                    'display_owners']

    list_filter = rev(['year', 'kept',
                       'spot', 'spot__parcel', 'spot__row', 'spot__column',
                       'spot__deeds__owners'])

    search_fields = ['year', 'kept',
                     'spot__parcel', 'spot__row', 'spot__column',
                     # FIXME DisallowedModelAdminLookup: Filtering by spot__deeds__owners__isnull not allowed
                     'spot__deeds__owners__name']

    actions = ['mark_kept', 'mark_unkept']

    def get_queryset(self, request):
        qs = super(MaintenanceAdmin, self).get_queryset(request)
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    @short(desc=_('Spot'), order='spot')
    def display_spot(self, maintenance):
        return entity_tag(maintenance.spot)

    @short(desc=_('Owners'), order='first_owner', tags=True)
    def display_owners(self, maintenance):
        return display_head_links(maintenance.owners)

    @short(desc=_('Mark selected entries as kept'))
    def mark_kept(self, request, queryset):
        n_updated = queryset.update(kept=True)

        if n_updated == 1:
            prefix = '1 entry was'
        else:
            prefix = f'{n_updated} entries were'
        self.message_user(request, prefix + ' successfully marked as kept',
                          level=SUCCESS)

    @short(desc=_('Mark selected entries as unkept'))
    def mark_unkept(self, request, queryset):
        n_updated = queryset.update(kept=False)

        if n_updated == 1:
            prefix = '1 entry was'
        else:
            prefix = f'{n_updated} entries were'
        self.message_user(request, prefix + ' successfully marked as unkept',
                          level=SUCCESS)
