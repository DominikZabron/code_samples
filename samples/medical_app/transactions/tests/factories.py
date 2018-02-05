# -*- coding: utf-8 -*-
import factory

from modules.users.tests.factories import PatientFactory

from ..models import Transaction


class TransactionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Transaction

    patient = factory.SubFactory(PatientFactory)
    amount = 30
    price = 6000
    commission = 60
