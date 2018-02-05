from django.db import models
from django.utils.translation import ugettext_lazy as _

from modules.core.db import BaseModel
from modules.users.models import Patient


class Token(BaseModel):
    patient = models.ForeignKey(
        Patient,
        verbose_name=_("patient"),
        related_name='payu',
        editable=False,
        unique=True
    )
    access_token = models.CharField(
        _("access token"),
        max_length=255
    )
    refresh_token = models.CharField(
        _("refresh token"),
        max_length=255
    )
    expires_in = models.DateTimeField(
        _("expires in")
    )

    def __unicode__(self):
        return self.patient.__unicode__()
