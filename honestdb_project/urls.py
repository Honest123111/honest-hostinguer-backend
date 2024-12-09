from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from myapp.views import (
    AssignRoleView,
    LoadStopsView,
    OfferHistoryView,
    RegisterView,
    WarningViewSet,
    StopViewSet,
)

# Registrar los viewsets en el router
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'loads', views.LoadViewSet)
router.register(r'stops', StopViewSet)  # Registrar el StopViewSet
router.register(r'equipment-types', views.EquipmentTypeViewSet)
router.register(r'warnings', WarningViewSet)

# Definir las rutas adicionales para vistas personalizadas
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API REST usando el router
    path('api/', include(router.urls)),

    # Rutas específicas para operaciones personalizadas
    path('api/loads/<int:load_id>/stops/', LoadStopsView.as_view(), name='load-stops'),
    path('api/loads/<int:load_id>/stops/<int:stop_id>/', LoadStopsView.as_view(), name='edit-stop'),

    # Ruta personalizada para obtener las paradas de una carga específica
    path(
        'api/stops/load/<int:load_id>/',
        StopViewSet.as_view({'get': 'stops_by_load'}),
        name='stops-by-load',
    ),

    # Rutas para gestionar ofertas
    path('api/loads/<int:load_id>/offers/', OfferHistoryView.as_view(), name='offer-history'),

    # Endpoints de autenticación
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestión de usuarios y roles
    path('register/', RegisterView.as_view(), name='register'),
    path('assign-role/', AssignRoleView.as_view(), name='assign_role'),
]
