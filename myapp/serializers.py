from datetime import timezone
from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import serializers
from django.apps import apps
from .models import (
    CarrierUser, Customer, AddressO, AddressD, Load, Role, Stop,
    EquipmentType, Job_Type, OfferHistory, Warning
)


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
        """Custom validations."""
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
        fields = '__all__'


class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = '__all__'


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
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'DOT_number', 'carrier_type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if CarrierUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
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


class UserDetailSerializer(serializers.ModelSerializer):
    role = RoleSerializer()  # Include role details

    class Meta:
        model = CarrierUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'DOT_number', 'role']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierUser
        fields = ['first_name', 'last_name', 'phone', 'DOT_number']
