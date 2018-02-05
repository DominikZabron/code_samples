from django.http import Http404
from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from modules.authentication.permissions import is_authenticated_as
from modules.transactionpackages.models import TransactionPackage

from . import serializers
from .models import Transaction


class TransactionView(ViewSetMixin, ListCreateAPIView):
    permission_classes = (is_authenticated_as(['patient']),)
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.OrderingFilter
    )
    filter_fields = ('payment_status',)
    ordering_fields = ('amount', 'price', 'payment_date', 'patient')

    def get_queryset(self):
        return Transaction.o.filter(
            patient=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.TransactionCreateSerializer
        elif self.action == 'list':
            return serializers.TransactionPatientSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tp = TransactionPackage.o.get(
                id=serializer.data['transaction_package'])
        except TransactionPackage.DoesNotExist:
            raise Http404

        transaction = Transaction.o.create(
            patient=self.request.user,
            amount=tp.amount,
            price=tp.price,
        )

        serializer = serializers.TransactionPatientSerializer(transaction)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BalanceView(RetrieveAPIView):
    permission_classes = (is_authenticated_as(['patient']),)
    serializer_class = serializers.BalanceSerializer

    def get_object(self):
        return self.request.user


class TransactionDetailView(RetrieveAPIView):
    permission_classes = (is_authenticated_as(['doctor', 'patient']),)

    def get_serializer_class(self):
        if self.request.user.type() == "doctor":
            return serializers.TransactionDoctorSerializer
        elif self.request.user.type() == "patient":
            return serializers.TransactionPatientSerializer

    def get_object(self):
        account_type = self.request.user.type()

        try:
            if account_type == 'patient':
                return Transaction.o.get(
                    id=self.kwargs['transaction_pk'],
                    patient=self.request.user
                )
            elif account_type == 'doctor':
                return Transaction.o.select_related('patient__doctor').get(
                    id=self.kwargs['transaction_pk'],
                    patient__doctor=self.request.user
                )
        except Transaction.DoesNotExist:
            raise Http404
