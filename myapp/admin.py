from django.contrib import admin
from .models import Load, Customer, AddressO, AddressD

admin.site.register(Customer)
admin.site.register(AddressO)
admin.site.register(AddressD)
admin.site.register(Load)
