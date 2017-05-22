from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET
    url(r'^', admin.site.urls),
]
