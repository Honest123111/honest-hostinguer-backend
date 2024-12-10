from email.headerregistry import Group
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Warning
from .models import Customer, Load, Stop, EquipmentType, OfferHistory,WarningList
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
from .serializers import WarningListSerializer
from .utils import send_email


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


# Consolidación de LoadStopsView
class LoadStopsView(APIView):
    def get(self, request, load_id):
        """Obtener todos los stops asociados a un Load específico."""
        try:
            load = Load.objects.get(idmmload=load_id)
            stops = load.stops.all()
            serializer = StopSerializer(stops, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Load.DoesNotExist:
            return Response({"error": "Load not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, load_id):
        """Crear nuevos stops asociados a un Load específico."""
        try:
            load = Load.objects.get(idmmload=load_id)
        except Load.DoesNotExist:
            return Response({"error": "Load not found"}, status=status.HTTP_404_NOT_FOUND)

        stop_data = request.data.get("stops", [])
        for stop in stop_data:
            stop["load"] = load.id  # Asegura la asociación correcta

        serializer = StopSerializer(data=stop_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, load_id, stop_id):
        """Actualizar un stop existente."""
        try:
            stop = Stop.objects.get(id=stop_id, load_id=load_id)
        except Stop.DoesNotExist:
            return Response({"error": "Stop not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StopSerializer(stop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, load_id, stop_id):
        """Eliminar un stop existente."""
        try:
            stop = Stop.objects.get(id=stop_id, load_id=load_id)
        except Stop.DoesNotExist:
            return Response({"error": "Stop not found"}, status=status.HTTP_404_NOT_FOUND)

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

class ReservedLoadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtener las cargas reservadas."""
        reserved_loads = Load.objects.filter(is_reserved=True)
        serializer = LoadSerializer(reserved_loads, many=True)
        return Response(serializer.data, status=200)

class OffertedLoadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtener las cargas que son ofertadas."""
        offerted_loads = Load.objects.filter(is_offerted=True)
        serializer = LoadSerializer(offerted_loads, many=True)
        return Response(serializer.data, status=200)

class UserAssignedLoadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtiene las cargas asignadas al usuario autenticado."""
        user = request.user
        print(f"Usuario autenticado: {user}")  # Log para verificar el usuario
        assigned_loads = Load.objects.filter(assigned_user=user)
        print(f"Cargas asignadas: {assigned_loads}")  # Log para verificar las cargas obtenidas
        serializer = LoadSerializer(assigned_loads, many=True)
        return Response(serializer.data, status=200)

class LoadWarningsView(APIView):
    """
    API para obtener las advertencias asociadas a una carga específica.
    """
    def get(self, request, load_id):
        try:
            print(f"Buscando carga con ID: {load_id}")
            load = Load.objects.get(idmmload=load_id)

            print(f"Encontrada carga: {load}")
            warnings = load.associated_warnings.all()  # Cambiar el nombre del related_name si es diferente
            print(f"Warnings asociados: {warnings}")

            serializer = WarningSerializer(warnings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Load.DoesNotExist:
            print(f"No se encontró la carga con ID: {load_id}")
            return Response({"error": "Load not found"}, status=status.HTTP_404_NOT_FOUND)


class AddWarningToLoadView(APIView):
    """
    API para agregar una advertencia a una carga específica.
    """
    def post(self, request, load_id):
        warning_list_id = request.data.get('warning_list_id')
        reported_by = request.user  # Suponiendo que el usuario autenticado reporta la advertencia

        if not warning_list_id:
            return Response({"error": "Warning List ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            load = Load.objects.get(idmmload=load_id)
            warning_list_item = WarningList.objects.get(id=warning_list_id)
        except Load.DoesNotExist:
            return Response({"error": "Load not found"}, status=status.HTTP_404_NOT_FOUND)
        except WarningList.DoesNotExist:
            return Response({"error": "Warning type not found"}, status=status.HTTP_404_NOT_FOUND)

        # Crear una nueva advertencia asociada al Load y al tipo de advertencia
        warning = Warning.objects.create(
            warning_type=warning_list_item,
            load=load,
            reported_by=reported_by
        )

        # Enviar correo al crear el warning
        try:
            subject = f"New Warning Created for Load ID {load.idmmload}"
            body = (
                f"A new warning has been created.\n\n"
                f"Details:\n"
                f"Load ID: {load.idmmload}\n"
                f"Warning Type: {warning_list_item.description}\n"
                f"Reported By: {reported_by.username}\n\n"
                f"Thank you,\nHonest Transportation INC"
            )
            recipient = "danielcampu28@gmail.com"  # Cambia al correo del destinatario
            send_email(subject, body, recipient)
        except Exception as e:
            print(f"Error sending email: {e}")

        return Response({"message": "Warning added successfully"}, status=status.HTTP_201_CREATED)

class WarningListView(APIView):
    """
    API para obtener la lista de todas las advertencias disponibles.
    """
    def get(self, request):
        warning_list = WarningList.objects.all()
        serializer = WarningListSerializer(warning_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
