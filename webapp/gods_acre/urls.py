from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    url(r'^jet',            include('jet.urls', 'jet')),    # django-jet
    url(r'^translations',   include('rosetta.urls')),       # django-rosetta
]

# TODO
urlpatterns += i18n_patterns(
    url(r'^', include('cemetery.urls')),
)
