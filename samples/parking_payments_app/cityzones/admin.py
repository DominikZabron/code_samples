import pygeoj
from pykml import parser

from django.contrib.gis import admin
from django.contrib.gis.geos import Polygon, MultiPolygon
from django.core.serializers import serialize
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

from .models import CityParkingZone, ZonePricingHours, ZonePricingProgression


def save_zone_json(modeladmin, request, queryset):
    for obj in queryset:
        geojson = pygeoj.load(filepath=obj.json_file.path)
        obj.zone = MultiPolygon(
            [Polygon(feature.geometry.coordinates[0]) for feature in geojson])
        obj.save()
save_zone_json.short_description = _("Load parking zone from json files")


def save_zone_kml(modeladmin, request, queryset):
    for obj in queryset:
        kml = parser.parse(obj.kml_file).getroot()
        coords = []
        for placemark in kml.Document.Folder.Placemark:
            coord = placemark.Polygon.outerBoundaryIs.LinearRing.coordinates.\
                text.replace('\n', '').replace('\t', '').split(',0 ')
            coords.append(coord)

        for item in coords:
            for i in range(len(item)):
                item[i] = item[i].split(',')
                if item[i] == ['']:
                    del item[i]
                    continue
                for j in range(len(item[i])):
                    item[i][j] = float(item[i][j])

        poly = []
        for item in coords:
            poly.append(Polygon(item))
        obj.zone = MultiPolygon(poly)
        obj.save()
save_zone_kml.short_description = _("Load parking zone from kml files")


def save_file(modeladmin, request, queryset):
    for obj in queryset:
        content = serialize(
            'geojson', [obj], geometry_field='zone', fields=())
        obj.json_file.save("{0}.json".format(obj.name), ContentFile(content))
        obj.save()
save_file.short_description = _("Export parking zone to files")


@admin.register(CityParkingZone)
class CityParkingZoneAdmin(admin.OSMGeoAdmin):
    fields = ('name', 'external_id', 'id', 'created_at', 'updated_at',
              'json_file', 'kml_file', 'zone',)
    readonly_fields = ('id', 'created_at', 'updated_at',)
    list_display = ('name', 'id', 'created_at', 'updated_at', 'external_id',)
    modifiable = False
    actions = [save_zone_json, save_zone_kml, save_file, ]

    def add_view(self, request, form_url='', extra_context=None):
        self.fields = ('name', 'external_id', 'id', 'created_at', 'updated_at',
                       'json_file', 'kml_file',)
        return self.changeform_view(request, None, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.fields = ('name', 'external_id', 'id', 'created_at', 'updated_at',
                       'json_file', 'kml_file', 'zone',)
        return self.changeform_view(
            request, object_id, form_url, extra_context)

    def get_actions(self, request):
        actions = super(CityParkingZoneAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


class ZonePricingProgressionInline(admin.TabularInline):
    model = ZonePricingProgression
    fields = ('time_range_from', 'time_range_to', 'price',)
    extra = 0


@admin.register(ZonePricingHours)
class ZonePricingHoursAdmin(admin.ModelAdmin):
    inlines = [ZonePricingProgressionInline, ]
    fields = ('zone', 'day_of_week', 'start', 'end', 'minimum_price',
              'billing_time',)
    list_display = ('zone', 'day_of_week', 'start', 'end', 'minimum_price',
                    'billing_time',)
    list_filter = ('zone__name',)
