# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from .view_contents import *
#from django_ajax.decorators import ajax

from django.http import HttpResponse
from simple_rest import Resource
import json
from datetime import date


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


def ownerships(request):
    return annual_table(
        request=request,
        name='ownerships',
        title='Concesiuni',
        table_headers=[TableHeader('Concesionari', 7), TableHeader('Telefoane', 5), TableHeader('Act', 2), TableHeader('Chitanțe', 3),
                       TableHeader('Pe același act', 3)],
        entites_filter=lambda year: spots_with_attribute_date_comparison_year('ownership_deeds', '==', year),
        entity_data=ownership_data
    )


def constructions(request):
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
    return render(request, 'payments.html')


class PaymentsAPI(Resource):

    @staticmethod
    # Read/Search
    def get(request):

        def query_value(key):
            return request.GET.get(key)

        payments = YearlyPayment.objects \
            .filter(spot__parcel__contains=query_value('parcel'),
                    spot__row__contains=query_value('row'),
                    spot__column__contains=query_value('column')) \
            .filter(year__contains=query_value('year'),
                    value__contains=query_value('value')) \
            .filter(receipt__number__contains=query_value('receiptNumber'),
                    # FIXME this tries to emulate receipt__date__year__contains=...
                    # but the default incoming parameter is zero
                    # and also it matches months and days as well
                    receipt__date__regex=query_value('receiptYear'))

        infos = []
        for p in payments:
            infos.append(
                {
                    'pk': p.id,
                    'fields': {
                        'parcel': p.spot.parcel,
                        'row': p.spot.row,
                        'column': p.spot.column,

                        'year': p.year,
                        'value': p.value,
                        'receiptNumber': p.receipt.number,
                        'receiptYear': p.receipt.date.year
                    }
                }
            )

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    def get_or_create_receipt(number, year):
        receipt_date = date.today() \
            .replace(year=int(year))
        (receipt, created_now) = ContributionReceipt.objects.get_or_create(
            number=number,
            date__year=year,
            defaults={'date': receipt_date}
        )
        return receipt

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot = Spot.objects.get(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column')
        )

        receipt = PaymentsAPI.get_or_create_receipt(
            number=query_value('receiptNumber'),
            year=query_value('receiptYear')
        )

        YearlyPayment.objects.create(
            year=query_value('year'),
            value=query_value('value'),
            spot=spot,
            receipt=receipt
        )

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, payment_id):

        def query_value(key):
            return request.PUT.get(key)

        payment = YearlyPayment.objects.get(pk=payment_id)
        payment.year = query_value('year')
        payment.value = query_value('value')

        payment.spot = Spot.objects.get(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column')
        )

        payments_on_receipt = len(YearlyPayment.objects
                                  .filter(receipt__id=payment.receipt.id))

        # If it's the only payment on the receipt
        if payments_on_receipt is 1:
            # Find if the receipt already exists
            try:
                payment.receipt = ContributionReceipt.objects.get(
                    number=query_value('receiptNumber'),
                    date__year=query_value('receiptYear')
                )
                payment.save()
                # This way we leak a receipt (it is linked to no payment now)

            # If it doesn't already exist, update this one
            except ContributionReceipt.DoesNotExist:
                payment.receipt.number = query_value('receiptNumber')
                payment.receipt.date.replace(year=int(query_value('receiptYear')))
                payment.receipt.save()

        # Other payments are on this receipt
        else:
            payment.receipt = PaymentsAPI.get_or_create_receipt(
                number=query_value('receiptNumber'),
                year=query_value('receiptYear')
            )
            payment.save()

        return HttpResponse(status=HTTP_200_OK)

    @staticmethod
    # Delete
    def delete(request, payment_id):
        payment = YearlyPayment.objects.get(pk=payment_id)
        payment.delete()

        return HttpResponse(status=HTTP_200_OK)


def burials(request):
    return render(request, 'burials.html')


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
            .filter(spot__parcel__contains=query_value('parcel'),
                    spot__row__contains=query_value('row'),
                    spot__column__contains=query_value('column')) \
            .filter(first_name__contains=query_value('firstName'),
                    last_name__contains=query_value('lastName'),
                    # FIXME same as above
                    date__regex=query_value('year'))

        # The operation type field can be left empty
        # And this way every type matches
        if query_value('type') != '':
            burials = burials.filter(type=query_value('type'))

        # Only filter by note if something is entered in that field
        # This is because None does not contain ''
        if query_value('note') != '':
            burials = burials.filter(note__contains=query_value('note'))

        infos = []
        for b in burials:
            infos.append(
                {
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
                    }
                }
            )

        json_infos = json.dumps(infos, default=lambda o: o.__dict__)
        return HttpResponse(json_infos, content_type='application/json', status=HTTP_200_OK)

    @staticmethod
    # Create
    def post(request):

        def query_value(key):
            return request.POST.get(key)

        spot = Spot.objects.get(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column')
        )

        burial_date = date.today().replace(
            year=int(query_value('year')))

        Operation.objects.create(
            spot=spot,
            date=burial_date,
            type=query_value('type'),
            first_name=query_value('firstName'),
            last_name=query_value('lastName'),
            note=query_value('note')
        )

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, burial_id):

        def query_value(key):
            return request.PUT.get(key)

        burial = Operation.objects.get(pk=burial_id)

        burial.spot = Spot.objects.get(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column')
        )

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
    return render(request, 'maintenance.html')


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
            .filter(spot__parcel__contains=query_value('parcel'),
                    spot__row__contains=query_value('row'),
                    spot__column__contains=query_value('column')) \
            .filter(year__contains=query_value('firstName'))

        if query_value('isKept') is not None:
            levels = levels.filter(description=bool_to_description(query_value('isKept')))


        infos = []
        for l in levels:
            owner = l.spot \
                .most_recent_deed_up_to(l.year) \
                .owners.all()[0]  # Chose a random owner as the representative
                # TODO should this be a list of owners?

            infos.append(
                {
                    'pk': l.id,
                    'fields': {
                        'parcel': l.spot.parcel,
                        'row': l.spot.row,
                        'column': l.spot.column,

                        'year': l.year,
                        'isKept': l.description == 'kept',

                        'firstName': owner.first_name,
                        'lastName': owner.last_name,
                    }
                }
            )

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

        spot = Spot.objects.get(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column')
        )

        MaintenanceLevel.objects.create(
            spot=spot,

            year=query_value('year'),
            description=MaintenanceAPI.description_from_query(query_value('isKept'))
        )

        return HttpResponse(status=HTTP_201_CREATED)

    @staticmethod
    # Update
    def put(request, level_id):

        def query_value(key):
            return request.PUT.get(key)

        level = MaintenanceLevel.objects.get(pk=level_id)

        level.spot = Spot.objects.get(
            parcel=query_value('parcel'),
            row=query_value('row'),
            column=query_value('column')
        )

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

