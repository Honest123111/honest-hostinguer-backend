from datetime import timezone
from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.apps import apps
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import (
    CarrierAdminProfile, CarrierEmployeeProfile, CarrierUser, Corporation, Customer, AddressO, AddressD, Delay, Load, Role, Stop,
    EquipmentType, Job_Type, OfferHistory, UserPermission, Warning,WarningList,LoadProgress,Truck
)
from datetime import datetime

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class CorporationSerializer(serializers.ModelSerializer):
    contacts = CustomerSerializer(many=True, read_only=True)

    class Meta:
        model = Corporation
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
        fields = ['load', 'location', 'date_time', 'action_type', 'estimated_weight', 'quantity', 'coordinates', 'loaded_on']
        read_only_fields = ['loaded_on']

    def validate_date_time(self, value):
        if value is None:
            raise serializers.ValidationError("The `date_time` field is required.")
        return value

class LoadSerializer(serializers.ModelSerializer):
    # Nested serializers for related fields
    origin = AddressOSerializer()
    destiny = AddressDSerializer()
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    stops = StopSerializer(many=True, read_only=True)
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentType.objects.all(), allow_null=True, required=False
    )
    warnings = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Warning.objects.all(), required=False
    )
    assigned_user = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model(settings.AUTH_USER_MODEL).objects.all(),
        allow_null=True,
        required=False
    )

    # Additional fields
    status = serializers.CharField(required=False, default='pending')  # Default 'pending'
    priority = serializers.ChoiceField(choices=Load.PRIORITY_CHOICES, default='medium')
    tracking_status = serializers.ChoiceField(choices=Load.TRACKING_CHOICES, required=False, default='not_started')
    expiration_date = serializers.DateTimeField(required=False, allow_null=True)
    current_location = serializers.CharField(required=False, allow_null=True)
    is_closed = serializers.BooleanField(required=False, default=False) 
    payment_status = serializers.ChoiceField(
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending',
        required=False,
    )
    is_reserved = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Load
        fields = '__all__'

    def to_representation(self, instance):
        """Customize representation for related objects."""
        representation = super().to_representation(instance)
        representation['origin'] = AddressOSerializer(instance.origin).data
        representation['destiny'] = AddressDSerializer(instance.destiny).data
        representation['customer'] = CustomerSerializer(instance.customer).data
        representation['stops'] = StopSerializer(instance.stops.all(), many=True).data
        representation['is_closed'] = instance.is_closed 
        if instance.equipment:
            representation['equipment'] = {
                'id': instance.equipment.idmmequipment,
                'name': instance.equipment.name
            }
        representation['warnings'] = [
            {'id': warning.id, 'description': warning.description}
            for warning in instance.warnings.all()
        ]
        representation['assigned_user'] = (
            instance.assigned_user.username if instance.assigned_user else None
        )
        return representation

    def create(self, validated_data):
        """Create a new load with related objects."""
        origin_data = validated_data.pop('origin')
        destiny_data = validated_data.pop('destiny')
        stops_data = validated_data.pop('stops', [])
        warnings_data = validated_data.pop('warnings', [])

        # Create related objects
        origin = AddressO.objects.create(**origin_data)
        destiny = AddressD.objects.create(**destiny_data)

        # Create the load
        load = Load.objects.create(origin=origin, destiny=destiny, **validated_data)

        # Add stops to the load
        for stop_data in stops_data:
            Stop.objects.create(load=load, **stop_data)

        # Set warnings for the load
        load.warnings.set(warnings_data)

        return load

    def update(self, instance, validated_data):
        """Update a load and its related objects."""
        origin_data = validated_data.pop('origin', None)
        destiny_data = validated_data.pop('destiny', None)
        stops_data = validated_data.pop('stops', None)
        warnings_data = validated_data.pop('warnings', None)

        # Update origin
        if origin_data:
            for attr, value in origin_data.items():
                setattr(instance.origin, attr, value)
            instance.origin.save()

        # Update destiny
        if destiny_data:
            for attr, value in destiny_data.items():
                setattr(instance.destiny, attr, value)
            instance.destiny.save()

        # Update stops
        if stops_data:
            instance.stops.all().delete()  # Clear existing stops
            for stop_data in stops_data:
                Stop.objects.create(load=instance, **stop_data)

        # Update warnings
        if warnings_data:
            instance.warnings.set(warnings_data)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def validate(self, data):
        """Validaciones personalizadas."""

        # Validación para asegurar que la fecha de expiración no esté en el pasado
        if data.get('expiration_date') and data['expiration_date'] < timezone.now():
            raise serializers.ValidationError("Expiration date cannot be in the past.")

        # Validación para asegurar que el usuario no tenga más cargas asignadas que camiones
        assigned_user = data.get('assigned_user')
        if assigned_user:
            # Contar las cargas en estado 'pending' o 'in_progress'
            assigned_loads_count = Load.objects.filter(
                assigned_user=assigned_user,
                status__in=['pending', 'in_progress']
            ).count()

            # Comparar con la cantidad de camiones registrados por el usuario
            if assigned_loads_count >= assigned_user.trucks.count():
                raise serializers.ValidationError(
                    "The user cannot be assigned more loads than the number of trucks they own."
                )

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
    user = serializers.StringRelatedField()  # Devuelve str(user)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(f'{value} is not a valid amount. The amount must be positive.')
        return value

    def validate(self, data):
        load = data.get('load')
        amount = data.get('amount')

        if load and amount:
            previous_accepted_offers = load.offer_history.filter(status='accepted')
            if previous_accepted_offers.exists():
                last_accepted = previous_accepted_offers.latest('date')
                if amount < last_accepted.amount:
                    raise serializers.ValidationError(
                        'Offer amount cannot be lower than previously accepted offers.'
                    )

        return data

    def create(self, validated_data):
        # Puedes agregar lógica extra aquí si necesitas
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Actualizar campos relevantes
        instance.amount = validated_data.get('amount', instance.amount)
        instance.proposed_pickup_date = validated_data.get('proposed_pickup_date', instance.proposed_pickup_date)
        instance.proposed_pickup_time = validated_data.get('proposed_pickup_time', instance.proposed_pickup_time)
        instance.proposed_delivery_date = validated_data.get('proposed_delivery_date', instance.proposed_delivery_date)
        instance.proposed_delivery_time = validated_data.get('proposed_delivery_time', instance.proposed_delivery_time)

        # Si alguno de los campos relevantes cambió, marcar términos modificados
        instance.terms_change = True
        instance.save()
        return instance

    class Meta:
        model = OfferHistory
        fields = [
            'id', 'load', 'user', 'amount', 'status', 'date', 'terms_change',
            'proposed_pickup_date', 'proposed_pickup_time',
            'proposed_delivery_date', 'proposed_delivery_time'
        ]
        read_only_fields = ['id', 'status', 'date', 'terms_change']

class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = '__all__'

class WarningListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarningList
        fields = ['id', 'description', 'issue_level', 'is_active', 'created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']


class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not CarrierUser.objects.filter(id=value).exists():
            raise serializers.ValidationError("The user with this ID does not exist.")
        return value

    def validate_role_id(self, value):
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError("The role with this ID does not exist.")
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
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'DOT_number', 'carrier_type']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if CarrierUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        # Usa el email como username
        user = CarrierUser.objects.create_user(
            username=validated_data['email'],  # ✅ importante
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone=validated_data.get('phone'),
            DOT_number=validated_data.get('DOT_number'),
            carrier_type=validated_data.get('carrier_type', 'us')
        )

        # Asignar grupo específico (Carrier Employee)
        carrier_group, _ = Group.objects.get_or_create(name="Carrier Employee")
        user.groups.set([carrier_group])  # ✅ solo ese grupo

        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CarrierUser.objects.get(email=value)
            self.context['user'] = user
        except CarrierUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        user = self.context['user']
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # URL de frontend (ajústalo según tu entorno)
        reset_url = f"https://honesttransportationfront.web.app/reset-password/{uid}/{token}"

        send_mail(
            subject="Password Reset",
            message=f"Click the link below to reset your password:\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class UserDetailSerializer(serializers.ModelSerializer):
    role = RoleSerializer()  # Include role details

    class Meta:
        model = CarrierUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'DOT_number', 'role']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierUser
        fields = ['first_name', 'last_name', 'phone', 'DOT_number']

class LoadProgressSerializer(serializers.ModelSerializer):
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = LoadProgress
        fields = ['idmmload', 'coordinates', 'step', 'picture', 'pending_for_approval', 'picture_url']

    def create(self, validated_data):
        # Manejar el campo idmmload correctamente
        load = validated_data.pop('idmmload')
        progress = LoadProgress.objects.create(idmmload=load, **validated_data)
        return progress

    def get_picture_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.picture.url)
        return obj.picture.url
class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = ['id', 'user', 'plate_number', 'model', 'equipment_type']

class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = '__all__'


class DelaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delay
        fields = '__all__'

class CarrierUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierUser
        fields = '__all__'

from .models import CarrierEmployeeProfile, CarrierUser, Role
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from datetime import datetime

class CarrierEmployeeSerializer(serializers.ModelSerializer):
    # Campos del usuario (CarrierUser)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    # Campos adicionales
    position = serializers.ChoiceField(choices=CarrierEmployeeProfile.POSITION_CHOICES)
    start_date = serializers.SerializerMethodField()
    termination_date = serializers.SerializerMethodField()

    # Nuevo campo de rol
    role = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Role.objects.all(),
        required=False
    )

    class Meta:
        model = CarrierEmployeeProfile
        fields = [
            'carrier_employee_id', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'phone', 'position',
            'phone_number', 'extension', 'status', 'start_date', 'termination_date',
            'role'
        ]
        read_only_fields = ['carrier_employee_id', 'status', 'start_date']

    def get_start_date(self, obj):
        return obj.start_date.date() if isinstance(obj.start_date, datetime) else obj.start_date

    def get_termination_date(self, obj):
        return obj.termination_date.date() if isinstance(obj.termination_date, datetime) else obj.termination_date

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password1 = validated_data.pop('password1')
        password2 = validated_data.pop('password2')
        role = validated_data.pop('role', None)

        if password1 != password2:
            raise serializers.ValidationError("Passwords do not match.")

        email = user_data['email']
        if CarrierUser.objects.filter(username=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        user = CarrierUser.objects.create(
            username=email,
            email=email,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            password=make_password(password1)
        )

        # Asignar rol por defecto si no se proporciona
        if not role:
            role = Role.objects.get_or_create(name='Carrier Employee')[0]

        return CarrierEmployeeProfile.objects.create(user=user, role=role, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password1 = validated_data.pop('password1', None)
        password2 = validated_data.pop('password2', None)

        # Actualizar datos del usuario
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError("Passwords do not match.")
            instance.user.password = make_password(password1)

        instance.user.save()

        # Actualizar perfil del empleado
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class CarrierAdminSerializer(serializers.ModelSerializer):
    # Campos del usuario vinculado (CarrierUser)
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    # Relaciones
    corporation = serializers.PrimaryKeyRelatedField(queryset=Corporation.objects.all())
    primary_contact = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), allow_null=True, required=False)

    class Meta:
        model = CarrierAdminProfile
        fields = [
            'id', 'email', 'password1', 'password2', 'first_name', 'last_name',
            'corporation', 'primary_contact',
            'insurance_type', 'insurance_amount', 'insurance_expiration',
            'commodities_excluded', 'cargo_policy_limit', 'trailer_interchange_limit',
            'reefer_breakdown_coverage', 'preferred_lanes', 'insurance_certificate',
            'number_of_drivers', 'number_of_vehicles', 'certifications',
            'status', 'start_date', 'termination_date'
        ]
        read_only_fields = ['status', 'start_date']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        email = user_data['email']
        if CarrierUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        user = CarrierUser(
            username=email,
            email=email,
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name')
        )
        user.set_password(password)
        user.save()

        role, _ = Role.objects.get_or_create(name='Admin Carrier')
        return CarrierAdminProfile.objects.create(user=user, role=role, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password1 = validated_data.pop('password1', None)
        password2 = validated_data.pop('password2', None)

        user = instance.user
        for attr in ['first_name', 'last_name', 'email']:
            if attr in user_data:
                setattr(user, attr, user_data[attr])

        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError("Passwords do not match.")
            user.set_password(password1)

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Asegurar que las fechas sean solo date (no datetime)
        for date_field in ['start_date', 'termination_date', 'insurance_expiration']:
            value = getattr(instance, date_field, None)
            if isinstance(value, datetime):
                rep[date_field] = value.date().isoformat()
            elif value:
                rep[date_field] = value.isoformat()
        return rep
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = CarrierUser.EMAIL_FIELD  # Usa email como username

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agrega info adicional al token si lo deseas
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        # Este paso es importante para asegurar que `email` se use como campo
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)