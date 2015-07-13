import operator
from .view_utils import *
from .models import *

#
# Spot detail
#


pass


#
# Annual tables
#


def spots_with_attribute_date_comparison_year(attribute, comparison, year):
    """
    :param attribute: ownership_deeds, construction_authorizations etc
    :param comparison: ==, <= etc
    :param year: what to compare date of the attribute to
    :return: list of spots
    """
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '=': operator.eq,
           '==': operator.eq,
           '!=': operator.ne}
    comp = ops[comparison]

    spts = []
    for spot in Spot.objects.all():
        for attr in getattr(spot, attribute).all():
            if comp(attr.date.year, year):
                spts.append(spot)
                break
    return spts


#
# Ownerships
#


def ownership_data(spot, year):
    deed = spot.most_recent_deed_up_to(year)
    return ownership_data_from_deed(spot, deed)


def ownership_data_from_deed(spot, deed):
    # receipts ordered by most recent
    receipts = deed.receipts.order_by('-date').all()
    receipts_disp = ', '.join(str(r) for r in receipts)

    owners = deed.owners.all()

    # other owners on the same deed
    others = list(deed.spots.all())
    others.remove(spot)
    others_disp = ', '.join([str(o) for o in others])

    return [owners_to_names(owners), phones_if_any(owners), str(deed), receipts_disp, others_disp]


def phones_if_any(owners):
    """
    :param: owners list of Owners
    :return: comma separated phone numbers. if there are none, a dash instead
    """
    numbers = []
    for owner in owners:
        if owner.phone is not None:
            numbers.append(owner.phone_display())
    if len(numbers) > 0:
        return ', '.join(numbers)
    else:
        return '-'

#
# Constructions
#


def construction_data(spot, year):
    # working under the assumption that there can be only one authorization in a year for a spot
    auth = spot.construction_authorizations.get(date__year=year)
    return construction_data_from_auth(spot, auth)


def construction_data_from_auth(spot, auth, include_others=True):
    # constructions sorted by type
    constrs = auth.constructions.order_by('type')
    constrs_types = ', '.join([c.get_type_display() for c in constrs])

    constructors = [c.constructor() for c in constrs]

    data = [constrs_types, collapse_names(constructors), str(auth)]

    if include_others:
        others = list(auth.spots.all())
        others.remove(spot)
        others_info = ', '.join([str(s) for s in others])

        data.append(others_info)

    return data


#
# Operations
#

def operation_data(operation, year, include_year=False):
    data = [operation.first_name, operation.last_name, operation.get_type_display()]
    if include_year:
        data.append(operation.date.year)
    data.append(operation.note)
    return data


#
# Revenue
#


def payment_data_list(payment, include_year=False):
    data = []
    if include_year:
        data.append(payment.year)
    return data + [payment.value, str(payment.receipt)]


def payment_data(spot, year):
    try:
        payment = YearlyPayment.objects.filter(year=year).get(spot=spot)
        return payment_data_list(payment)
    # means it was not paid that year (but we know it was owned)
    except YearlyPayment.DoesNotExist:
        return [0, '-']


#
# Maintenance
#


def maintenance_to_owners(maintenance, year):
    # if there is than one deed change for a spot in a year, only the latest one will show
    deed = maintenance.spot.most_recent_deed_up_to(year)
    owners = deed.owners.order_by('last_name', 'first_name').all()
    return owners_to_names(owners)


def maintenance_data(maintenance, year):
    return [maintenance_to_owners(maintenance, year), maintenance.get_description_display()]