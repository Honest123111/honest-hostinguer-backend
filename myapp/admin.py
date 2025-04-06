from django.contrib import admin
from .models import (
    CarrierAdminProfile, CarrierEmployeeProfile, CarrierUser, Corporation, Customer, AddressO, AddressD, Load, Role, Stop,
    EquipmentType, Job_Type, OfferHistory, ProcessedEmail, Warning,WarningList,LoadProgress,Truck
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
admin.site.register(LoadProgress)
admin.site.register(Truck)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['permissions']  # Para gestionar permisos en la interfaz

@admin.register(CarrierUser)
class CarrierUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'carrier_type', 'number_of_trucks', 'created_at')
    search_fields = ('username', 'email', 'carrier_type')
    list_filter = ('carrier_type',)
    ordering = ('created_at',)

    def delete_queryset(self, request, queryset):
        """Método para eliminar varios usuarios desde Django Admin"""
        for user in queryset:
            user.delete_user()

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

@admin.register(CarrierEmployeeProfile)
class CarrierEmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'status', 'start_date', 'termination_date')
    list_filter = ('position', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

@admin.register(Corporation)
class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dot_number', 'city', 'state', 'zip_code', 'phone_number')
    search_fields = ('name', 'dot_number', 'city', 'state')
    list_filter = ('state',)
    ordering = ('name',)

@admin.register(CarrierAdminProfile)
class CarrierAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'corporation', 'get_customer', 'status', 'start_date', 'termination_date')
    list_filter = ('role', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

    def get_customer(self, obj):
        return obj.customer.name if obj.customer else '-'
    
    get_customer.short_description = 'Customer'
