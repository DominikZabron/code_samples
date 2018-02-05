from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from . import serializers


class BeaconRetrieveAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        serializer = serializers.ParameterSerializer(
            data=request.query_params, context={'request': self.request})
        if serializer.is_valid():
            pbox = serializer.validated_data['parkbox']
            serializer = serializers.ParkboxIdSerializer(pbox)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_404_NOT_FOUND)
