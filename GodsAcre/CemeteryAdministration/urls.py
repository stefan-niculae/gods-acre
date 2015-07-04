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
    url(r'^administr/?$', views.administration, name='administration'),
]