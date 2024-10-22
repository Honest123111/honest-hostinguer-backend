from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'addressos', views.AddressOViewSet)
router.register(r'addressds', views.AddressDViewSet)
router.register(r'loads', views.LoadViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
