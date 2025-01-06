from email.headerregistry import Group
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Avg, Sum, Count
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
from django.db import models
from django.shortcuts import get_object_or_404
from .serializers import WarningSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import WarningListSerializer
from .utils import send_email
from .models import Load, LoadProgress
from .serializers import LoadProgressSerializer
from rest_framework.parsers import MultiPartParser, FormParser


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


class EquipmentTypeView(APIView):
    # Obtener todos los tipos de equipo (GET)
    def get(self, request):
        equipment_types = EquipmentType.objects.all()
        serializer = EquipmentTypeSerializer(equipment_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Crear un nuevo tipo de equipo (POST)
    def post(self, request):
        serializer = EquipmentTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar un tipo de equipo existente (PUT)
    def put(self, request, pk):
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except EquipmentType.DoesNotExist:
            return Response({'error': 'Tipo de equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EquipmentTypeSerializer(equipment_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Eliminar un tipo de equipo (DELETE)
    def delete(self, request, pk):
        try:
            equipment_type = EquipmentType.objects.get(pk=pk)
        except EquipmentType.DoesNotExist:
            return Response({'error': 'Tipo de equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        equipment_type.delete()
        return Response({'message': 'Tipo de equipo eliminado'}, status=status.HTTP_204_NO_CONTENT)

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
    permission_classes = [IsAuthenticated]

    def get(self, request, load_id=None):
        """
        Listar todas las ofertas o las ofertas de un `Load` específico.
        """
        if load_id:
            # Filtrar ofertas por `load_id`
            offers = OfferHistory.objects.filter(load_id=load_id)
            if not offers.exists():
                return Response(
                    {"detail": f"No se encontraron ofertas para la carga con ID {load_id}."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            # Devolver todas las ofertas si no se especifica `load_id`
            offers = OfferHistory.objects.all()

        serializer = OfferHistorySerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, load_id):
        """
        Crear una nueva oferta asociada a una carga específica.
        """
        load = get_object_or_404(Load, idmmload=load_id)

        # Validar si el load tiene alguna oferta previa
        if load.is_offerted:
            return Response(
                {"detail": f"La carga {load_id} ya tiene ofertas registradas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OfferHistorySerializer(data=request.data)
        if serializer.is_valid():
            # Asociar la oferta con el usuario autenticado y la carga
            serializer.save(user=request.user, load=load)

            # Actualizar los campos del modelo Load
            load.number_of_offers += 1
            load.is_offerted = True
            load.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, offer_id, action):
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
            return Response({"error": "Acción no válida."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, offer_id):
        """
        Editar una oferta específica.
        """
        offer = get_object_or_404(OfferHistory, id=offer_id)

        # Validar si la oferta ya ha sido aceptada o rechazada
        if offer.status in ['accepted', 'rejected']:
            return Response(
                {"detail": "No se puede editar una oferta ya aceptada o rechazada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar y actualizar la oferta
        serializer = OfferHistorySerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, offer_id):
        """
        Eliminar una oferta específica.
        """
        offer = get_object_or_404(OfferHistory, id=offer_id)

        # Reducir el contador de ofertas en la carga asociada
        load = offer.load
        load.number_of_offers -= 1
        if load.number_of_offers == 0:
            load.is_offerted = False
        load.save()

        # Eliminar la oferta
        offer.delete()
        return Response({"message": "Oferta eliminada con éxito."}, status=status.HTTP_200_OK)
    
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

class UserLoadStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Filtrar cargas asignadas al usuario autenticado
        assigned_loads = Load.objects.filter(assigned_user=user)

        # Estadísticas generales
        total_loads = assigned_loads.count()
        loads_by_status = assigned_loads.values('status').annotate(count=Count('status'))
        equipment_types = assigned_loads.values('equipment_type').annotate(count=Count('equipment_type'))

        # Estadísticas adicionales
        loads_by_priority = assigned_loads.values('priority').annotate(count=Count('priority'))
        loads_by_tracking_status = assigned_loads.values('tracking_status').annotate(count=Count('tracking_status'))
        total_loaded_miles = assigned_loads.aggregate(total_miles=Sum('loaded_miles'))['total_miles']
        total_weight = assigned_loads.aggregate(total_weight=Sum('total_weight'))['total_weight']
        loads_with_warnings = assigned_loads.filter(warnings__isnull=False).distinct().count()
        average_offers_per_load = assigned_loads.aggregate(avg_offers=Avg('number_of_offers'))['avg_offers']

        # Preparar los datos de respuesta
        data = {
            "total_loads": total_loads,
            "loads_by_status": loads_by_status,
            "equipment_types": equipment_types,
            "loads_by_priority": loads_by_priority,
            "loads_by_tracking_status": loads_by_tracking_status,
            "total_loaded_miles": total_loaded_miles,
            "total_weight": total_weight,
            "loads_with_warnings": loads_with_warnings,
            "average_offers_per_load": average_offers_per_load,
        }
        return Response(data)

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
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=401)

        assigned_loads = Load.objects.filter(assigned_user=user)
        if not assigned_loads.exists():
            return Response({"message": "No assigned loads found for this user."}, status=404)

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

class RegisterProgressView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Permitir archivos y datos multipart

    def post(self, request, load_id):
        try:
            # Obtener la carga por ID
            load = Load.objects.get(idmmload=load_id)
        except Load.DoesNotExist:
            return Response({"error": "Load not found"}, status=status.HTTP_404_NOT_FOUND)

        # Combinar los datos y la carga en el request
        data = request.data.copy()
        data['idmmload'] = load.idmmload

        # Serializar los datos
        serializer = LoadProgressSerializer(data=data)
        if serializer.is_valid():
            # Guardar los datos validados
            serializer.save(idmmload=load)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Responder con errores si los datos no son válidos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)