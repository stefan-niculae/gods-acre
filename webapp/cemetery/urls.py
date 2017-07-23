from django.conf.urls import url
from django.contrib import admin

from .views import import_entries, test_view

# TODO translate urls
urlpatterns = [
    url(r'^', admin.site.urls),
    url(r'^import$', import_entries, name='import'),
    url(r'^test$', test_view, name='test')
]
