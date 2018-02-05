from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from modules.core.db.base import BaseModel

DAY_OF_WEEK = (
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday")),
)


class CityParkingZone(BaseModel):
    name = models.CharField(
        _("name"),
        max_length=255,
    )
    zone = models.MultiPolygonField(
        _("zone"),
        geography=True,
        default='MULTIPOLYGON(((0 0, 0 0.0000000000000001,'
                ' 0.0000000000000001 0.0000000000000001, 0 0)))',
    )
    json_file = models.FileField(
        _("json file"),
        blank=True,
        null=True,
        default=None,
    )
    kml_file = models.FileField(
        _("kml file"),
        blank=True,
        null=True,
        default=None,
    )
    external_id = models.PositiveIntegerField(
        _("external id"),
        unique=True,
        null=True,
        default=None,
    )

    def __unicode__(self):
        return self.name


class ZonePricingHours(BaseModel):
    zone = models.ForeignKey(
        CityParkingZone,
        verbose_name=_("zone"),
        related_name='pricing',
    )
    day_of_week = models.IntegerField(
        _("day of week"),
        choices=DAY_OF_WEEK,
    )
    start = models.TimeField(
        _("start"),
    )
    end = models.TimeField(
        _("end"),
    )
    minimum_price = models.DecimalField(
        _("minimum price"),
        max_digits=7,
        decimal_places=2,
    )
    billing_time = models.PositiveIntegerField(
        _("billing time"),
    )

    def __unicode__(self):
        return self.zone.name + ' ' + self.get_day_of_week_display()

    class Meta:
        verbose_name = _("zone pricing hour")
        verbose_name_plural = _("zone pricing hours")


class ZonePricingProgression(BaseModel):
    pricing = models.ForeignKey(
        ZonePricingHours,
        verbose_name=_("pricing"),
        related_name='progression',
    )
    time_range_from = models.PositiveIntegerField(
        _("time range from"),
    )
    time_range_to = models.PositiveIntegerField(
        _("time range to"),
        null=True,
        default=None,
    )
    price = models.DecimalField(
        _("price"),
        max_digits=7,
        decimal_places=2,
    )

    def __unicode__(self):
        return str(self.time_range_from) + ' : ' + str(self.time_range_to)
