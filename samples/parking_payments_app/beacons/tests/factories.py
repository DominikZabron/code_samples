from uuid import uuid4

import factory

from ..models import Parkbox


class ParkboxFactory(factory.DjangoModelFactory):
    class Meta:
        model = Parkbox

    uuid = factory.sequence(lambda n: uuid4())
    major = factory.sequence(lambda n: 10000 + n)
    minor = factory.sequence(lambda n: 10000 + n)
