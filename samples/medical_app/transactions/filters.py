import django_filters

from .models import Transaction


def filter_month(queryset, value):
    if not value:
        return queryset

    try:
        year, month = value.split('_', 1)
        q = queryset.filter(created_at__year=year, created_at__month=month)
        return q
    except:
        return queryset


class TransactionFilter(django_filters.FilterSet):
    year_month = django_filters.CharFilter(action=filter_month)

    class Meta:
        model = Transaction
        fields = ('year_month', 'payment_status',)
