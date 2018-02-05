# -*- coding: utf-8 -*-
import datetime
from uuid import uuid4

import factory
from django.utils import timezone

from modules.users.tests.factories import PatientFactory

from ..models import Token


class TokenFactory(factory.DjangoModelFactory):
    class Meta:
        model = Token

    patient = factory.SubFactory(PatientFactory)
    access_token = str(uuid4())
    refresh_token = str(uuid4())
    expires_in = timezone.now() + datetime.timedelta(seconds=1000)
