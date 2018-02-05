from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework import serializers
from rest_framework_friendly_errors.mixins \
    import FriendlyErrorMessagesMixin as FemMixin

from .models import CityParkingZone


class CityParkingZoneSerializer(FemMixin, serializers.ModelSerializer):
    class Meta:
        model = CityParkingZone
        # TODO - include pricing when done
        fields = ('id', 'name')


class ParameterSerializer(FemMixin, serializers.Serializer):
    position = serializers.CharField(required=True)
    accuracy = serializers.CharField(required=False)

    def validate(self, attrs):
        try:
            attrs['lat'], attrs['lng'] = (
                float(p) for p in attrs['position'].split(','))
        except ValueError:
            raise serializers.ValidationError(
                _("Provided position is not valid.")
            )
        attrs['m'] = settings.POSITION_ACCURACY.get(
            attrs.get('accuracy'), settings.POSITION_ACCURACY['gps'])
        return attrs

    NON_FIELD_ERRORS = {
        _("Provided position is not valid."): 1777,
    }
