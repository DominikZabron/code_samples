from rest_framework import serializers

from modules.users.models import Patient

from .models import Transaction


class TransactionCreateSerializer(serializers.Serializer):
    transaction_package = serializers.UUIDField()


class PatientBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'first_name', 'last_name')


class TransactionDoctorSerializer(serializers.ModelSerializer):
    patient = PatientBasicSerializer()

    class Meta:
        model = Transaction
        fields = (
            'id', 'created_at', 'patient', 'amount', 'price',
            'payment_status', 'status', 'commission'
        )
        read_only_fields = (
            'id', 'created_at', 'patient', 'amount', 'price',
            'payment_status', 'status', 'commission'
        )


class TransactionPatientSerializer(serializers.ModelSerializer):
    patient = PatientBasicSerializer()

    class Meta:
        model = Transaction
        fields = (
            'id', 'created_at', 'patient', 'amount', 'price', 'payment_status',
            'payment_id'
        )
        read_only_fields = (
            'id', 'created_at', 'patient', 'amount', 'price', 'payment_status',
            'payment_id'
        )


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('currency_balance',)
