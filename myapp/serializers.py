from datetime import timezone
from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import serializers

from django.apps import apps
from .models import CarrierUser, Customer, AddressO, AddressD, Load, Role, Stop, EquipmentType, Job_Type, OfferHistory

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class AddressOSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressO
        fields = '__all__'


class AddressDSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressD
        fields = '__all__'


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = '__all__'


class LoadSerializer(serializers.ModelSerializer):
    # Relaciones con otros modelos
    origin = AddressOSerializer()
    destiny = AddressDSerializer()
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    stops = StopSerializer(many=True)
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentType.objects.all(), allow_null=True, required=False
    )
    assigned_user = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model(settings.AUTH_USER_MODEL).objects.all(),
        allow_null=True,
        required=False
    )

    # Campos adicionales
    status = serializers.CharField(required=False, default='pending')  # Default 'pending'
    priority = serializers.ChoiceField(choices=Load.PRIORITY_CHOICES, default='medium')  # Default 'medium'
    tracking_status = serializers.ChoiceField(choices=Load.TRACKING_CHOICES, required=False, default='not_started')
    expiration_date = serializers.DateTimeField(required=False, allow_null=True)
    current_location = serializers.CharField(required=False, allow_null=True)
    payment_status = serializers.ChoiceField(
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending',
        required=False,
    )
    is_reserved = serializers.BooleanField(read_only=True)  # Solo lectura
    created_at = serializers.DateTimeField(read_only=True)  # Solo lectura
    updated_at = serializers.DateTimeField(read_only=True)  # Solo lectura

    class Meta:
        model = Load
        fields = '__all__'

    def to_representation(self, instance):
        """Personalizamos la representación para incluir datos completos de relaciones."""
        representation = super().to_representation(instance)
        representation['customer'] = CustomerSerializer(instance.customer).data
        representation['origin'] = AddressOSerializer(instance.origin).data
        representation['destiny'] = AddressDSerializer(instance.destiny).data
        representation['stops'] = StopSerializer(instance.stops.all(), many=True).data
        representation['assigned_user'] = (
            instance.assigned_user.username if instance.assigned_user else None
        )
        if instance.equipment:
            representation['equipment'] = EquipmentType.objects.get(idmmequipment=instance.equipment.idmmequipment).name
        return representation

    def create(self, validated_data):
        """Crear una nueva carga y sus relaciones."""
        origin_data = validated_data.pop('origin')
        destiny_data = validated_data.pop('destiny')
        stops_data = validated_data.pop('stops', [])
        customer = validated_data.pop('customer')

        # Crear las instancias relacionadas
        origin = AddressO.objects.create(**origin_data)
        destiny = AddressD.objects.create(**destiny_data)

        # Crear la carga
        load = Load.objects.create(
            origin=origin, destiny=destiny, customer=customer, **validated_data
        )

        # Crear los stops relacionados
        for stop_data in stops_data:
            Stop.objects.create(load=load, **stop_data)

        return load

    def update(self, instance, validated_data):
        """Actualizar una carga existente y sus relaciones."""
        origin_data = validated_data.pop('origin', None)
        destiny_data = validated_data.pop('destiny', None)
        stops_data = validated_data.pop('stops', None)

        # Verificar si la carga está reservada antes de permitir ciertos cambios
        if instance.is_reserved:
            raise serializers.ValidationError("Cannot modify a reserved load.")

        # Actualizar origen
        if origin_data:
            origin_instance = instance.origin
            for attr, value in origin_data.items():
                setattr(origin_instance, attr, value)
            origin_instance.save()

        # Actualizar destino
        if destiny_data:
            destiny_instance = instance.destiny
            for attr, value in destiny_data.items():
                setattr(destiny_instance, attr, value)
            destiny_instance.save()

        # Actualizar stops
        if stops_data:
            instance.stops.clear()  # Eliminar stops actuales
            for stop_data in stops_data:
                Stop.objects.create(load=instance, **stop_data)

        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def validate(self, data):
        """Validaciones personalizadas."""
        if data.get('expiration_date') and data['expiration_date'] < timezone.now():
            raise serializers.ValidationError("Expiration date cannot be in the past.")
        return data
class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = '__all__'


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Type
        fields = '__all__'


class OfferHistorySerializer(serializers.ModelSerializer):
     class Meta:
        model = OfferHistory
        exclude = ['user']  # Excluir el campo para que no se envíe en la solicitud

        def create(self, validated_data):
            # Asignar automáticamente el usuario logueado al crear la oferta
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['user'] = request.user
            return super().create(validated_data)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']

class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not CarrierUser.objects.filter(id=value).exists():
            raise serializers.ValidationError("El usuario con este ID no existe.")
        return value

    def validate_role_id(self, value):
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError("El rol con este ID no existe.")
        return value

    def update(self, instance, validated_data):
        user = CarrierUser.objects.get(id=validated_data['user_id'])
        role = Role.objects.get(id=validated_data['role_id'])
        user.role = role
        user.save()
        return user
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'DOT_number', 'carrier_type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if CarrierUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def create(self, validated_data):
        user = CarrierUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone=validated_data.get('phone'),
            DOT_number=validated_data.get('DOT_number'),
            carrier_type=validated_data.get('carrier_type')
        )
        carrier_group, _ = Group.objects.get_or_create(name="Carrier")
        user.groups.add(carrier_group)
        return user
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']

    permissions = serializers.StringRelatedField(many=True)

class UserDetailSerializer(serializers.ModelSerializer):
    role = RoleSerializer()  # Incluye los detalles del rol

    class Meta:
        model = CarrierUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'DOT_number', 'role']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierUser
        fields = ['first_name', 'last_name', 'phone', 'DOT_number']
