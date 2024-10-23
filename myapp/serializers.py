from rest_framework import serializers
from .models import Load, Customer, AddressO, AddressD

class AddressOSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressO
        fields = '__all__'

class AddressDSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressD
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressOSerializer()

    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = AddressO.objects.create(**address_data)
        customer = Customer.objects.create(address=address, **validated_data)
        return customer

    def update(self, instance, validated_data):
        # Extract nested address data
        address_data = validated_data.pop('address', None)
        if address_data:
            # Update address instance
            address_instance = instance.address
            for attr, value in address_data.items():
                setattr(address_instance, attr, value)
            address_instance.save()

        # Update other customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class LoadSerializer(serializers.ModelSerializer):
    origin = AddressOSerializer()
    destiny = AddressDSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Load
        fields = '__all__'

    def create(self, validated_data):
        # Extract nested data for origin, destiny, and customer
        origin_data = validated_data.pop('origin')
        destiny_data = validated_data.pop('destiny')
        customer_data = validated_data.pop('customer')

        # Create nested objects
        origin = AddressO.objects.create(**origin_data)
        destiny = AddressD.objects.create(**destiny_data)
        customer = CustomerSerializer.create(CustomerSerializer(), validated_data=customer_data)

        # Create and return Load instance
        load = Load.objects.create(origin=origin, destiny=destiny, customer=customer, **validated_data)
        return load

    def update(self, instance, validated_data):
        # Extract nested data
        origin_data = validated_data.pop('origin', None)
        destiny_data = validated_data.pop('destiny', None)
        customer_data = validated_data.pop('customer', None)

        # Update nested origin if data is provided
        if origin_data:
            origin_instance = instance.origin
            for attr, value in origin_data.items():
                setattr(origin_instance, attr, value)
            origin_instance.save()

        # Update nested destiny if data is provided
        if destiny_data:
            destiny_instance = instance.destiny
            for attr, value in destiny_data.items():
                setattr(destiny_instance, attr, value)
            destiny_instance.save()

        # Update nested customer if data is provided
        if customer_data:
            customer_instance = instance.customer
            for attr, value in customer_data.items():
                setattr(customer_instance, attr, value)
            customer_instance.save()

        # Update the rest of the Load fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

