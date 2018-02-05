from django.contrib import admin

from import_export import resources
from import_export.admin import ImportMixin
from fsm_admin.mixins import FSMTransitionMixin

from .models import Parkbox, ParkboxHistory


class ParkboxResource(resources.ModelResource):
    class Meta:
        model = Parkbox
        import_id_fields = ('uuid',)
        fields = ('uuid', 'major', 'minor',)


@admin.register(Parkbox)
class ParkboxAdmin(ImportMixin, FSMTransitionMixin, admin.ModelAdmin):
    fields = ('id', 'created_at', 'updated_at', 'uuid', 'type',
              'major', 'minor', 'state', 'estimated_battery_life',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'state',
                       'estimated_battery_life',)
    list_display = ('uuid', 'type', 'major',
                    'minor', 'state', 'estimated_battery_life',)
    search_fields = ('uuid', 'vehicle__plate_number', 'vehicle__user__phone')
    list_filter = ('state',)
    resource_class = ParkboxResource
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ParkboxHistory)
class ParkboxHistoryAdmin(admin.ModelAdmin):
    fields = ('id', 'created_at', 'updated_at', 'parkbox', 'state', 'previous',
              'vehicle', 'comment',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'parkbox', 'state',
                       'previous', 'vehicle',)
    list_display = ('id', 'created_at', 'updated_at', 'parkbox', 'state',
                    'previous', 'vehicle',)

    def has_delete_permission(self, request, obj=None):
        return False
