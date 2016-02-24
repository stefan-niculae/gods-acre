# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from .view_contents import *
#from django_ajax.decorators import ajax

from django.http import HttpResponse
from simple_rest import Resource
import json
from datetime import date
from django.db.models import Q


#TODO remove str(...) from here and instead, call str as as mapping in tests


def index(request):
    return render(request, name_to_template('index'))


def general_register(request):
    def join_constr_types(constrs):
        return ', '.join([c.get_type_display() for c in constrs])

    # todo dash if any of these is empty!!

    # todo search form (and pagination)
    rows = []
    for spot in Spot.objects.all():
        # todo check if there is no act (do it more efficiently and also treat it better)
        # get the most recent act
        deeds = []
        for d in OwnershipDeed.objects.order_by('-date'):
            if spot in d.spots.all():
                deeds.append(d)

        if len(deeds) > 0:
            deed = deeds[0]
        else:
            break
        owners = deed.owners.all()
        # todo refactor filtering to deed date into one thing
        opers = spot.operations.all().filter(date__gte=deed.date).order_by('-date')
        auths = []
        # todo models order... so that you don't have to write order_by for everything
        for auth in ConstructionAuthorization.objects.filter(date__gte=deed.date).order_by('-date'):
            if spot in auth.spots.all():
                auths.append(auth)

        # todo refactor this atrocity
        constr_types = [join_constr_types(Construction.objects.filter(construction_authorization=a)) for a in auths]

        row = [[spot.id], [spot.parcel], [spot.row], [spot.column],
               persons_to_names(owners, as_list=True), owners_to_phones(owners, as_list=True),  # todo align each phone with its owner
               [deed], deed.receipts.all(),
               persons_to_names(opers, as_list=True), ['{}{}'.format(o.date.year, o.get_type_display()[0]) for o in opers],
               # todo preference bordura, cavou 1/2001 or bordura 1/2001, cavou 1/2001 on different lines
               constr_types, auths,
               [last_paid(spot, deed)],
               [', '.join([str(year_to_shortcut(y)) for y in unkept_years(spot, deed)])]
               ]
        rows.append(row)

    context = {
        'title': 'Registru General',
        'rows': rows
    }
    return render(request, name_to_template('general_register'), context)


def spots(request):
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    # todo prettify 404 page
    spot = get_object_or_404(Spot, pk=spot_id)

    # todo notice when one of these is empty!!!
    # todo highlight latest item in each category
    deeds = []
    # todo check whether there should be an order by every time *.objects is called
    for deed in OwnershipDeed.objects.order_by('-date'):
        if spot in deed.spots.all():
            deeds.append(deed)
    owners = [ownership_data_from_deed(spot, d) for d in deeds]

    opers = [operation_data(o, None, include_year=True) for o in Operation.objects.filter(spot=spot).order_by('-date')]

    pays = YearlyPayment.objects.filter(spot=spot).order_by('-year')
    payments = [payment_data_list(p, include_year=True) for p in pays]

    auths = []
    for auth in ConstructionAuthorization.objects.order_by('-date'):
        if spot in auth.spots.all():
            auths.append(auth)
    constrs = [construction_data_from_auth(spot, a, include_others=False) for a in auths]

    oldest_deed = deeds[-1]

    context = {
        'title': 'Fișă Individuală (istoric)',
        'spot': spot,
        'owners': owners,
        'operations': opers,
        'payments': payments,
        'last_year_paid': last_paid(spot),
        'constructions': constrs,
        'unkept_years': unkept_years(spot, oldest_deed)
    }
    return render(request, name_to_template('spot_detail'), context)


#
# Annual tables
#


def annual_table(request, title, name, table_headers, entites_filter, entity_data):
    """
    :param request: http request
    :param title: external page title and header (showed on the page)
    :param name: internal page name (used in form submission)
    :param table_headers: list containing TableHeaders (not including spot headers)
    :param entites_filter: function that takes year as an argument and returns a query set of apropriate entities
    :param entity_data: function that takes an entity and returns list of data about it (not including spot identifiers)
    :return: render of the completed template
    """

    def spot_identif(ent):
        if hasattr(ent, 'spot'):
            return ent.spot.identif()
        elif hasattr(ent, 'remote_spot'):
            return ent.remote_spot().identif()
        else:
            return ent.identif()

    table_headers = spot_headers() + table_headers

    # text max length is 7 times each column width
    max_data_widths = list(map(lambda x: int(x.width * 7), table_headers))

    # show the form and/or extract the years from it
    form = years_form(request)
    years = years_list(form)

    # build a table for each year in the list
    tables = []
    for year in years:
        # get the entities corresponding to that year
        entities = entites_filter(year)
        rows = []
        for entity in entities:
            # show the data for each entitiy
            rows.append(spot_identif(entity) +
                        entity_data(entity, year))
        tables.append(Table(year, rows))

    context = {
        'template_name': name_to_template(name, html=False),
        'title': title,
        'years_form': form,
        'max_data_widths': max_data_widths,
        'table_headers': table_headers,
        'tables': tables
    }
    return render(request, name_to_template(name, html=True), context)


def ownerships_old(request):
    return annual_table(
        request=request,
        name='ownerships',
        title='Concesiuni',
        table_headers=[TableHeader('Concesionari', 7), TableHeader('Telefoane', 5), TableHeader('Act', 2), TableHeader('Chitanțe', 3),
                       TableHeader('Pe același act', 3)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '==', year),
        entity_data=ownership_data
    )


def constructions_old(request):
    return annual_table(
        request=request,
        name='constructions',
        title='Construcții',
        table_headers=[TableHeader('Tip', 2), TableHeader('Constructor', 8), TableHeader('Autorizațe', 2),
                       TableHeader('Pe aceeași autorizațe', 8)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('construction_authorizations', '==', year),
        entity_data=construction_data,
    )


def operations(request):
    return annual_table(
        request=request,
        name='operations',
        title='Înhumări',
        table_headers=person_headers(4, 4) + [TableHeader('Tip', 2), TableHeader('Notă', 10)],
        entites_filter=lambda year: Operation.objects.filter(date__year=year),
        entity_data=operation_data
    )


def revenue(request):
    return annual_table(
        request=request,
        name='revenue',
        title='Încasări',
        table_headers=[TableHeader('Valoare', 10), TableHeader('Chitanță', 10)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '<=', year),
        entity_data=payment_data
    )


def maintentance_old(request):
    return annual_table(
        request=request,
        name='maintenance',
        title='Întreținere',
        table_headers=[TableHeader('Concesionari', 16), TableHeader('Nivel întreținere', 4)],
        entites_filter=lambda year: MaintenanceLevel.objects.filter(year=year),
        entity_data=maintenance_data
    )


#
# Administration
#


def administration(request):
    table_headers = ['#', 'Parcela', 'Rand', 'Loc']
    row1 = ['1', '1a', '1', '1bis']
    row2 = ['2', '2a', '100', '3']
    row3 = ['3', '5a', '67', '1B']
    table_rows = [row1, row2, row3]
    context = {
        'table_headers': table_headers,
        'table_rows': table_rows,
    }
    return render(request, name_to_template('administration'), context)


# Used to identify the field name when sending back from the front-end
class TraceableData:
    def __init__(self, entity, db_id, field, data):
        self.entity = entity
        self.field = field
        self.db_id = db_id
        self.data = data


def spots_administration(request):
    headers = ['#', 'Parcela', 'Rand', 'Loc', 'Nota']
    fields = ['id', 'parcel', 'row', 'column', 'note']
    rows = []
    for spot in Spot.objects.all():
        row = [TraceableData('Spot', spot.id, field, getattr(spot, field)) for field in fields]
        rows.append(row)

    context = {
        'title': 'Administrare locuri de veci',
        'headers': headers,
        'rows': rows,
    }
    return render(request, name_to_template('spots_administration'), context)


def companies_administration(request):
    headers = ['Nume']
    fields = ['name']
    rows = []
    for company in ConstructionCompany.objects.all():
        row = [TraceableData('ConstructionCompany', company.id, field, getattr(company, field)) for field in fields]
        rows.append(row)

    context = {
        'title': 'Administrare companii de constructii',
        'headers': headers,
        'rows': rows,
    }
    return render(request, name_to_template('spots_administration'), context)


# @ajax
# def save(request):
#     entity  = request.POST.get('entity',    'NO ENTITY')
#     db_id   = request.POST.get('db_id',     'NO ID')
#     field   = request.POST.get('field',     'NO FIELD')
#     data    = request.POST.get('data',      'NO DATA')
#
#     try:
#         obj = globals()[entity].objects.get(id=int(db_id))
#         setattr(obj, field, data)
#         obj.save()
#         return 'SUCCESS'
#     except:  # TODO check what exceptions this can throw
#         print('>' * 25, 'Error running update statement!')
#         return 'ERROR'


HTTP_200_OK = 200
HTTP_201_CREATED = 201


def payments(request):
    context = {
        'title': 'Incasari'
    }
    return render(request, 'payments.html', context)


def date_from_year(year):
    year = int(year)
    # Because no day/month info was provided, we use the day of entry instead
    return date.today().replace(year=year)


# TODO move APIs to a different file
class PaymentsAPI(Resource):

    @staticmethod
    # Read/Search
    def get(request):

        def query_value(key):
            return request.GET.get(key)

        print '>'*25, r"Cast(Extract(Year From Date) As VarChar) LIKE '%" + query_value('receiptYear') + r"%'"

        payments = YearlyPayment.objects \
            .filter(spot__parcel__icontains=query_value('parcel'),
                    spot__row__icontains=query_value('row'),
                    spot__column__icontains=query_value('column')) \
            .filter(year__icontains=query_value('year'),
                    value__icontains=query_value('value')) \
            .filter(receipt__number__icontains=query_value('receiptNumber'))

        # Extra filter
        payments = filter(
            # Year contains query string
            lambda p: query_value('receiptYear') in str(p.receipt.date.year),
            payments)

        infos = []
        for p in payments:
            infos.append({
                'pk': p.id,
                'fields': {
                    'parcel': p.spot.parcel,
                    'row': p.spot.row,
                    'column': p.spot.column,

                    'year': p.year,
                    'value': p.value,
                    'receiptNumber': p.receipt.number,
                    'receiptYear': p.receipt.date.year
                }})

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    def get_or_create_receipt(number, year):
        receipt, created_now = ContributionReceipt.objects.get_or_create(
            number=number,
            date__year=year,
            defaults={'date': date_from_year(year)})
        return receipt

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        receipt = PaymentsAPI.get_or_create_receipt(
            number=query_value('receiptNumber'),
            year=query_value('receiptYear'))

        YearlyPayment.objects.create(
            year=query_value('year'),
            value=query_value('value'),
            spot=spot,
            receipt=receipt)

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, payment_id):

        def query_value(key):
            return request.PUT.get(key)

        payment = YearlyPayment.objects.get(pk=payment_id)
        payment.year = query_value('year')
        payment.value = query_value('value')

        payment.spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        payments_on_receipt = len(YearlyPayment.objects
                                  .filter(receipt__id=payment.receipt.id))

        # If it's the only payment on the receipt
        if payments_on_receipt is 1:
            # Find if the receipt already exists
            try:
                old_receipt = payment.receipt
                payment.receipt = ContributionReceipt.objects.get(
                    number=query_value('receiptNumber'),
                    date__year=query_value('receiptYear'))
                payment.save()

                # This way we don't leak a receipt (linked to no payment)
                old_receipt.delete()

            # If it doesn't already exist, update this one
            except ContributionReceipt.DoesNotExist:
                payment.receipt.number = query_value('receiptNumber')
                payment.receipt.date.replace(year=int(query_value('receiptYear')))
                payment.receipt.save()

        # Other payments are on this receipt
        else:
            payment.receipt = PaymentsAPI.get_or_create_receipt(
                number=query_value('receiptNumber'),
                year=query_value('receiptYear'))
            payment.save()

        return HttpResponse(status=HTTP_200_OK)

    @staticmethod
    # Delete
    def delete(request, payment_id):
        payment = YearlyPayment.objects.get(pk=payment_id)
        payment.delete()

        return HttpResponse(status=HTTP_200_OK)


def burials(request):
    context = {
        'title': 'Inhumari'
    }
    return render(request, 'burials.html', context)


class BurialsAPI(Resource):

    @staticmethod
    # Read/Search
    def get(request):
        # TODO don't let a person that is already buried be buried again
        # ?or exhumate an unburied person
        # ?and make sure the spot is empty before adding a burial

        def query_value(key):
            return request.GET.get(key)

        burials = Operation.objects \
            .filter(spot__parcel__icontains=query_value('parcel'),
                    spot__row__icontains=query_value('row'),
                    spot__column__icontains=query_value('column')) \
            .filter(first_name__icontains=query_value('firstName'),
                    last_name__icontains=query_value('lastName'))

        # The operation type field can be left empty
        # And this way every type matches
        if query_value('type') != '':
            burials = burials.filter(type=query_value('type'))

        # Only filter by note if something is entered in that field
        # This is because None does not contain ''
        if query_value('note') != '':
            burials = burials.filter(note__icontains=query_value('note'))

        # Year contains
        burials = filter(
            lambda b: query_value('year') in str(b.date.year),
            burials)

        infos = []
        for b in burials:
            infos.append({
                'pk': b.id,
                'fields': {
                    'parcel': b.spot.parcel,
                    'row': b.spot.row,
                    'column': b.spot.column,

                    'firstName': b.first_name,
                    'lastName': b.last_name,
                    'type': b.type,
                    'year': b.date.year,
                    'note': b.note
                }})

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        Operation.objects.create(
            spot=spot,
            date=date_from_year(query_value('year')),
            type=query_value('type'),
            first_name=query_value('firstName'),
            last_name=query_value('lastName'),
            note=query_value('note'))

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, burial_id):

        def query_value(key):
            return request.PUT.get(key)

        burial = Operation.objects.get(pk=burial_id)

        burial.spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        burial.type = query_value('type')
        burial.first_name = query_value('firstName')
        burial.last_name = query_value('lastName')
        burial.note = query_value('note')

        burial.save()

        return HttpResponse(status=HTTP_200_OK)

    @staticmethod
    # Delete
    def delete(request, burial_id):
        burial = Operation.objects.get(pk=burial_id)
        burial.delete()

        return HttpResponse(status=HTTP_200_OK)


def maintenance(request):
    context = {
        'title': 'Intretinere'
    }
    return render(request, 'maintenance.html', context)


class MaintenanceAPI(Resource):

    @staticmethod
    # Read/Search
    def get(request):
        # TODO make sure the spot has an owner in the time the maintenance level is recorded

        def query_value(key):
            return request.GET.get(key)

        def bool_to_description(s):
            return 'kept' if bool(s) else 'ukpt'

        levels = MaintenanceLevel.objects \
            .filter(spot__parcel__icontains=query_value('parcel'),
                    spot__row__icontains=query_value('row'),
                    spot__column__icontains=query_value('column')) \
            .filter(year__icontains=query_value('year'))
        # Can't prefetch related spot owners

        # Error: Relation fields do not support nested lookups
        # .filter(spot__owners__first_name__icontains=query_value('firstName'),
        #         spot__owners__last_name__icontains=query_value('lastName'))

        # Filter by kept status if query is present
        if query_value('isKept') is not None:
            levels = levels.filter(description=bool_to_description(query_value('isKept')))


        infos = []
        for l in levels:
            owners = l.spot \
                .most_recent_deed_up_to(l.year) \
                .owners.filter(
                    first_name__icontains=query_value('firstName'),
                    last_name__icontains=query_value('lastName'))

            # Skip this maintenance level if none of the owners match the filter
            if not owners.exists():
                continue

            infos.append({
                'pk': l.id,
                'fields': {
                    'parcel': l.spot.parcel,
                    'row': l.spot.row,
                    'column': l.spot.column,

                    'year': l.year,
                    'isKept': l.description == 'kept',

                    'firstName': owners[0].first_name,  # Chose a random owner as the representative
                    'lastName': owners[0].last_name,  # TODO should this be a list of owners?
                }})

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    def description_from_query(s):
        if s == 'true':
            return 'kept'
        return 'ukpt'

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        MaintenanceLevel.objects.create(
            spot=spot,
            year=query_value('year'),
            description=MaintenanceAPI.description_from_query(query_value('isKept')))

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, level_id):

        def query_value(key):
            return request.PUT.get(key)

        level = MaintenanceLevel.objects.get(pk=level_id)

        level.spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        level.year = query_value('year')
        level.description = MaintenanceAPI.description_from_query(query_value('isKept'))

        level.save()

        return HttpResponse(status=HTTP_200_OK)

    @staticmethod
    # Delete
    def delete(request, level_id):
        level = MaintenanceLevel.objects.get(pk=level_id)
        level.delete()

        return HttpResponse(status=HTTP_200_OK)


def ownerships(request):
    context = {
        'title': 'Concesiuni'
    }
    return render(request, 'ownerships.html', context)


class OwnershipsAPI(Resource):

    @staticmethod
    # Read/Search
    def get(request):

        def query_value(key):
            return request.GET.get(key)

        deeds = OwnershipDeed.objects.all() \
            .filter(number__icontains=query_value('deedNumber')) \
            .prefetch_related('spots', 'owners', 'ownershipreceipt')  # We need additional data for each deed

        deeds = filter(
            lambda d: query_value('deedYear') in str(d.date),
            deeds)

        infos = []
        for d in deeds:
            # We do the filtering here and not in the main query
            # because we want only entries where the parcel (ie) matches,
            # not spots that are on a deed with a spot where the parcel matches
            spots = d.spots \
                .filter(parcel__icontains=query_value('parcel'),
                        row__icontains=query_value('row'),
                        column__icontains=query_value('column'))

            if not spots.exists():
                continue

            owners = d.owners \
                .filter(first_name__icontains=query_value('firstName'),
                        last_name__icontains=query_value('lastName'))

            # Filter by phone only if a phone number is entered
            # Because None does not contain ''
            if query_value('phone') != '':
                owners = owners.filter(
                    phone__icontains=query_value('phone'))

            if not owners.exists():
                continue

            receipts = d.receipts \
                .filter(number__icontains=query_value('receiptNumber'),
                        value__icontains=query_value('receiptValue'))
            receipts = filter(
                lambda r: query_value('receiptYear') in str(r.date),
                receipts)

            if not receipts:
                continue

            for s in spots:
                # Get the display string of every spot that is not the current one
                other_spots = [os.display_string() for os in spots if os != s]

                o = owners[0]  # Chose a random representative owner
                r = receipts[0]  # Chose a random representative receipt

                infos.append({
                    'pk': '%d,%d' % (d.id, r.id),
                    'fields': {
                        'parcel': s.parcel,
                        'row': s.row,
                        'column': s.column,

                        'firstName': o.first_name,   # TODO list of owners?
                        'lastName': o.last_name,
                        'phone': o.phone,  # TODO see if any of the owners have a phone nr

                        'deedNumber': d.number,
                        'deedYear': d.date.year,

                        'receiptNumber': r.number,  # TODO list of receipts?
                        'receiptYear': r.date.year,
                        'receiptValue': r.value,

                        'sharingSpots': ', '.join(other_spots)  # TODO handle way of displaying on frontend?
                    }})

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    def none_if_empty(s):
        return None if s == '' else s

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        owner, created_now = Owner.objects.get_or_create(
            first_name=query_value('firstName'),
            last_name=query_value('lastName'),
            phone=OwnershipsAPI.none_if_empty(query_value('phone')))

        deed, created_now = OwnershipDeed.objects.get_or_create(
            number=query_value('deedNumber'),
            date=date_from_year(query_value('deedYear')))
        deed.spots.add(spot)
        deed.save()

        owner.ownership_deeds.add(deed)
        owner.save()

        OwnershipReceipt.objects.get_or_create(
            number=query_value('receiptNumber'),
            date=date_from_year(query_value('receiptYear')),
            value=query_value('receiptValue'),
            ownership_deed=deed)

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, deed_id, receipt_id):

        def query_value(key):
            return request.PUT.get(key)

        deed = OwnershipDeed.objects.get(pk=deed_id)
        deed.number = query_value('deedNumber')  # TODO set validator to see if there is already a deed with this nr/yr
        deed.date = date_from_year(query_value('deedYear'))

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))
        deed.spots.add(spot)  # It's ok if it already exists

        # If the old owner has no other deeds, it will remain leaking
        owner, created_now = Owner.objects.get_or_create(
            first_name=query_value('firstName'),
            last_name=query_value('lastName'),
            phone=OwnershipsAPI.none_if_empty(query_value('phone')))
        deed.owners.add(owner)
        deed.save()

        try:
            # Check if the entered receipt already exits
            OwnershipReceipt.objects.get(
                number=query_value('receiptNumber'),
                date__year=query_value('receiptYear'))
            # If so, delete the old one
            OwnershipReceipt.objects.get(pk=receipt_id).delete()

        except OwnershipReceipt.DoesNotExist:
            # If the receipt does not exist, edit the old one
            receipt = OwnershipReceipt.objects.get(pk=receipt_id)
            receipt.number = query_value('receiptNumber')
            receipt.date = date_from_year(query_value('receiptYear'))
            receipt.value = query_value('receiptValue')
            receipt.save()

        return HttpResponse(status=HTTP_200_OK)

    @staticmethod
    # Delete
    def delete(request, deed_id, receipt_id):
        deed = OwnershipDeed.objects.get(pk=deed_id)
        deed.delete()  # Any receipts will be cascade-deleted as well
        # If this was the owner's only deed, it will remain leaking

        return HttpResponse(status=HTTP_200_OK)


def constructions(request):
    context = {
        'title': 'Constructii'
    }
    return render(request, 'constructions.html', context)


class ConstructionsAPI(Resource):

    @staticmethod
    # Read/Search
    def get(request):

        def query_value(key):
            return request.GET.get(key)

        constructions = Construction.objects \
            .filter(construction_authorization__number__icontains=query_value('authorizationNumber')) \
            .filter(Q(owner_builder__first_name__icontains=query_value('builder')) |
                    Q(owner_builder__last_name__icontains=query_value('builder')) |
                    Q(construction_company__name__icontains=query_value('builder')))

        # The operation type field can be left empty ... this way every type matches
        # TODO refactor this into a reusable function
        if query_value('constructionType') != '':
            constructions = constructions.filter(type=query_value('constructionType'))

        constructions = filter(
            lambda c: query_value('authorizationYear') in str(c.construction_authorization.date),
            constructions)

        infos = []
        for c in constructions:
            a = c.construction_authorization

            spots = a.spots \
                .filter(parcel__icontains=query_value('parcel'),
                        row__icontains=query_value('row'),
                        column__icontains=query_value('column'))
            if not spots.exists():
                continue

            for s in spots:
                other_spots = [os.display_string() for os in spots if os != s]

                infos.append({
                    'pk': '%d,%d,%d' % (c.id, a.id, s.id),
                    'fields': {
                        'parcel': s.parcel,
                        'row': s.row,
                        'column': s.column,

                        'constructionType': c.type,
                        'builder': c.constructor(),

                        'authorizationNumber': a.number,
                        'authorizationYear': a.date.year,
                        'sharingAuthorization': ', '.join(other_spots)
                    }})

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    def get_or_create_authorization(number, year):
        authorization, created_now = ConstructionAuthorization.objects.get_or_create(
            number=number,
            date__year=year,
            defaults={'date': date_from_year(year)})
        return authorization

    @staticmethod
    def owner_and_company_builders(name):
        owner_builder = None
        company = None

        # Warning: this way, a new owner can't be created (he has to be added from the ownership page instead)
        owners = filter(
            lambda o: o.full_name() == name,
            Owner.objects.all())

        if not owners:
            # TODO show warning when creating a company (maybe it is a misspelled owner name)
            company, created_now = ConstructionCompany.objects.get_or_create(name=name)
        else:
            # TODO show a warning if there are multiple owners by the same name
            # This is to get the case when there are multiple owners with the same full name
            owner_builder = owners[0]

        return owner_builder, company

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))

        owner_builder, company = ConstructionsAPI.owner_and_company_builders(query_value('builder'))

        authorization = ConstructionsAPI.get_or_create_authorization(
            query_value('authorizationNumber'),
            query_value('authorizationYear'))
        authorization.spots.add(spot)
        authorization.save()

        print '{0} \nspot = {1}, \nowner_builder = {2}, \ncompany = {3}, \nauthorization = {4}'.format('-'*50, spot, owner_builder, company, authorization)

        Construction.objects.create(
            # TODO warn if there is already a construction of the same type on this spot
            type=query_value('constructionType'),
            owner_builder=owner_builder,
            construction_company=company,
            construction_authorization=authorization)

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, construction_id, authorization_id, spot_id):
        # TODO there is the issue of updating the type on one spot
        # and when the page is refreshed, the type will be refreshed on all spots sharing the authorization
        # that's because there is not a direct link from construction to spot, only one through authorization

        # TODO look into the other APIs and see if we did the mistake of removing the newly entered spot/something else
        # instead of removing the old one (which should be transmitted by id)
        def query_value(key):
            return request.PUT.get(key)
        # TODO look into the other APIs and see if we did the mistake of only getting the model instead of get_or_crate
        # when there are other models being edited
        construction = Construction.objects.get(pk=construction_id)
        construction.type = query_value('constructionType')

        owner_builder, company = ConstructionsAPI.owner_and_company_builders(query_value('builder'))
        construction.owner_builder = owner_builder
        construction.construction_company = company

        spot, created_now = Spot.objects.get_or_create(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column'))
        old_spot = Spot.objects.get(pk=spot_id)

        authorization = ConstructionsAPI.get_or_create_authorization(
            query_value('authorizationNumber'),
            query_value('authorizationYear'))
        authorization.spots.add(spot)
        authorization.save()

        old_authorization = ConstructionAuthorization.objects.get(pk=authorization_id)
        construction.construction_authorization = authorization  # We set this now because its authorization
        construction.save()

        # On update of either spot or authorization
        if authorization != old_authorization or spot != old_spot:
            # Remove the spot from the authorization
            old_authorization.spots.remove(old_spot)
            old_authorization.save()

            # Delete the old authorization has no other spots
            if authorization != old_authorization and old_authorization.spots.count() == 0:
                old_authorization.delete()

        return HttpResponse(status=HTTP_200_OK)

    @staticmethod
    # Delete
    def delete(request, construction_id, authorization_id, spot_id):
        spot = Spot.objects.get(pk=spot_id)

        # TODO Upon deletion, warn the user that the spot will be removed from the authorization
        # This means rows with this spot and this authorization will be ALL removed
        # update this visually as well
        authorization = ConstructionAuthorization.objects.get(pk=authorization_id)
        authorization.spots.remove(spot)
        # Delete the authorization if it has no other spots
        if authorization.spots.count() == 0:
            # Constructions will be deleted when their authorization is removed
            authorization.delete()

        return HttpResponse(status=HTTP_200_OK)
