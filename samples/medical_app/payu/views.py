import datetime
import json
import logging

import requests
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.authentication.permissions import is_authenticated_as
from modules.transactions.models import Transaction

from .models import Token
from . import serializers

logger = logging.getLogger(__name__)


class TokenView(APIView):
    permission_classes = (is_authenticated_as(['patient']),)

    def get(self, request):
        try:
            token = Token.o.get(patient=request.user)
            # jezeli token jest wazny, zwracamy token
            if token.expires_in > timezone.now():
                access_token = token.access_token
            # jezeli token wygasl, pytamy o kolejny
            else:
                # access_token = self.payu_auth_refresh(instance=token)
                token.delete()
                access_token = self.payu_auth_request(patient=request.user)
        # jezeli nie ma w bazie tokena, pytamy o nowy
        except Token.DoesNotExist:
            access_token = self.payu_auth_request(patient=request.user)

        return Response({'access_token': str(access_token)}, status=200)

    def payu_auth_request(self, patient, url=settings.PAYU_AUTH_URL):
        patient_data = {
            'id': patient.id,
            'email': patient.email,
            'email_verified': patient.email_verified
        }
        serializer = serializers.PatientPaymentSerializer(data=patient_data)
        serializer.is_valid(raise_exception=True)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        payload = {
            'grant_type': 'trusted_merchant',
            'client_id': settings.PAYU_CLIENT_ID,
            'client_secret': settings.PAYU_CLIENT_SECRET,
            'email': serializer.validated_data['email'],
            'ext_customer_id': serializer.validated_data['id'],
        }
        response = requests.post(url, payload, headers=headers)
        serializer = serializers.TokenAuthSerializer(
            data=json.loads(response.text))
        if serializer.is_valid(raise_exception=True):
            Token.o.create(
                patient=patient,
                access_token=serializer.validated_data['access_token'],
                refresh_token=serializer.validated_data['refresh_token'],
                expires_in=timezone.now() + datetime.timedelta(
                    seconds=serializer.validated_data['expires_in'])
            )
            return serializer.validated_data['access_token']
        else:
            logger.exception(
                u"Invalid payu_auth_request response."
                u"request:{0}, response{1}".format(
                    force_text(payload), force_text(response.text))
            )

    def payu_auth_refresh(self, instance, url=settings.PAYU_AUTH_URL):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        payload = {
            'grant_type': 'trusted_merchant_refresh_token',
            'access_token': instance.access_token,
            'refresh_token': instance.refresh_token,
        }
        response = requests.post(url, payload, headers=headers)
        serializer = serializers.TokenAuthSerializer(
            data=json.loads(response.text))
        if serializer.is_valid():
            instance.expires_in = timezone.now() + datetime.timedelta(
                seconds=serializer.validated_data['expires_in'])
            instance.access_token = serializer.validated_data['access_token']
            instance.save()
            return serializer.validated_data['access_token']
        else:
            patient = instance.patient
            instance.delete()
            access_token = self.payu_auth_request(patient)
            return access_token


@method_decorator(csrf_exempt, name='dispatch')
class PaymentStatusView(View):
    def post(self, request):
        serializer = serializers.StatusSerializer(
            data=json.loads(request.body))
        if not serializer.is_valid():
            logger.exception(u"PayU: Unsupported data. {0}".format(
                force_text(request.body)))
            return HttpResponse(status=status.HTTP_200_OK)

        try:
            instance = Transaction.o.get(
                payment_id=serializer.validated_data['order']['extOrderId'])
        except Transaction.DoesNotExist:
            logger.exception(
                u"PayU: payment does not exist. {0}".format(
                    force_text(request.body)))
            return HttpResponse(status=status.HTTP_200_OK)

        if instance.payment_status != 'confirmed':
            with transaction.atomic():
                if serializer.validated_data['order']['status'] == 'COMPLETED':
                    instance.payment_status = 'confirmed'
                    instance.payment_date = timezone.now()
                    instance.recharge_account()
                    instance.save()
                elif serializer.validated_data['order']['status'] == 'PENDING':
                    pass
                else:
                    instance.payment_status = 'canceled'
                    instance.payment_date = timezone.now()
                    instance.save()

        return HttpResponse(status=status.HTTP_200_OK)
