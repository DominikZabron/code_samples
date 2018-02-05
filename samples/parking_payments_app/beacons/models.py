import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

from django_fsm import FSMField, transition

from modules.core.db.base import BaseModel

BEACON_TYPE = {
    ('kontaktio', _("kontaktio")),
}


def set_estimated_battery_life(beacon_type):
    return timezone.now() + \
        datetime.timedelta(settings.ESTIMATED_BATTERY_LIFE[beacon_type])


class Parkbox(BaseModel):
    uuid = models.UUIDField(
        _("uuid"),
    )
    type = models.CharField(
        _("type"),
        max_length=20,
        default='kontaktio',
    )
    major = models.PositiveIntegerField(
        _("major"),
    )
    minor = models.PositiveIntegerField(
        _("minor"),
    )
    estimated_battery_life = models.DateTimeField(
        _("estimated battery life"),
        null=True,
    )
    state = FSMField(
        _("state"),
        default='free',
    )

    def __unicode__(self):
        return unicode(self.uuid)

    def save(self, *args, **kwargs):
        if not self.estimated_battery_life:
            self.estimated_battery_life = set_estimated_battery_life(self.type)
            super(Parkbox, self).save(*args, **kwargs)
            ParkboxHistory.objects.create(parkbox=self)
        else:
            super(Parkbox, self).save(*args, **kwargs)

    def can_associate(self):
        return hasattr(self, 'vehicle')

    @transition(field=state,
                source=['free', 'restored'],
                target='associated',
                conditions=[can_associate],)
    def associate(self):
        ParkboxHistory.objects.create(
            parkbox=self,
            state='associated',
            vehicle=self.vehicle,
        )

    @transition(field=state,
                source='associated',
                target='disassociated',)
    def disassociate(self):
        vehicle = self.vehicle
        vehicle.parkbox = None
        vehicle.save()
        ParkboxHistory.objects.create(
            parkbox=self,
            state='disassociated',
            vehicle=None,
        )

    @transition(field=state,
                source=['disassociated', 'removed'],
                target='restored')
    def restore(self):
        ParkboxHistory.objects.create(
            parkbox=self,
            state='restored',
            vehicle=None,
        )

    @transition(field=state,
                source=['free', 'restored', 'disassociated'],
                target='removed')
    def remove(self):
        ParkboxHistory.objects.create(
            parkbox=self,
            state='removed',
            vehicle=None,
        )

    class Meta:
        verbose_name = _("parkbox")
        verbose_name_plural = _("parkboxes")
        unique_together = ('uuid', 'major', 'minor',)


class ParkboxHistory(BaseModel):
    parkbox = models.ForeignKey(
        Parkbox,
        verbose_name=_("parkbox"),
        related_name='history',
        on_delete=models.CASCADE,

    )
    state = models.CharField(
        _("state"),
        max_length=20,
        default='free',
    )
    previous = models.OneToOneField(
        'self',
        verbose_name=_("previous state"),
        related_name='next',
        null=True,
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        verbose_name=_("vehicle"),
        related_name='history',
        null=True,
        default=None,
    )
    comment = models.TextField(
        _("comment"),
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return self.state

    def save(self, *args, **kwargs):
        if not self.previous:
            try:
                self.previous = ParkboxHistory.objects.filter(
                    parkbox=self.parkbox).latest('created_at')
            except ParkboxHistory.DoesNotExist:
                self.previous = None
        super(ParkboxHistory, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("History")
        verbose_name_plural = _("History")
