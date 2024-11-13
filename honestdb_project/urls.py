from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp import views
from myapp.views import LoadStopsView, OfferHistoryView

# Registrar los viewsets en el router
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'loads', views.LoadViewSet)
router.register(r'stops', views.StopViewSet)
router.register(r'equipment-types', views.EquipmentTypeViewSet)

# Definir las rutas adicionales para vistas personalizadas
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Rutas para los viewsets registrados en el router
    path('api/loads/<int:load_id>/stops/', LoadStopsView.as_view(), name='load-stops'),  # Ruta para manejar los stops de un load específico
    path('api/loads/<int:load_id>/stops/<int:stop_id>/', LoadStopsView.as_view(), name='edit-stop'),  # Ruta para editar/eliminar un stop específico
    path('api/loads/<int:load_id>/offers/', OfferHistoryView.as_view(), name='load-offers'),  # Ruta para manejar el historial de ofertas de un load
]
