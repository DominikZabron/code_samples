from hashlib import md5
from decimal import Decimal

from django.db import models, transaction
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from modules.core.db import BaseModel
from modules.users.models import Patient

SETTLEMENT_STATUS = (
    ('settled', _("settled")),
    ('to_settle', _("to settle"))
)

PAYMENT_STATUS = (
    ('new', _("new")),
    ('confirmed', _("confirmed")),
    ('canceled', _("canceled"))
)


class Transaction(BaseModel):
    patient = models.ForeignKey(
        Patient,
        verbose_name=_("patient"),
        related_name='transactions',
        editable=False
    )
    amount = models.PositiveIntegerField(
        _("amount"),
        editable=False
    )
    price = models.DecimalField(
        _("price"),
        max_digits=9,
        decimal_places=2,
        editable=False
    )
    payment_id = models.CharField(
        _("payment id"),
        max_length=255,
        blank=True
    )
    payment_status = models.CharField(
        _("payment status"),
        max_length=9,
        choices=PAYMENT_STATUS,
        default='new'
    )
    payment_date = models.DateTimeField(
        _("payment date"),
        blank=True,
        null=True,
        default=None
    )
    status = models.CharField(
        _("status"),
        max_length=9,
        choices=SETTLEMENT_STATUS,
        default='to_settle'
    )
    commission = models.DecimalField(
        _("commission"),
        max_digits=9,
        decimal_places=2,
        null=True,
        default=None
    )

    def save(self, *args, **kwargs):
        self.payment_id = self.set_external_id(self.id)
        super(Transaction, self).save(*args, **kwargs)

    def set_external_id(self, id):
        hash = md5(str(id))
        hash_hex = hash.hexdigest()
        hash_string = hash_hex.decode('ascii')
        return hash_string

    def recharge_account(self):
        with transaction.atomic():
            self.patient.currency_balance += self.amount
            self.patient.save()
            self.commission = self.price * Decimal(settings.COMMISSION_QUOTE)
            self.save()

    def __unicode__(self):
        return self.patient.__unicode__()

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
