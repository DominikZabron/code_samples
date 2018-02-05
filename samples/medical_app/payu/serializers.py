from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .models import Token


class TokenAuthSerializer(serializers.ModelSerializer):
    expires_in = serializers.IntegerField()

    class Meta:
        model = Token
        fields = ('access_token', 'refresh_token', 'expires_in')


class OrderStatusSerializer(serializers.Serializer):
    extOrderId = serializers.CharField()
    status = serializers.CharField()


class StatusSerializer(serializers.Serializer):
    order = OrderStatusSerializer()


class PatientPaymentSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    email = serializers.EmailField()
    email_verified = serializers.BooleanField(required=True)

    def validate_email(self, value):
        if value is None:
            raise serializers.ValidationError(
                u"code=30001|message={0}".format(
                    _("Enter a valid email address.")
                )
            )
        return value

    def validate_email_confirmed(self, value):
        if value is False:
            raise serializers.ValidationError(
                u"code=42006|message={0}".format(
                    _("Email not verified.")
                )
            )
        return value
