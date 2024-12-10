from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from myapp.views import AssignRoleView, LoadStopsView, OfferHistoryView, RegisterView, WarningViewSet,ReservedLoadsView
from myapp.views import UserAssignedLoadsView,LoadWarningsView,AddWarningToLoadView,WarningListView

# Registrar los viewsets en el router
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'loads', views.LoadViewSet)
router.register(r'stops', views.StopViewSet)
router.register(r'equipment-types', views.EquipmentTypeViewSet)
router.register(r'warnings', views.WarningViewSet) 
 # Registra el endpoint para advertencias

# Definir las rutas adicionales para vistas personalizadas
urlpatterns = [
  
    path('admin/', admin.site.urls),
    path('api/loads/reserved/', ReservedLoadsView.as_view(), name='reserved-loads'),
    path('api/loads/assigned-to-user/', UserAssignedLoadsView.as_view(), name='user-assigned-loads'),
    path('api/loads/<int:load_id>/warnings/', LoadWarningsView.as_view(), name='load-warnings'),
    path('api/loads/<int:load_id>/add-warning/', AddWarningToLoadView.as_view(), name='add-warning-to-load'),
    path('api/warnings-list/', WarningListView.as_view(), name='warning-list'), 

    path('api/', include(router.urls)),  # Rutas para los viewsets registrados en el router
    path('api/loads/<int:load_id>/stops/', LoadStopsView.as_view(), name='load-stops'),  # Ruta para manejar los stops de un load específico
    path('api/loads/<int:load_id>/stops/<int:stop_id>/', LoadStopsView.as_view(), name='edit-stop'),  # Ruta para editar/eliminar un stop específico
    path('api/loads/<int:load_id>/offers/', OfferHistoryView.as_view(), name='load-offers'),  # Ruta para manejar el historial de ofertas de un load
  
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login para obtener el token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh del token

    # Endpoints de gestión de usuarios y roles
    path('register/', RegisterView.as_view(), name='register'),               # Registro de usuario
    path('assign-role/', AssignRoleView.as_view(), name='assign_role'),       # Asignar rol a usuario         # Perfil del usuario autenticado
    

]
