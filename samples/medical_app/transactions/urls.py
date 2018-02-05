from django.conf.urls import url

from modules.core.utils import UUID4_REGEXP

from . import views

app_name = 'transactions'

urlpatterns = [
    url(
        r'^/?$',
        views.TransactionView.as_view({'get': 'list', 'post': 'create'}),
        name='list_create'
    ),
    url(
        r'^/balance/?$',
        views.BalanceView.as_view(),
        name='balance'
    ),
    url(
        r'^/(?P<transaction_pk>{uuid4_regexp})/?$'.format(
            uuid4_regexp=UUID4_REGEXP
        ),
        views.TransactionDetailView.as_view(),
        name='detail'
    ),
]
