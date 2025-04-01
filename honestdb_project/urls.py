from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from myapp import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from myapp.views import (
    AssignLoadWithoutOfferView,
    AssignRoleView,
    CarrierUserViewSet,
    ClosedLoadsView,
    DelayView,
    ExcelUploadView,
    LoadStopsView,
    OfferHistoryView,
    RegisterView,
    UnderReviewLoadsView,
    UserPermissionViewSet,
    WarningViewSet,
    StopViewSet,
    CustomerViewSet,
    LoadViewSet,
    EquipmentTypeView,
    UserLoadStatistics,
    ReservedLoadsView,
    UserAssignedLoadsView,
    LoadWarningsView,
    AddWarningToLoadView,
    WarningListView,
    RegisterProgressView,
    LoadProgressListView,
    TruckViewSet,
    UserViewSet,
    UpdateLoadProgressView,
    CloseLoadView,
    ClosedLoadsView,
    ExcelUploadView,
    UnderReviewLoadsView,
    UploadLoadImageView
)
from django.conf import settings
from django.conf.urls.static import static

# Registrar los viewsets en el router
router = DefaultRouter()
router.register(r'user-permissions', UserPermissionViewSet, basename='user-permissions')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'loads', LoadViewSet, basename='loads')
router.register(r'stops', StopViewSet, basename='stops')
router.register(r'warnings', WarningViewSet, basename='warnings')
router.register(r'trucks', TruckViewSet, basename='trucks')
router.register(r'users', UserViewSet, basename='users')
router.register(r'carrier-users', CarrierUserViewSet, basename='carrieruser')


# Definir las rutas adicionales para vistas personalizadas
urlpatterns = [
    # Redirección de la raíz (/) al panel de administración
    path('', RedirectView.as_view(url='/admin/', permanent=True)),

    # Admin
    path('admin/', admin.site.urls),

    # API REST usando el router
    path('api/', include(router.urls)),

    # Rutas para EquipmentTypeView
    path('api/equipment-types/', EquipmentTypeView.as_view(), name='equipment-types-list-create'),
    path('api/equipment-types/<int:pk>/', EquipmentTypeView.as_view(), name='equipment-types-detail'),

    # Rutas específicas para operaciones personalizadas de cargas y paradas
    path('api/loads/<int:load_id>/stops/', LoadStopsView.as_view(), name='load-stops'),
    path('api/loads/<int:load_id>/stops/<int:stop_id>/', LoadStopsView.as_view(), name='edit-stop'),

    # Ruta personalizada para obtener las paradas de una carga específica
    path('api/stops/load/<int:load_id>/', StopViewSet.as_view({'get': 'stops_by_load'}), name='stops-by-load'),

    # Rutas para gestionar ofertas
    path('api/loads/<int:load_id>/offers/', OfferHistoryView.as_view(), name='load-offers'),
    path('api/loads/offers/<int:offer_id>/', OfferHistoryView.as_view(), name='offer-detail'),
    path('api/loads/offers/<int:offer_id>/<str:action>/', OfferHistoryView.as_view(), name='offer-action'),
    path('api/loads/offers/', OfferHistoryView.as_view(), name='all-offers'),

    # Endpoint para estadísticas de cargas del usuario autenticado
    path('api/user-load-statistics/', UserLoadStatistics.as_view(), name='user-load-statistics'),

    # Endpoints adicionales
    path('api/loads/reserved/', ReservedLoadsView.as_view(), name='reserved-loads'),
    path('api/assigned-loads/', UserAssignedLoadsView.as_view(), name='assigned-loads'),
    path('api/loads/<int:load_id>/warnings/', LoadWarningsView.as_view(), name='load-warnings'),
    path('api/loads/<int:load_id>/add-warning/', AddWarningToLoadView.as_view(), name='add-warning-to-load'),
    path('api/loads/<int:load_id>/warnings/<int:warning_id>/', LoadWarningsView.as_view(), name='delete-load-warning'),
    path('api/warnings-list/', WarningListView.as_view(), name='warning-list'),
    path('api/upload-excel/', ExcelUploadView.as_view(), name='upload-excel'),
    path('api/loads/under-review/', LoadViewSet.as_view({'get': 'under_review_loads'}), name='under-review-loads'),
    path('api/loads/<int:load_id>/under-review/', UnderReviewLoadsView.as_view(), name='update-under-review-load'),
    path('api/image-load/', UploadLoadImageView.as_view(), name='upload-load'),
    # Rutas para progreso de carga
    path('api/load-progress/<int:load_id>/', RegisterProgressView.as_view(), name='register-progress'),
    path('api/load-progress-list/<int:load_id>/', LoadProgressListView.as_view(), name='load-progress-list'),

    # Endpoints de autenticación usando JWT
    path('api/loads/load-progress/<int:load_id>/<str:step>/update/', UpdateLoadProgressView.as_view(), name='update-load-progress'),
    path('api/loads/<int:load_id>/close/', CloseLoadView.as_view(), name='close_load'),

    # Endpoints de autenticación
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestión de usuarios y roles
    path('register/', RegisterView.as_view(), name='register'),
    path('assign-role/', AssignRoleView.as_view(), name='assign-role'),

    # Aceptar carga sin ofertar
    path('api/loads/<int:load_id>/assign-without-offer/', AssignLoadWithoutOfferView.as_view(), name='assign-load-without-offer'),

    # Adicionales para csv y excel
    path('api/upload-excel/', ExcelUploadView.as_view(), name='upload-excel'),
    path('api/loads/under-review/', LoadViewSet.as_view({'get': 'under_review_loads'}), name='under-review-loads'),
    path('api/loads/<int:load_id>/under-review/', UnderReviewLoadsView.as_view(), name='update-under-review-load'),

    # Cargas cerradas 
    path('api/closed-loads/', ClosedLoadsView.as_view(), name='closed-loads'),

    # Delay en los Stops
    path('api/stops/<int:stop_id>/delays/', DelayView.as_view(), name='delay-list-create'),

    # Formularios Personalizados
    path('register/carrier-employee/', views.register_carrier_employee, name='register_carrier_employee'),

]

# Agregar soporte para archivos estáticos y de medios
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('/progress_pictures/', document_root=settings.BASE_DIR / 'progress_pictures')
