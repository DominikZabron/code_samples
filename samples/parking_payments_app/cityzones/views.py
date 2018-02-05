from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from . import serializers
from .models import CityParkingZone


class CityParkingZoneListAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        serializer = serializers.ParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        lat = serializer.validated_data['lat']
        lng = serializer.validated_data['lng']
        m = serializer.validated_data['m']
        zones = CityParkingZone.objects.filter(
            zone__dwithin=(Point(lat, lng), D(m=m)))
        serializer = serializers.CityParkingZoneSerializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
