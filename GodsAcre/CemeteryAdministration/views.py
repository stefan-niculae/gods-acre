from django.shortcuts import render
from django.http import HttpResponse


def name_to_template(name):
    app_name = 'CemeteryAdministration'
    return '{0}/{1}.html'.format(app_name, name)


def index(request):
    return render(request, name_to_template('index'))


def general_register(request):
    return render(request, name_to_template('general_register'))


def spots(request):
    return render(request, name_to_template('spot'))


def spot_detail(request, spot_id):
    return render(request, name_to_template('spot_detail'), {'spot_id': spot_id, })


def ownerships(request):
    return render(request, name_to_template('ownerships'))


def constructions(request):
    return render(request, name_to_template('constructions'))


def operations(request):
    return render(request, name_to_template('operations'))


def revenue(request):
    return render(request, name_to_template('revenue'))


def maintentance(request):
    return render(request, name_to_template('maintenance'))


def administration(request):
    return render(request, name_to_template('administration'))
