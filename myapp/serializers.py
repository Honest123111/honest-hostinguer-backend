from django.contrib.auth.models import Group
from rest_framework import serializers
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
    status = serializers.CharField(required=False, default='pending')  # Establecer 'pending' por defecto
    priority = serializers.ChoiceField(choices=Load.PRIORITY_CHOICES, default='medium')  # Prioridad
    created_at = serializers.DateTimeField(read_only=True)  # Solo lectura
    updated_at = serializers.DateTimeField(read_only=True)  # Solo lectura

    class Meta:
        model = Load
        fields = '__all__'

    def to_representation(self, instance):
        # Personalizamos la representación para incluir el customer como un objeto completo
        representation = super().to_representation(instance)
        representation['customer'] = CustomerSerializer(instance.customer).data
        representation['origin'] = AddressOSerializer(instance.origin).data
        representation['destiny'] = AddressDSerializer(instance.destiny).data
        representation['stops'] = StopSerializer(instance.stops.all(), many=True).data
        return representation

    def create(self, validated_data):
        # Extraemos y eliminamos los datos de las relaciones
        origin_data = validated_data.pop('origin')
        destiny_data = validated_data.pop('destiny')
        stops_data = validated_data.pop('stops', [])
        customer = validated_data.pop('customer')
        status = validated_data.pop('status', 'pending')  # Default status is 'pending'
        priority = validated_data.pop('priority', 'medium')  # Default priority is 'medium'

        # Creamos las instancias de los modelos relacionados
        origin = AddressO.objects.create(**origin_data)
        destiny = AddressD.objects.create(**destiny_data)

        # Creamos la carga
        load = Load.objects.create(
            origin=origin, destiny=destiny, customer=customer, status=status, priority=priority, **validated_data
        )

        # Creamos los "stops" relacionados con la carga
        for stop_data in stops_data:
            Stop.objects.create(load=load, **stop_data)

        return load

    def update(self, instance, validated_data):
        # Actualización de relaciones
        origin_data = validated_data.pop('origin', None)
        destiny_data = validated_data.pop('destiny', None)
        stops_data = validated_data.pop('stops', None)
        priority = validated_data.pop('priority', None)  # Se actualiza el campo de prioridad

        # Actualización de 'origin' si los datos están presentes
        if origin_data:
            origin_instance = instance.origin
            for attr, value in origin_data.items():
                setattr(origin_instance, attr, value)
            origin_instance.save()

        # Actualización de 'destiny' si los datos están presentes
        if destiny_data:
            destiny_instance = instance.destiny
            for attr, value in destiny_data.items():
                setattr(destiny_instance, attr, value)
            destiny_instance.save()

        # Actualización de 'stops' si los datos están presentes
        if stops_data:
            instance.stops.clear()  # Eliminamos los stops actuales
            for stop_data in stops_data:
                Stop.objects.create(load=instance, **stop_data)  # Creamos los nuevos stops

        # Actualizamos los campos restantes del load, incluido el campo de prioridad
        if priority:
            instance.priority = priority

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

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
        fields = '__all__'


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
