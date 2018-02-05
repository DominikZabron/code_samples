from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_friendly_errors.mixins \
    import FriendlyErrorMessagesMixin as FemMixin

from .models import Parkbox


class ParkboxSerializer(FemMixin, serializers.ModelSerializer):
    class Meta:
        model = Parkbox
        fields = ('id', 'created_at', 'updated_at', 'uuid',
                  'type', 'major', 'minor', 'state',
                  'estimated_battery_life',)


class ParkboxIdSerializer(FemMixin, serializers.ModelSerializer):
    parkbox_id = serializers.UUIDField(source='id')

    class Meta:
        model = Parkbox
        fields = ('parkbox_id',)


class ParameterSerializer(FemMixin, serializers.Serializer):
    uuid = serializers.UUIDField()
    major = serializers.IntegerField(required=False)
    minor = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if attrs.get('uuid', False):
            try:
                pbox = Parkbox.objects.get(**attrs)
            except Parkbox.DoesNotExist:
                raise serializers.ValidationError(
                    _("Beacon not found.")
                )
            except Parkbox.MultipleObjectsReturned:
                raise serializers.ValidationError(
                    _("Major and minor is required for better accuracy.")
                )

            if pbox.state in ('disassociated', 'removed'):
                raise serializers.ValidationError(
                    _("Beacon not found.")
                )

            if hasattr(pbox, 'vehicle'):
                if pbox.vehicle.user == self.context['request'].user:
                    raise serializers.ValidationError(
                        _("Beacon registered to other car of current user.")
                    )
                else:
                    raise serializers.ValidationError(
                        _("Beacon owned by other user.")
                    )

            attrs['parkbox'] = pbox
            return attrs

        raise serializers.ValidationError(_("Beacon not found."))

    NON_FIELD_ERRORS = {
        _("Beacon not found."): 7014,
        _("Major and minor is required for better accuracy."): 7013,
        _("Beacon registered to other car of current user."): 7011,
        _("Beacon owned by other user."): 7012,
    }
