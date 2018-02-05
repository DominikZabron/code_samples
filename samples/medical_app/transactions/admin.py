from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum

from .models import Transaction

# Usuwa akcje dla calego admina
admin.site.disable_action('delete_selected')


class TotalChangeList(ChangeList):
    def get_results(self, request):
        super(TotalChangeList, self).get_results(request)
        self.amount_total = self.result_list.aggregate(
            Sum('amount')).items()[0][1]
        self.price_total = self.result_list.aggregate(
            Sum('price')).items()[0][1]
        self.commission_total = self.result_list.aggregate(
            Sum('commission')).items()[0][1]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('patient', 'amount', 'price', 'payment_id',
                       'payment_date', 'payment_status', 'commission',
                       'created_at')
    fieldsets = (
        (None, {
            'fields': ('created_at',)
        }),
        (_('Details'), {
            'fields': ('patient', 'amount', 'price')
        }),
        (_('Clearing'), {
            'fields': ('payment_id', 'payment_date', 'payment_status')
        }),
        (_('Settlement'), {
            'fields': ('commission', 'status')
        })
    )
    list_display = ('patient', 'created_at', 'amount', 'price',
                    'payment_date', 'payment_status', 'commission', 'status')
    ordering = ('payment_date', 'created_at')
    # payment_status tylko na czas developmentu
    list_editable = ('payment_status', 'status',)
    list_filter = ('payment_status', 'status',
                   ('payment_date', DateRangeFilter))
    search_fields = ('patient__first_name', 'patient__last_name',
                     '=patient__phone_number', '=patient__doctor__email',
                     '=patient__doctor__phone_number',
                     '=patient__doctor__nip',
                     '=patient__doctor__first_name',
                     '=patient__doctor__last_name'
                     )
    show_full_result_count = False
    actions = ['make_payment_confirmed']

    def get_changelist(self, request, **kwargs):
        return TotalChangeList

    def make_payment_confirmed(modeladmin, request, queryset):
        for obj in queryset:
            if obj.payment_status != 'confirmed':
                obj.payment_status = 'confirmed'
                obj.payment_date = timezone.now()
                obj.recharge_account()
                obj.save()
    make_payment_confirmed.short_description = \
        _("Confirm payments and recharge accounts")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
