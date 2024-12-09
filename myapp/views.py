from email.headerregistry import Group
from rest_framework import viewsets, status
from rest_framework.decorators import action
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
    """
    ViewSet para manejar las paradas (stops).
    """
    queryset = Stop.objects.all()
    serializer_class = StopSerializer

    # Endpoint personalizado para obtener las paradas relacionadas con un load específico
    @action(detail=False, methods=['get'], url_path='load/(?P<load_id>[^/.]+)')
    def stops_by_load(self, request, load_id=None):
        stops = Stop.objects.filter(load__idmmload=load_id)
        if not stops.exists():
            return Response(
                {"detail": "No stops found for the specified load."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(stops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EquipmentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para manejar los tipos de equipamiento (EquipmentTypes).
    """
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer


class LoadStopsView(APIView):
    """
    APIView para manejar operaciones específicas en Stops asociados a un Load.
    """

    def get(self, request, load_id):
        """Obtener todas las paradas asociadas a un Load específico."""
        load = get_object_or_404(Load, idmmload=load_id)
        stops = load.stops.all()  # Usa related_name definido en el modelo
        serializer = StopSerializer(stops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, load_id):
        """Crear nuevas paradas asociadas a un Load específico."""
        load = get_object_or_404(Load, idmmload=load_id)
        stop_data = request.data.get("stops", [])

        for stop in stop_data:
            stop["load"] = load.id  # Asociar con el campo correcto

        serializer = StopSerializer(data=stop_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, load_id, stop_id):
        """Actualizar un stop existente."""
        stop = get_object_or_404(Stop, id=stop_id, load__idmmload=load_id)

        serializer = StopSerializer(stop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, load_id, stop_id):
        """Eliminar un stop existente."""
        stop = get_object_or_404(Stop, id=stop_id, load__idmmload=load_id)
        stop.delete()
        return Response({"message": "Stop deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class OfferHistoryView(APIView):
    """
    APIView para manejar el historial de ofertas asociadas a un Load.
    """

    def get(self, request, load_id):
        """Obtener el historial de ofertas asociadas a un Load específico."""
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication is required to view offers."}, status=status.HTTP_401_UNAUTHORIZED)

        load = get_object_or_404(Load, idmmload=load_id)
        offers = OfferHistory.objects.filter(load=load).order_by('-date')
        serializer = OfferHistorySerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class OfferHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, load_id):
        """
        Listar el historial de ofertas de una carga específica.
        """
        load = get_object_or_404(Load, idmmload=load_id)
        offers = OfferHistory.objects.filter(load=load)
        serializer = OfferHistorySerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, load_id):
        """
        Crear una nueva oferta asociada a una carga específica.
        """
        load = get_object_or_404(Load, idmmload=load_id)

        # Validar los datos enviados
        serializer = OfferHistorySerializer(data=request.data)
        if serializer.is_valid():
            # Asociar la oferta con el usuario autenticado y la carga
            serializer.save(user=request.user, load=load)

            # Actualizar campos en el modelo Load
            load.number_of_offers += 1
            load.is_offerted = True
            load.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, offer_id, action):
        """
        Aceptar o rechazar una oferta específica.
        """
        offer = get_object_or_404(OfferHistory, id=offer_id)

        if action == "accept":
            try:
                offer.accept_offer()
                return Response({"message": "Oferta aceptada con éxito."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif action == "reject":
            try:
                offer.reject_offer()
                return Response({"message": "Oferta rechazada con éxito."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Acción no válida. Use 'accept' o 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
