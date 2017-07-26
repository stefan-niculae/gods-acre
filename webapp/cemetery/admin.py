from datetime import date
from math import fabs

from django.utils.translation import pgettext_lazy, ugettext_lazy as _

from django.contrib.admin import ModelAdmin, register, site
from django.db.models import Min, Case, When, Max
from django.contrib.messages import SUCCESS, WARNING
from easy import short, SimpleAdminField as Field

from .models import Spot, Deed, OwnershipReceipt, Owner, Maintenance, Operation, PaymentUnit, PaymentReceipt, \
    Construction, Authorization, Company
from .forms import SpotForm, DeedForm, OwnerForm, AuthorizationForm, PaymentReceiptForm, CompanyForm, OperationForm, \
    PaymentUnitForm, MaintenanceForm, OwnershipReceiptForm
from .inlines import OwnershipReceiptInline, MaintenanceInline, OperationInline, ConstructionInline, \
    AuthorizationInline, PaymentUnitInline
from .utils import rev, all_equal
from .display_helpers import entity_tag, show_head_links, truncate, show_date, year_to_shorthand
from django.utils.safestring import mark_safe


DISTANT_DATE_THRESHOLD = 10  # year(s)

"""
Site
"""

site.site_header = _("God's Acre")  # in the menus
site.site_title  = _("God's Acre")  # in the tab's title
site.index_title = _("Cemetery Administration")  # in the tab's title, for the home page
site.site_url = None  # remove the "View Site" link


"""
Composables
"""

class CustomModelAdmin(ModelAdmin):
    class Media:
        css = {
            # HACK
            'all': ['remove-second-breadcrumb.css']
        }


class NrYearAdmin(CustomModelAdmin):
    def save_model(self, request, entity, form, change):
        # difference = entity.date - date.today()   # in days
        # years = distance / 365.25
        years = entity.year - date.today().year
        distance = int(fabs(years))
        if distance > DISTANT_DATE_THRESHOLD:
            entity_link = entity_tag(entity)
            message = _(f'For {entity_link}, the year ({entity.year}) is distant: {distance} years from today')
            self.message_user(request, _(mark_safe(message)), WARNING)
        entity.save()


"""
Spot
"""

@register(Spot)
class SpotAdmin(CustomModelAdmin):
    # What columns the list-view has
    list_display = ['__str__', 'show_parcel', 'show_row', 'show_column',
                    'show_active_deed',
                    'show_shares_deed_with',
                    'show_owners',
                    'show_operations',
                    'show_constructions',
                    'show_shares_authorizations_with',
                    'show_last_paid_year',
                    'show_unkept_since']

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

    show_parcel = Field(lambda s: s.parcel, 'P', admin_order_field='parcel')
    show_row    = Field(lambda s: s.row,    'R', admin_order_field='row')
    show_column = Field(lambda s: s.column, 'C', admin_order_field='column')

    show_active_deed   = Field(lambda s: show_head_links(s.active_deeds, 1),     _('Active Deed'),   'first_active_deed',    True)
    show_owners        = Field(lambda s: show_head_links(s.active_owners),       _('Active Owners'), 'first_active_owner',   True)
    show_operations    = Field(lambda s: show_head_links(s.operations, 1),       _('Operations'),    'first_operation',      True)
    show_constructions = Field(lambda s: show_head_links(s.constructions, 1),    _('Constructions'), 'first_construction',   True)

    show_shares_deed_with = Field(lambda s: show_head_links(s.shares_deed_with), _('Sharing Deed'),                          allow_tags=True)
    show_last_paid_year   = Field(lambda s: s.last_paid_year,                    _('Last Paid'),     'max_payments_year')
    show_unkept_since     = Field(lambda s: s.unkept_since,                      _('Unkept Since'))
    show_shares_authorizations_with = Field(lambda s: show_head_links(s.shares_authorization_with), _('Sharing Auth.'),      allow_tags=True)

    def save_model(self, request, spot, form, change):
        if spot.active_deeds.count() > 1:
            spot_link = entity_tag(spot)
            deeds_links = show_head_links(spot.active_deeds, head_length=0)
            message = _(f'This spot ({spot_link}) has more than one active deed: {deeds_links}')
            self.message_user(request, _(mark_safe(message)), WARNING)
        spot.save()


"""
Ownership
"""

@register(Deed)
class DeedAdmin(NrYearAdmin):
    list_display = ['show_repr', 'number', 'year', 'cancel_reason',
                    'show_spots', 'show_receipts', 'show_owners']

    list_filter = rev(['number', 'year', 'cancel_reason',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column',
                       'owners',
                       'receipts'])

    search_fields = ['number', 'year', 'cancel_reason',
                     'spots__parcel', 'spots__row', 'spots__column',
                     'owners__name',
                     'receipts__number', 'receipts__year']

    form = DeedForm
    inlines = [OwnershipReceiptInline]

    def get_queryset(self, request):
        qs = super(DeedAdmin, self).get_queryset(request)
        return qs.annotate(first_spot=Min('spots'),
                           first_receipt=Min('receipts'),
                           first_owner=Min('owners'))

    show_repr     = Field(lambda d: str(d),                      pgettext_lazy('short', 'Deed'))
    show_spots    = Field(lambda d: show_head_links(d.spots),    _('Spots'),                    'first_spot',    True)
    show_receipts = Field(lambda d: show_head_links(d.receipts), _('Receipts'),                 'first_receipt', True)
    show_owners   = Field(lambda d: show_head_links(d.owners),   _('Owners'),                   'first_owner',   True)

    # TODO: check if any of the deed's spots have more than one active deed

@register(OwnershipReceipt)
class OwnershipReceiptAdmin(NrYearAdmin):
    list_display = ['show_repr', 'number', 'year', 'value',
                    'show_deed', 'show_spots', 'show_owners']

    list_filter = rev(['number', 'year', 'value',
                       'deed',
                       'deed__spots', 'deed__spots__parcel', 'deed__spots__row', 'deed__spots__column'])

    search_fields = ['number', 'year', 'value',
                     'deed__year', 'deed__number',
                     'deed__spots__parcel', 'deed__spots__row', 'deed__spots__column']

    form = OwnershipReceiptForm

    def get_queryset(self, request):
        # http://stackoverflow.com/questions/2168475/django-admin-how-to-sort-by-one-of-the-custom-list-display-fields-that-has-no-d
        qs = super(OwnershipReceiptAdmin, self).get_queryset(request)
        # Out of all the spots for this receipt's deed,
        # get the minimum one (as defined by Spot::ordering).
        # Because that the order they are shown in the cell as well
        return qs.annotate(first_spot=Min('deed__spots'),
                           first_owner=Min('deed__owners'))

    show_repr   = Field(lambda r: str(r),                    _('Receipt'))
    show_deed   = Field(lambda r: entity_tag(r.deed),        pgettext_lazy('short', 'Deed'), 'deed',        True)
    show_spots  = Field(lambda r: show_head_links(r.spots),  _('Spots'),                     'first_spot',  True)
    show_owners = Field(lambda r: show_head_links(r.owners), _('Owners'),                    'first_owner', True)


@register(Owner)
class OwnerAdmin(CustomModelAdmin):
    list_display = ['name', 'show_phone', 'show_address', 'show_city',
                    'show_spots', 'show_deeds', 'show_receipts',
                    # 'show_constructions'
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

    show_address  = Field(lambda o: truncate(o.address),         _('Address'),                     'address')
    show_city     = Field(lambda o: truncate(o.city),            _('City'),                        'city')
    show_deeds    = Field(lambda o: show_head_links(o.deeds),    pgettext_lazy('short', 'Deeds'), 'first_deed',    True)
    show_receipts = Field(lambda o: show_head_links(o.receipts), _('Receipts'),                   'first_receipt', True)
    show_spots    = Field(lambda o: show_head_links(o.spots),    _('Spots'),                      'first_spot',    True)

    @short(desc=_('Phone'), order='phone')
    def show_phone(self, owner):
        if not owner.phone:
            return
        return f'{owner.phone[0:3]} {owner.phone[3:6]} {owner.phone[6:9]}'

    # @short(desc=_('Built'), order='first_construction', tags=True)
    # def show_constructions(self, owner):
    #     return show_head_links(owner.constructions_built)


"""
Operations
"""

@register(Operation)
class OperationAdmin(CustomModelAdmin):
    list_display = ['__str__', 'type', 'show_date', 'deceased', 'show_owner',
                    'show_spot', 'exhumation_written_report', 'remains_brought_from']

    date_hierarchy = 'date'

    list_filter = rev(['type', 'deceased', 'spot', 'exhumation_written_report', 'remains_brought_from',
                       'spot__parcel', 'spot__row', 'spot__column',
                       'spot__deeds__owners'])

    search_fields = ['type', 'date', 'deceased', 'note', 'exhumation_written_report', 'remains_brought_from',
                     'spot__parcel', 'spot__row', 'spot__column',
                     'spot__deeds__owners__name']

    form = OperationForm

    def get_queryset(self, request):
        qs = super(OperationAdmin, self).get_queryset(request)
        # FIXME only active owners
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    show_date  = Field(lambda o: show_date(o.date),                     _('Date'),  'date')
    show_owner = Field(lambda o: show_head_links(o.spot.active_owners), _('Owner'), 'first_owner', True)
    show_spot  = Field(lambda o: entity_tag(o.spot),                    _('Spot'),  'spot',        True)

    def save_model(self, request, entity, form, change):
        difference = entity.date - date.today()
        years = difference.days / 365.25
        distance = fabs(years)
        if distance > DISTANT_DATE_THRESHOLD:
            entity_link = entity_tag(entity)
            message = _(f'For {entity_link}, the date ({entity.date}) is distant: {distance:.1f} years from today')
            self.message_user(request, _(mark_safe(message)), WARNING)
        entity.save()


"""
Constructions
"""

@register(Authorization)
class AuthorizationAdmin(NrYearAdmin):
    list_display = ['__str__', 'number', 'year', 'show_spots', 'show_construction']

    list_filter = rev(['number', 'year',
                       'construction', 'construction__type',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column'])

    search_fields = ['number', 'year',
                     'construction__type',
                     'spots__parcel', 'spots__row', 'spots__column']

    form = AuthorizationForm

    show_spots        = Field(lambda authorization: show_head_links(authorization.spots),    _('Spots'),        'spots',        True)
    show_construction = Field(lambda authorization: entity_tag(authorization.construction),  _('Construction'), 'construction', True)  # in case you were wondering: yes, this was developed on an ultra-wide


@register(Construction)
class ConstructionAdmin(CustomModelAdmin):
    list_display = ['__str__', 'type', 'show_authorizations', 'show_spots',
                    'show_owner_builder', 'show_company']

    list_filter = rev(['type', 'owner_builder', 'company',
                       'spots', 'spots__parcel', 'spots__row', 'spots__column',
                       'authorizations'])

    search_fields = ['type', 'owner_builder__name', 'company__name',
                     'spots__parcel', 'spots__row', 'spots__column'
                     'authorizations__number', 'authorizations__year']

    # no custom form
    inlines = [AuthorizationInline]

    show_authorizations = Field(lambda c: show_head_links(c.authorizations), _('Authorizations'), 'authorizations',        True)
    show_spots          = Field(lambda c: show_head_links(c.spots),          _('Spots'),          'authorizations__spots', True)
    show_company        = Field(lambda c: entity_tag(c.company),             _('Owner Builder'),  'owner_builder',         True)
    show_owner_builder  = Field(lambda c: entity_tag(c.owner_builder),       _('Company'),        'company',               True)


@register(Company)
class CompanyAdmin(CustomModelAdmin):
    list_display = ['__str__', 'show_n_constructions', 'show_constructions']

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

    form = CompanyForm
    inlines = [ConstructionInline]

    show_n_constructions = Field(lambda c: c.n_constructions,                   _('#Constructions'))
    show_constructions   = Field(lambda c: show_head_links(c.constructions, 5), _('Constructions'), 'constructions', True)


"""
Payments
"""

@register(PaymentUnit)
class PaymentUnitAdmin(NrYearAdmin):
    list_display = ['__str__', 'year', 'show_spot', 'value',
                    'show_receipts',
                    'show_owners']

    list_filter = rev(['year', 'value',
                       'spot', 'spot__parcel', 'spot__row', 'spot__column',
                       'receipt', 'receipt__number', 'receipt__year',
                       'spot__deeds__owners'])

    search_fields = ['year', 'value',
                     'spot__parcel', 'spot__row', 'spot__column',
                     'receipt__number', 'receipt__year',
                     'spot__deeds__owners__name']

    form = PaymentUnitForm

    def get_queryset(self, request):
        qs = super(PaymentUnitAdmin, self).get_queryset(request)
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    show_spot     = Field(lambda p: entity_tag(p.spot),        _('Spot'),    'spot',        True)
    show_receipts = Field(lambda p: entity_tag(p.receipt),     _('Receipt'), 'receipt',     True)
    show_owners   = Field(lambda p: show_head_links(p.owners), _('Owners'),  'first_owner', True)


@register(PaymentReceipt)
class PaymentReceiptAdmin(NrYearAdmin):
    list_display = ['show_repr', 'number', 'show_receipt_year',
                    'show_total_value', 'show_spots', 'show_units_years',
                    'show_units',
                    'show_owners']

    list_filter = rev(['number', 'year',
                       'units__spot', 'units__spot__parcel', 'units__spot__row', 'units__spot__column',
                       'units__spot__deeds__owners'])

    search_fields = ['number', 'year',
                     'units__spot__parcel', 'units__spot__row', 'units__spot__column',
                     'units__spot__deeds__owners__name']

    form = PaymentReceiptForm
    inlines = [PaymentUnitInline]

    def get_queryset(self, request):
        qs = super(PaymentReceiptAdmin, self).get_queryset(request)
        return qs.annotate(first_unit=Min('units'),
                           first_spot=Min('units__spot'),
                           first_owner=Min('units__spot__deeds__owners'),
                           # first payment-year not the year in which the first unit was made
                           first_unit_year=Min('units__year'))

    show_repr         = Field(str,              pgettext_lazy('short', 'Receipt'))
    show_receipt_year = Field(lambda r: r.year, _('Receipt Year'), 'year')

    show_total_value  = Field(lambda r: r.total_value,                         _('Total Value'))
    show_spots        = Field(lambda r: show_head_links(r.spots.distinct()),  _('Spots'),     'first_spot',  True)
    show_units        = Field(lambda r: show_head_links(r.units),             _('Units'),     'first_unit',  True)
    show_owners       = Field(lambda r: show_head_links(r.owners.distinct()), _('Owners'),    'first_owner', True)

    @short(desc=_('Payment Year(s)'), order='first_unit_year')
    def show_units_years(self, receipt):
        years = receipt.units_years.all()
        if not years:
            return
        if all_equal(years):
            return year_to_shorthand(years[0])
        return ', '.join(map(year_to_shorthand, years))


"""
Maintenance
"""

@register(Maintenance)
class MaintenanceAdmin(NrYearAdmin):
    list_display = ['__str__', 'year', 'show_spot', 'kept',
                    'show_owners']

    list_filter = rev(['year', 'kept',
                       'spot', 'spot__parcel', 'spot__row', 'spot__column',
                       'spot__deeds__owners'])

    search_fields = ['year', 'kept',
                     'spot__parcel', 'spot__row', 'spot__column',
                     # FIXME DisallowedModelAdminLookup: Filtering by spot__deeds__owners__isnull not allowed
                     'spot__deeds__owners__name']

    form = MaintenanceForm
    actions = ['mark_kept', 'mark_unkept']

    def get_queryset(self, request):
        qs = super(MaintenanceAdmin, self).get_queryset(request)
        return qs.annotate(first_owner=Min('spot__deeds__owners'))

    show_spot   = Field(lambda m: entity_tag(m.spot),        _('Spot'),   'spot')
    show_owners = Field(lambda m: show_head_links(m.owners), _('Owners'), 'first_owner', True)

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
