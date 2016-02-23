from django.conf.urls import url
from . import views
from .views import *


urlpatterns = [
    # home
    url(r'^$', views.index, name='index'),
    # /reg
    url(r'^loc/?$', views.spots, name='spot'),
    # /loc/10
    url(r'^loc/(?P<spot_id>[0-9]+)/?$', views.spot_detail, name='spot_detail'),
    url(r'^reg/?$', views.general_register, name='general_register'),

    url(r'^conces/?$', views.ownerships_old, name='ownerships_old'),
    url(r'^constr/?$', views.constructions_old, name='constructions_old'),
    url(r'^oper/?$', views.operations, name='operations'),
    url(r'^incas/?$', views.revenue, name='revenue'),
    #url(r'^intret/?$', views.maintentance, name='maintenance'),

    url(r'^admin/?$', views.administration, name='administration'),
    url(r'^admin/locuri/?$', views.spots_administration, name='spots_administration'),
    url(r'^admin/acte_conces/?$', views.administration, name='ownership_deeds_administration'),
    url(r'^admin/chit_conces/?$', views.administration, name='ownership_receipts_administration'),
    url(r'^admin/conces/?$', views.administration, name='owners_administration'),
    url(r'^admin/constr/?$', views.administration, name='constructions_administration'),
    url(r'^admin/aut_constr/?$', views.administration, name='construction_authorizations_administration'),
    url(r'^admin/firme_constr/?$', views.administration, name='construction_companies_administration'),
    url(r'^admin/contrib/?$', views.administration, name='payments_administration'),
    url(r'^admin/chit_contrib/?$', views.administration, name='payment_receipts_administration'),
    url(r'^admin/inhum/?$', views.administration, name='operations_administration'),
    url(r'^admin/intret/?$', views.administration, name='maintenance_administration'),

    # url(r'^save/?$', views.save, name='save'),

    url(r'^payments/?$', views.payments, name='payments'),
    url(r'^payments/api/?$', PaymentsAPI.as_view()),
    url(r'^payments/api/(?P<payment_id>[0-9]+)/?$', PaymentsAPI.as_view()),

    url(r'^burials/?$', burials, name='burials'),
    url(r'^burials/api/?$', BurialsAPI.as_view()),
    url(r'^burials/api/(?P<burial_id>[0-9]+)/?$', BurialsAPI.as_view()),

    # TODO delete the _jsgrid suffix
    url(r'^maintenance_jsgrid/?$', views.maintenance, name='maintenance'),
    url(r'^maintenance_jsgrid/api/?$', MaintenanceAPI.as_view()),
    url(r'^maintenance_jsgrid/api/(?P<level_id>[0-9]+)/?$', MaintenanceAPI.as_view()),

    # TODO remove _jsgrid suffix
    url(r'^ownerships_jsgrid/?$', views.ownerships, name='ownerships'),
    url(r'^ownerships_jsgrid/api/?$', OwnershipsAPI.as_view()),
    url(r'^ownerships_jsgrid/api/(?P<deed_id>[0-9]+),(?P<receipt_id>[0-9]+)/?$',
        OwnershipsAPI.as_view()),

    # TODO remove _jsgrid suffix
    url(r'^constructions_jsgrid/?$', views.constructions, name='constructions_jsgrid'),
    url(r'^constructions_jsgrid/api/?$', ConstructionsAPI.as_view()),
    url(r'^constructions_jsgrid/api/(?P<construction_id>[0-9]+),(?P<authorization_id>[0-9]+),(?P<spot_id>[0-9]+)/?$',
        ConstructionsAPI.as_view()),
]
