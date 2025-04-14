import os
print("🔥 CARGANDO urls.py en:", os.path.abspath(__file__))

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from myapp.views import (
    AdminCarrier2ViewSet,
    AssignLoadWithoutOfferView,
    AssignRoleView,
    CarrierAdminViewSet,
    CarrierUserActionsViewSet,
    CarrierUserViewSet,
    ClosedLoadsView,
    CorporationViewSet,
    CustomTokenObtainPairView,
    DebugTestViewSet,
    DelayView,
    DispatcherViewSet,
    ExcelUploadView,
    LoadStopsView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ShipperAdminViewSet,
    ShipperEmployeeViewSet,
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
    UploadLoadImageView,
    OfferHistoryViewSet  # ✅ ViewSet actualizado
)

# Routers
router = DefaultRouter()
router.register(r'user-permissions', UserPermissionViewSet, basename='user-permissions')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'corporations', CorporationViewSet, basename='corporations')
router.register(r'loads', LoadViewSet, basename='loads')
router.register(r'trucks', TruckViewSet, basename='trucks')
router.register(r'stops', StopViewSet, basename='stops')
router.register(r'warnings', WarningViewSet, basename='warnings')
router.register(r'users', UserViewSet, basename='users')
router.register(r'carrier-users', CarrierUserViewSet, basename='carrieruser')
router.register(r'carrier-actions', CarrierUserActionsViewSet, basename='carrier-actions')
router.register(r'debug-test', DebugTestViewSet, basename='debug-test')
router.register(r'offers', OfferHistoryViewSet, basename='offers')  # ✅ Ruta general para ofertas
router.register(r'carrier-admins', CarrierAdminViewSet, basename='carrier-admins')  # ✅ Agregado
router.register(r'shipper-admins', ShipperAdminViewSet, basename='shipper-admin')
router.register(r'shipper-employees', ShipperEmployeeViewSet, basename='shipper-employees')
router.register(r'admincarrier2', AdminCarrier2ViewSet, basename='admincarrier2')
router.register(r'dispatchers', DispatcherViewSet, basename='dispatchers')

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Equipment
    path('api/equipment-types/', EquipmentTypeView.as_view(), name='equipment-types-list-create'),
    path('api/equipment-types/<int:pk>/', EquipmentTypeView.as_view(), name='equipment-types-detail'),

    # Stops
    path('api/loads/<int:load_id>/stops/', LoadStopsView.as_view(), name='load-stops'),
    path('api/loads/<int:load_id>/stops/<int:stop_id>/', LoadStopsView.as_view(), name='edit-stop'),
    path('api/stops/load/<int:load_id>/', StopViewSet.as_view({'get': 'stops_by_load'}), name='stops-by-load'),
    path('api/stops/<int:stop_id>/delays/', DelayView.as_view(), name='delay-list-create'),

    # Offers por carga (cuidado con el orden)
    path('api/loads/<int:load_id>/offers/', OfferHistoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='load-offers'),
    path('api/offers/<int:pk>/', OfferHistoryViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='offer-detail'),
    path('api/offers/<int:pk>/accept/', OfferHistoryViewSet.as_view({'patch': 'accept_offer'}), name='offer-accept'),
    path('api/offers/<int:pk>/reject/', OfferHistoryViewSet.as_view({'patch': 'reject_offer'}), name='offer-reject'),

    # Warnings
    path('api/loads/<int:load_id>/warnings/', LoadWarningsView.as_view(), name='load-warnings'),
    path('api/loads/<int:load_id>/add-warning/', AddWarningToLoadView.as_view(), name='add-warning-to-load'),
    path('api/loads/<int:load_id>/warnings/<int:warning_id>/', LoadWarningsView.as_view(), name='delete-load-warning'),
    path('api/warnings-list/', WarningListView.as_view(), name='warning-list'),

    # Loads & Progress
    path('api/loads/reserved/', ReservedLoadsView.as_view(), name='reserved-loads'),
    path('api/assigned-loads/', UserAssignedLoadsView.as_view(), name='assigned-loads'),
    path('api/loads/under-review/', LoadViewSet.as_view({'get': 'under_review_loads'}), name='under-review-loads'),
    path('api/loads/<int:load_id>/under-review/', UnderReviewLoadsView.as_view(), name='update-under-review-load'),
    path('api/loads/<int:load_id>/assign-without-offer/', AssignLoadWithoutOfferView.as_view(), name='assign-load-without-offer'),
    path('api/loads/<int:load_id>/close/', CloseLoadView.as_view(), name='close_load'),

    path('api/load-progress/<int:load_id>/', RegisterProgressView.as_view(), name='register-progress'),
    path('api/load-progress-list/<int:load_id>/', LoadProgressListView.as_view(), name='load-progress-list'),
    path('api/loads/load-progress/<int:load_id>/<str:step>/update/', UpdateLoadProgressView.as_view(), name='update-load-progress'),

    # Files & Media
    path('api/upload-excel/', ExcelUploadView.as_view(), name='upload-excel'),
    path('api/image-load/', UploadLoadImageView.as_view(), name='upload-load'),
    path('api/closed-loads/', ClosedLoadsView.as_view(), name='closed-loads'),

    # Stats
    path('api/user-load-statistics/', UserLoadStatistics.as_view(), name='user-load-statistics'),

    # Auth
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Register & Permissions
    path('register/', RegisterView.as_view(), name='register'),
    path('assign-role/', AssignRoleView.as_view(), name='assign-role'),

    # Password Reset
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

]


# Static & Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('/progress_pictures/', document_root=settings.BASE_DIR / 'progress_pictures')
