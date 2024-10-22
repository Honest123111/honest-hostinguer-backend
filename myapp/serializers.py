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

class LoadSerializer(serializers.ModelSerializer):
    origin = AddressOSerializer()
    destiny = AddressDSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Load
        fields = '__all__'
