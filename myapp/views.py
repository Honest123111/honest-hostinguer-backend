from email.headerregistry import Group
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Warning
from .models import Customer, Load, Stop, EquipmentType, OfferHistory
from .serializers import (
    AssignRoleSerializer,
    CustomerSerializer,
    LoadSerializer,
    RegisterSerializer,
    StopSerializer,
    EquipmentTypeSerializer,
    OfferHistorySerializer,
)
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .serializers import WarningSerializer
from rest_framework.permissions import IsAuthenticated


# Customer ViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# Load ViewSet
class LoadViewSet(viewsets.ModelViewSet):
    queryset = Load.objects.prefetch_related('stops').all()  # Pre-fetch stops para optimizar
    serializer_class = LoadSerializer


# Stop ViewSet
class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer


# EquipmentType ViewSet
class EquipmentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer


# LoadStopsView para operaciones específicas en Stops de un Load
class LoadStopsView(APIView):

    def get(self, request, load_id):
        """Obtener todos los stops asociados a un Load específico."""
        try:
            load = get_object_or_404(Load, idmmload=load_id)
            stops = load.stops.all()  # Usa related_name para obtener stops
            serializer = StopSerializer(stops, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error retrieving stops: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, load_id):
        """Crear nuevos stops asociados a un Load específico."""
        try:
            load = get_object_or_404(Load, idmmload=load_id)
        except Load.DoesNotExist:
            return Response({"error": "Load not found"}, status=status.HTTP_404_NOT_FOUND)

        stop_data = request.data.get("stops", [])
        for stop in stop_data:
            stop["load"] = load.idmmload  # Asociar con el campo correcto

        serializer = StopSerializer(data=stop_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, load_id, stop_id):
        """Actualizar un stop existente."""
        stop = get_object_or_404(Stop, id=stop_id, load_id=load_id)

        serializer = StopSerializer(stop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, load_id, stop_id):
        """Eliminar un stop existente."""
        stop = get_object_or_404(Stop, id=stop_id, load_id=load_id)
        stop.delete()
        return Response({"message": "Stop deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class OfferHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, load_id):
        """Crear una oferta en el historial asociado a un Load específico."""
        # Verifica si el usuario está autenticado
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication is required to create an offer."}, status=401)

        load = get_object_or_404(Load, idmmload=load_id)

        amount = request.data.get("amount")
        offer_status = request.data.get("status", "pending")
        terms_change = request.data.get("terms_change", False)
        proposed_pickup_date = request.data.get("proposed_pickup_date")
        proposed_pickup_time = request.data.get("proposed_pickup_time")
        proposed_delivery_date = request.data.get("proposed_delivery_date")
        proposed_delivery_time = request.data.get("proposed_delivery_time")

        if not amount:
            return Response({"error": "Offer amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la oferta asociando el usuario logueado
        offer = OfferHistory.objects.create(
            load=load,
            user=request.user,  # Asociar el usuario autenticado
            amount=amount,
            status=offer_status,
            date=timezone.now(),
            terms_change=terms_change,
            proposed_pickup_date=proposed_pickup_date,
            proposed_pickup_time=proposed_pickup_time,
            proposed_delivery_date=proposed_delivery_date,
            proposed_delivery_time=proposed_delivery_time,
        )

        load.number_of_offers += 1
        load.is_offerted = True
        load.save()

        serializer = OfferHistorySerializer(offer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class AssignRoleView(APIView):
    """
    API para asignar un rol a un usuario.
    """
    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Role assigned successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RegisterView(APIView):
    permission_classes = []  # Permitir el acceso sin autenticación
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class WarningViewSet(viewsets.ModelViewSet):
    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
