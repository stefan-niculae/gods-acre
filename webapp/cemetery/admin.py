from django.db.models import Min, Sum, Case, When, Max
from django.contrib.admin import ModelAdmin, register, AdminSite
from django.contrib.messages import SUCCESS
from django.conf.urls import url
from django.template.response import TemplateResponse
from easy import short, SimpleAdminField

from .models import Spot, Deed, OwnershipReceipt, Owner, Maintenance, Operation, Payment, PaymentReceipt, Construction,\
    Authorization, Company
from .forms import SpotForm, DeedForm, OwnerForm, AuthorizationForm, PaymentReceiptForm, MaintenanceBulkForm
from .inlines import OwnershipReceiptInline, MaintenanceInline, OperationInline, ConstructionInline, \
    AuthorizationInline, PaymentInline
from .utils import rev, display_change_link, display_head_links, truncate, display_date

"""
Site
"""

class CustomAdminSite(AdminSite):
    # TODO use this instead of the default admin site
    site_header = "God's Acre"  # in the menus
    site_title = "God's Acre"  # in the tab's title
    index_title = "Cemetery Administration"  # in the tab's title, for the home page
    site_url = None  # remove the "View Site" link


"""
Spot
"""

@register(Spot)
class SpotAdmin(ModelAdmin):
    # What columns the list-view has
    list_display = ['__str__', 'display_parcel', 'display_row', 'display_column',
                    'display_active_deed',
                    'display_shares_deed_with',
                    'display_owners',
                    # 'display_ownership_receipts',  removed because TMI
                    'display_operations',
                    'display_constructions',
                    'display_shares_authorizations_with',
                    'display_last_paid_year',  # TODO sortable, filter-able
                    'unkept_since',  # TODO order
                    ]

    # What filters are available at the top of the list-view page: "by field" combo-box
    list_filter = rev(['parcel', 'row', 'column',
                       'deeds', 'deeds__owners', 'deeds__receipts',
                       # FIXME operations__type and constructions__type both read 'By type'
                       # TODO filter by missing too (eg construction type: "?")
                       'operations__type', 'constructions__type',
                       'constructions__company'])

    search_fields = ['parcel', 'row', 'column',
                     'deeds__number', 'deeds__year',
                     'deeds__owners__name',
                     'deeds__receipts__number', 'deeds__receipts__year',
                     # TODO make it possible to search for "burial" (field choice), not "b" (db value)
                     'operations__type', 'constructions__type',
                     'constructions__company__name']

    form = SpotForm
    inlines = [OperationInline, PaymentInline, MaintenanceInline]

    def get_queryset(self, request):
        qs = super(SpotAdmin, self).get_queryset(request)
        return qs.annotate(first_operation=Min('operations'),
                           first_construction=Min('constructions'),
                           first_active_deed=Min(Case(
                               When(deeds__cancel_reason__isnull=True, then='deeds'))),
                           first_active_owner=Min(Case(
                               When(deeds__cancel_reason__isnull=True, then='deeds__owners__name'))),
                           # TODO "shares deed with" order
                           # first_sharing_deed_spot=Min(
                           #     When(Q(deeds__spots__deeds=spot.deeds) & Q(~deeds__spots=spot)), then='deeds__spots'),
                           max_payments_year=Max('payments__year')
                           )

    display_parcel = SimpleAdminField(lambda spot: spot.parcel, 'P', 'parcel')
    display_row    = SimpleAdminField(lambda spot: spot.row,    'R', 'row')
    display_column = SimpleAdminField(lambda spot: spot.column, 'C', 'column')

    @short(desc='Deed', order='first_active_deed', tags=True)
    def display_active_deed(self, spot):
        return display_head_links(spot.active_deeds, 1)

    @short(desc='Sharing Deed', tags=True)
    def display_shares_deed_with(self, spot):
        return display_head_links(spot.shares_deed_with)

    # @short(desc='Deed Receipts', order='deeds_receipts', tags=True)
    # def display_ownership_receipts(self, spot):
    #     return display_head_links(spot.ownership_receipts)

    @short(desc='Owners', order='first_active_owner', tags=True)
    def display_owners(self, spot):
        return display_head_links(spot.active_owners)

    @short(desc='Operations', order='first_operation', tags=True)
    def display_operations(self, spot):
        return display_head_links(spot.operations, 1)

    @short(desc='Constructions', order='first_construction', tags=True)
    def display_constructions(self, spot):
        return display_head_links(spot.constructions, 1)

    @short(desc='Sharing Auth.', tags=True)  # TODO order
    def display_shares_authorizations_with(self, spot):
        return display_head_links(spot.shares_authorization_with)

    @short(desc='Last Paid', order='max_payments_year')
    def display_last_paid_year(self, spot):
        return spot.last_paid_year


"""
Ownership
"""

@register(Deed)
class DeedAdmin(ModelAdmin):
    form = DeedForm

    list_display = ['__str__', 'number', 'year', 'cancel_reason',
                    'display_spots', 'display_receipts', 'display_owners']

    # TODO date hierarchy by date added?
    # date_hierarchy = 'pseudo_date'

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

    @short(desc='Spots', order='first_spot', tags=True)
    def display_spots(self, deed):
        return display_head_links(deed.spots)

    @short(desc='Receipts', order='first_receipt', tags=True)
    def display_receipts(self, deed):
        return display_head_links(deed.receipts)

    @short(desc='Owners', order='first_owner', tags=True)
    def display_owners(self, deed):
        return display_head_links(deed.owners)


@register(OwnershipReceipt)
class OwnershipReceiptAdmin(ModelAdmin):
    list_display = ['__str__', 'number', 'year', 'value',
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

    @short(desc='Deed', order='deed', tags=True)
    def display_deed(self, receipt):
        return display_change_link(receipt.deed)

    @short(desc='Spots', order='first_spot', tags=True)
    def display_spots(self, receipt):
        return display_head_links(receipt.spots)

    @short(desc='Owners', order='first_owner', tags=True)
    def display_owners(self, receipt):
        return display_head_links(receipt.owners)


@register(Owner)
class OwnerAdmin(ModelAdmin):
    list_display = ['name', 'display_phone', 'display_address',
                    'display_deeds', 'display_receipts', 'display_spots', 'display_constructions']

    list_filter = rev(['name', 'phone', 'address',
                       'deeds',
                       'deeds__spots', 'deeds__spots__parcel', 'deeds__spots__row', 'deeds__spots__column',
                       'constructions_built'])

    search_fields = ['name', 'phone', 'address',
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
                           first_construction=Min('constructions_built'))

    @short(desc='Phone', order='phone')
    def display_phone(self, owner):
        if not owner.phone:
            return
        return f'{owner.phone[0:3]} {owner.phone[3:6]} {owner.phone[6:9]}'

    @short(desc='Address', order='address')
    def display_address(self, owner):
        return truncate(owner.address)

    @short(desc='Deeds', order='first_deed', tags=True)
    def display_deeds(self, owner):
        return display_head_links(owner.deeds)

    @short(desc='Receipts', order='first_receipt', tags=True)
    def display_receipts(self, owner):
        return display_head_links(owner.receipts)

    @short(desc='Spots', order='first_spot', tags=True)
    def display_spots(self, owner):
        return display_head_links(owner.spots)

    @short(desc='Built', order='first_construction', tags=True)
    def display_constructions(self, owner):
        return display_head_links(owner.constructions_built)


"""
Operations
"""

@register(Operation)
class OperationAdmin(ModelAdmin):
    list_display = ['__str__', 'type', 'display_date', 'name', 'display_spot', 'display_note']

    date_hierarchy = 'date'

    list_filter = rev(['type', 'name', 'spot',
                       'spot__parcel', 'spot__row', 'spot__column',
                       'spot__deeds__owners'])

    # TODO search by month name?
    search_fields = ['type', 'date', 'name', 'note',
                     'spot__parcel', 'spot__row', 'spot__column',
                     'spot__deeds__owners__name']

    @short(desc='Date', order='date')
    def display_date(self, operation):
        return display_date(operation.date)

    @short(desc='Spot', order='spot', tags=True)
    def display_spot(self, operation):
        return display_change_link(operation.spot)

    @short(desc='Note', order='note')
    def display_note(self, operation):
        return truncate(operation.note)


"""
Constructions
"""

@register(Authorization)
class AuthorizationAdmin(ModelAdmin):
    list_display = ['__str__', 'number', 'year', 'display_spots', 'display_construction']

    list_filter = rev(['number', 'year',
                       'construction', 'construction__type',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column'])

    search_fields = ['number', 'year',
                     'construction__type',
                     'spots__parcel', 'spots__row', 'spots__column']

    form = AuthorizationForm

    @short(desc='Spots', order='spots', tags=True)
    def display_spots(self, authorization):
        return display_head_links(authorization.spots)

    @short(desc='Construction', order='construction', tags=True)
    def display_construction(self, authorization):
        return display_change_link(authorization.construction)


@register(Construction)
class ConstructionAdmin(ModelAdmin):
    list_display = ['__str__', 'type', 'display_authorizations', 'display_spots', 'owner_builder', 'company']

    list_filter = rev(['type', 'owner_builder', 'company',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column',
                       'authorizations'])

    search_fields = ['type', 'owner_builder__name', 'company__name',
                     'spots__parcel', 'spots__row', 'spots__column'
                     'authorizations__number', 'authorizations__year']

    # TODO! constructions for spots
    inlines = [AuthorizationInline]

    @short(desc='Authorizations', order='authorizations', tags=True)
    def display_authorizations(self, construction):
        return display_head_links(construction.authorizations)

    @short(desc='Spots', order='authorizations__spots', tags=True)
    def display_spots(self, construction):
        return display_head_links(construction.spots)


@register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ['__str__', 'display_n_constructions', 'display_constructions']

    list_filter = rev(['name',
                       'constructions', 'constructions__type',
                       'constructions__spots',
                       'constructions__spots__parcel', 'constructions__spots__row', 'constructions__spots__column',
                       'constructions__authorizations',
                       # FIXME say "auth nr" instead of "number'
                       'constructions__authorizations__number', 'constructions__authorizations__year'])

    search_fields = ['name',
                     'constructions__type',
                     'constructions__spots__parcel', 'constructions__spots__row', 'constructions__spots__column',
                     'constructions__authorizations__number', 'constructions__authorizations__year']

    inlines = [ConstructionInline]

    display_n_constructions = SimpleAdminField(lambda company: company.n_constructions,
                                               '#Constructions')  # TODO order

    @short(desc='Constructions', order='constructions', tags=True)
    def display_constructions(self, company):
        return display_head_links(company.constructions, 5)


"""
Payments
"""

@register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ['__str__', 'year', 'display_spot', 'display_expected',
                    'display_receipts', 'display_received',
                    'display_owners']

    list_filter = rev(['year', 'expected',
                       'spot', 'spot__parcel', 'spot__row', 'spot__column',
                       'receipt', 'receipt__number', 'receipt__year',
                       'spot__deeds__owners'])

    search_fields = ['year', 'expected',
                     'spot__parcel', 'spot__row', 'spot__column',
                     'receipt__number', 'receipt__year',
                     'spot__deeds__owners__name']

    def get_queryset(self, request):
        qs = super(PaymentAdmin, self).get_queryset(request)
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    @short(desc='Spot', order='spot', tags=True)
    def display_spot(self, payment):
        return display_change_link(payment.spot)

    @short(desc='Expected value', order='expected')
    def display_expected(self, payment):
        return payment.expected

    @short(desc='Receipt', order='receipt', tags=True)
    def display_receipts(self, payment):
        return display_change_link(payment.receipt)

    @short(desc='Received value', order='receipt__value', tags=True)
    def display_received(self, payment):
        return payment.received_value

    @short(desc='Owners', order='first_owner', tags=True)
    def display_owners(self, payment):
        return display_head_links(payment.owners)


@register(PaymentReceipt)
class PaymentReceiptAdmin(ModelAdmin):
    list_display = ['__str__', 'number', 'display_receipt_year',
                    'display_value', 'display_payments', 'display_total_expected',
                    'display_spots', 'display_payments_years',
                    'display_owners']

    list_filter = rev(['number', 'year', 'value',
                       'payments__spot', 'payments__spot__parcel', 'payments__spot__row', 'payments__spot__column',
                       'payments__spot__deeds__owners'])

    search_fields = ['number', 'year', 'value',
                     'payments__spot__parcel', 'payments__spot__row', 'payments__spot__column',
                     'payments__spot__deeds__owners__name']

    form = PaymentReceiptForm

    def get_queryset(self, request):
        qs = super(PaymentReceiptAdmin, self).get_queryset(request)
        return qs.annotate(first_payment=Min('payments'),
                           first_spot=Min('payments__spot'),
                           first_owner=Min('payments__spot__deeds__owners'),
                           # first payment-year not the year in which the first payment was made
                           first_payment_year=Min('payments__year'))

    @short(desc='Payments', order='first_payment', tags=True)
    def display_payments(self, receipt):
        return display_head_links(receipt.payments)

    @short(desc='Receipt Year', order='year')
    def display_receipt_year(self, receipt):
        return receipt.year

    @short(desc='Paid', order='value')
    def display_value(self, receipt):
        return receipt.value

    @short(desc='Total Expected', order='payments_sum')
    def display_total_expected(self, receipt):
        return receipt.total_expected

    @short(desc='Spots', order='first_spot', tags=True)
    def display_spots(self, receipt):
        return display_head_links(receipt.spots)

    @short(desc='Payments Years', order='first_payment_year')
    def display_payments_years(self, receipt):
        return ', '.join(map(str, receipt.payments_years.all()))

    @short(desc='Owners', order='first_owner', tags=True)
    def display_owners(self, receipt):
        return display_head_links(receipt.owners)


"""
Maintenance
"""

@register(Maintenance)
class MaintenanceAdmin(ModelAdmin):
    list_display = ['__str__', 'year', 'display_spot', 'kept',
                    'display_owners']

    list_filter = rev(['year', 'kept',  # TODO how to search by boolean (kept)?
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

    def get_urls(self):
        urls = super(MaintenanceAdmin, self).get_urls()
        custom_url = url(r'^test_view/$',
                         self.admin_site.admin_view(self.test_view),
                         name='add_bulk')
        return [custom_url] + urls

    def test_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'form': MaintenanceBulkForm
        }
        return TemplateResponse(request, 'admin/cemetery/maintenance/add_bulk.html', context)

    @short(desc='Spot', order='spot')
    def display_spot(self, maintenance):
        return display_change_link(maintenance.spot)

    @short(desc='Owners', order='first_owner', tags=True)
    def display_owners(self, maintenance):
        return display_head_links(maintenance.owners)

    @short(desc='Mark selected entries as kept')
    def mark_kept(self, request, queryset):
        n_updated = queryset.update(kept=True)

        if n_updated == 1:
            prefix = '1 entry was'
        else:
            prefix = f'{n_updated} entries were'
        self.message_user(request, prefix + ' successfully marked as kept',
                          level=SUCCESS)

    @short(desc='Mark selected entries as unkept')
    def mark_unkept(self, request, queryset):
        n_updated = queryset.update(kept=False)

        if n_updated == 1:
            prefix = '1 entry was'
        else:
            prefix = f'{n_updated} entries were'
        self.message_user(request, prefix + ' successfully marked as unkept',
                          level=SUCCESS)
