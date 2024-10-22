from rest_framework import viewsets
from .models import Load, Customer, AddressO, AddressD
from .serializers import LoadSerializer, CustomerSerializer, AddressOSerializer, AddressDSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class AddressOViewSet(viewsets.ModelViewSet):
    queryset = AddressO.objects.all()
    serializer_class = AddressOSerializer

class AddressDViewSet(viewsets.ModelViewSet):
    queryset = AddressD.objects.all()
    serializer_class = AddressDSerializer

class LoadViewSet(viewsets.ModelViewSet):
    queryset = Load.objects.all()
    serializer_class = LoadSerializer
