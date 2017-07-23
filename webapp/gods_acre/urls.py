from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns

from cemetery.views import import_entries


urlpatterns = [
    url(r'^jet',            include('jet.urls', 'jet')),    # django-jet
    url(r'^translations',   include('rosetta.urls')),       # django-rosetta
]

# TODO
urlpatterns += i18n_patterns(
    url(r'^', include('cemetery.urls')),
    # we have to do it here because translatable patterns can't be included
    url(r'^import$', import_entries, name='import'),
)
