from django.conf.urls import include, url
from django.contrib import admin

from .views import import_entries


urlpatterns = [
    url(r'^jet', include('jet.urls', 'jet')),  # Django JET
    url(r'^', admin.site.urls),
    # TODO add link to import page on main page
    url(r'^import$', import_entries, name='import'),
]
