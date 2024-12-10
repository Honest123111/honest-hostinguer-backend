from django.contrib import admin
from .models import (
    CarrierUser, Customer, AddressO, AddressD, Load, Role, Stop,
    EquipmentType, Job_Type, OfferHistory, ProcessedEmail, Warning,WarningList
)

admin.site.register(Customer)
admin.site.register(AddressO)
admin.site.register(AddressD)
admin.site.register(Stop)
admin.site.register(EquipmentType)
admin.site.register(Job_Type)
admin.site.register(OfferHistory)
admin.site.register(ProcessedEmail)
admin.site.register(WarningList)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['permissions']  # Para gestionar permisos en la interfaz

@admin.register(CarrierUser)
class CarrierUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'carrier_type', 'is_active']
    list_filter = ['carrier_type', 'is_active']
    search_fields = ['username', 'email']

@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_description', 'created_at', 'updated_at')

    def get_description(self, obj):
        return obj.warning_type.description
    get_description.short_description = 'Description'

@admin.register(Load)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('idmmload', 'status', 'priority', 'is_reserved')
    filter_horizontal = ('warnings',)  # Agrega un selector para advertencias
