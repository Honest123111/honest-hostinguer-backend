from django.contrib import admin  # Asegúrate de importar admin aquí
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp import views
from myapp.views import LoadStopsView 

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'loads', views.LoadViewSet)
router.register(r'stops', views.StopViewSet)
router.register(r'equipment-types', views.EquipmentTypeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/loads/<int:load_id>/stops/', views.LoadStopsView.as_view(), name='load-stops'),
    path('loads/<int:load_id>/stops/', LoadStopsView.as_view(), name='load-stops'),
    path('loads/<int:load_id>/stops/<int:stop_id>/', LoadStopsView.as_view(), name='edit-stop'),
]


