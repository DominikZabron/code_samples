from django.conf.urls import url

from . import views

app_name = 'payu'

urlpatterns = [
    url(
        r'^/accesstoken/?$',
        views.TokenView.as_view(),
        name='get'
    ),
    url(
        r'^/orderstatus/?$',
        views.PaymentStatusView.as_view(),
        name='update'
    ),
]
