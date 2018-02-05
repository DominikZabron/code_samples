from django.conf.urls import url

from . import views


app_name = 'beacons'

urlpatterns = [
    url(
        r'^/?$',
        views.BeaconRetrieveAPIView.as_view(),
        name='get'
    ),
]
