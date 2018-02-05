from django.contrib.gis.geos import Polygon, MultiPolygon

import factory

from ..models import CityParkingZone


class CityParkingZoneFactory(factory.DjangoModelFactory):
    class Meta:
        model = CityParkingZone

    name = factory.Sequence(lambda n: "Zone {0}".format(n))
    zone = factory.Sequence(lambda n: MultiPolygon(
        Polygon((
            (0, 0),
            (0, 100/(n+1)),
            (100/(n+1), 100/(n+1)),
            (100/(n+1), 0),
            (0, 0)
        )),
        Polygon((
            (0, 0),
            (0, -100/(n+1)),
            (-100/(n+1), -100/(n+1)),
            (-100/(n+1), 0),
            (0, 0)
        )),
    ))
    external_id = factory.Sequence(lambda n: n)
