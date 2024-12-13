from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from myapp.views import (
    AssignRoleView,
    LoadStopsView,
    OfferHistoryView,
    RegisterView,
    WarningViewSet,
    StopViewSet,
    CustomerViewSet,
    LoadViewSet,
    EquipmentTypeViewSet,
    UserLoadStatistics,
    ReservedLoadsView,
    UserAssignedLoadsView,
    LoadWarningsView,
    AddWarningToLoadView,
    WarningListView,
)

# Registrar los viewsets en el router
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'loads', LoadViewSet, basename='loads')
router.register(r'stops', StopViewSet, basename='stops')
router.register(r'equipment-types', EquipmentTypeViewSet, basename='equipment-types')
router.register(r'warnings', WarningViewSet, basename='warnings')

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
    path('api/loads/<int:load_id>/offers/', OfferHistoryView.as_view(), name='load-offers'),
    path('api/loads/offers/<int:offer_id>/', OfferHistoryView.as_view(), name='offer-detail'),
    path('api/loads/offers/<int:offer_id>/<str:action>/', OfferHistoryView.as_view(), name='offer-action'),
    path('api/loads/offers/', OfferHistoryView.as_view(), name='all-offers'),

    # Endpoint para estadísticas de cargas del usuario autenticado
    path('api/user-load-statistics/', UserLoadStatistics.as_view(), name='user-load-statistics'),

    # Endpoints adicionales
    path('api/loads/reserved/', ReservedLoadsView.as_view(), name='reserved-loads'),
    path('api/loads/assigned-to-user/', UserAssignedLoadsView.as_view(), name='user-assigned-loads'),
    path('api/loads/<int:load_id>/warnings/', LoadWarningsView.as_view(), name='load-warnings'),
    path('api/loads/<int:load_id>/add-warning/', AddWarningToLoadView.as_view(), name='add-warning-to-load'),
    path('api/warnings-list/', WarningListView.as_view(), name='warning-list'),

    # Endpoints de autenticación
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestión de usuarios y roles
    path('register/', RegisterView.as_view(), name='register'),
    path('assign-role/', AssignRoleView.as_view(), name='assign-role'),
]