from rest_framework import serializers
from .models import Customer, AddressO, AddressD, Load, Stop, EquipmentType, Job_Type, OfferHistory

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
    origin = AddressOSerializer()
    destiny = AddressDSerializer()
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    stops = StopSerializer(many=True)

    class Meta:
        model = Load
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['customer'] = CustomerSerializer(instance.customer).data
        return representation

    def create(self, validated_data):
        origin_data = validated_data.pop('origin')
        destiny_data = validated_data.pop('destiny')
        stops_data = validated_data.pop('stops', [])
        customer = validated_data.pop('customer')

        origin = AddressO.objects.create(**origin_data)
        destiny = AddressD.objects.create(**destiny_data)

        load = Load.objects.create(origin=origin, destiny=destiny, customer=customer, **validated_data)

        for stop_data in stops_data:
            Stop.objects.create(load=load, **stop_data)

        return load

    def update(self, instance, validated_data):
        origin_data = validated_data.pop('origin', None)
        destiny_data = validated_data.pop('destiny', None)
        stops_data = validated_data.pop('stops', None)

        if origin_data:
            origin_instance = instance.origin
            for attr, value in origin_data.items():
                setattr(origin_instance, attr, value)
            origin_instance.save()

        if destiny_data:
            destiny_instance = instance.destiny
            for attr, value in destiny_data.items():
                setattr(destiny_instance, attr, value)
            destiny_instance.save()

        if stops_data:
            instance.stops.all().delete()
            for stop_data in stops_data:
                Stop.objects.create(load=instance, **stop_data)

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
