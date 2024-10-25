from django.contrib import admin
from .models import Customer, AddressO, AddressD, Load, Stop, EquipmentType, Job_Type

admin.site.register(Customer)
admin.site.register(AddressO)
admin.site.register(AddressD)
admin.site.register(Load)
admin.site.register(Stop)
admin.site.register(EquipmentType)
admin.site.register(Job_Type)
