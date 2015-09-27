from django.conf.urls import url
from . import views


urlpatterns = [
    # home
    url(r'^$', views.index, name='index'),
    # /reg
    url(r'^loc/?$', views.spots, name='spot'),
    # /loc/10
    url(r'^loc/(?P<spot_id>[0-9]+)/?$', views.spot_detail, name='spot_detail'),
    url(r'^reg/?$', views.general_register, name='general_register'),

    url(r'^conces/?$', views.ownerships, name='ownerships'),
    url(r'^constr/?$', views.constructions, name='constructions'),
    url(r'^oper/?$', views.operations, name='operations'),
    url(r'^incas/?$', views.revenue, name='revenue'),
    url(r'^intret/?$', views.maintentance, name='maintenance'),

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

    url(r'^save/?$', views.save, name='save'),
]