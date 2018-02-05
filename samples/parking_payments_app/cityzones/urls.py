from django.conf.urls import url

from . import views


app_name = 'cityzones'

urlpatterns = [
    url(
        r'^/check_position/?$',
        views.CityParkingZoneListAPIView.as_view(),
        name='list'
    ),
]
