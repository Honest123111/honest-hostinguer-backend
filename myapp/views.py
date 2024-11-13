from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer, Load, Stop, EquipmentType, OfferHistory
from .serializers import CustomerSerializer, LoadSerializer, StopSerializer, EquipmentTypeSerializer, OfferHistorySerializer
from django.utils import timezone
from django.shortcuts import get_object_or_404

# Customer ViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

# Load ViewSet
class LoadViewSet(viewsets.ModelViewSet):
    queryset = Load.objects.all()
    serializer_class = LoadSerializer

# Stop ViewSet
class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer

# EquipmentType ViewSet
class EquipmentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer

# Primera definición de LoadStopsView
class LoadStopsView(APIView):
    def get(self, request, load_id):
        try:
            load = Load.objects.get(idmmload=load_id)
            stops = load.stops.all()
            serializer = StopSerializer(stops, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Load.DoesNotExist:
            return Response({'error': 'Load not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, load_id):
        try:
            load = Load.objects.get(idmmload=load_id)
        except Load.DoesNotExist:
            return Response({'error': 'Load not found'}, status=status.HTTP_404_NOT_FOUND)

        stop_data = request.data.get('stops', [])
        serializer = StopSerializer(data=stop_data, many=True)

        if serializer.is_valid():
            for stop in serializer.validated_data:
                stop['load'] = load
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Segunda definición de LoadStopsView (duplicada)
class LoadStopsView(APIView):
    # Obtener todos los stops de un load específico
    def get(self, request, load_id):
        try:
            load = Load.objects.get(idmmload=load_id)
            stops = load.stops.all()
            serializer = StopSerializer(stops, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Load.DoesNotExist:
            return Response({'error': 'Load not found'}, status=status.HTTP_404_NOT_FOUND)

    # Crear nuevos stops para un load
    def post(self, request, load_id):
        try:
            load = Load.objects.get(idmmload=load_id)
        except Load.DoesNotExist:
            return Response({'error': 'Load not found'}, status=status.HTTP_404_NOT_FOUND)

        stop_data = request.data.get('stops', [])

        # Asegúrate de agregar el `load` a cada Stop
        for stop in stop_data:
            stop['load'] = load.idmmload

        serializer = StopSerializer(data=stop_data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar un stop existente
    def put(self, request, load_id, stop_id):
        try:
            stop = Stop.objects.get(id=stop_id, load_id=load_id)
        except Stop.DoesNotExist:
            return Response({'error': 'Stop not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StopSerializer(stop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Eliminar un stop existente
    def delete(self, request, load_id, stop_id):
        try:
            stop = Stop.objects.get(id=stop_id, load_id=load_id)
        except Stop.DoesNotExist:
            return Response({'error': 'Stop not found'}, status=status.HTTP_404_NOT_FOUND)

        stop.delete()
        return Response({'message': 'Stop deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# OfferHistoryView para manejar el historial de ofertas de un load
class OfferHistoryView(APIView):
    def post(self, request, load_id):
        try:
            load = Load.objects.get(idmmload=load_id)
        except Load.DoesNotExist:
            return Response({'error': 'Load not found'}, status=status.HTTP_404_NOT_FOUND)

        amount = request.data.get('amount')
        offer_status = request.data.get('status', 'Pending')

        # Crear la oferta en el historial
        offer = OfferHistory.objects.create(load=load, amount=amount, status=offer_status, date=timezone.now())

        # Actualizar el número de ofertas y el estado de is_offerted
        load.number_of_offers += 1
        load.is_offerted = True
        load.save()

        serializer = OfferHistorySerializer(offer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
