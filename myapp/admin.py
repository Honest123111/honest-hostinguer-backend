from django.contrib import admin
from .models import CarrierUser, Customer, AddressO, AddressD, Load, Role, Stop, EquipmentType, Job_Type,OfferHistory,ProcessedEmail

admin.site.register(Customer)
admin.site.register(AddressO)
admin.site.register(AddressD)
admin.site.register(Load)
admin.site.register(Stop)
admin.site.register(EquipmentType)
admin.site.register(Job_Type)
admin.site.register(OfferHistory)
admin.site.register(ProcessedEmail)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['permissions']  # Para gestionar permisos en la interfaz

@admin.register(CarrierUser)
class CarrierUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'carrier_type', 'is_active']  # Ajusta según los campos actuales
    list_filter = ['carrier_type', 'is_active']  # Cambia 'role' por 'carrier_type' o elimina si no necesitas filtros
    search_fields = ['username', 'email']  # Campos para búsqueda