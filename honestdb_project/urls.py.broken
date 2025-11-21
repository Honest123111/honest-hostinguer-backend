cat > honestdb_project/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    # Add your API paths here - uncomment and adjust as needed
    path('api/', include('myapp.urls')),
    
    # Serve Angular app
    path('', TemplateView.as_view(template_name='index.html')),
    # Catch all for Angular routing
    re_path(r'^(?!admin|api|static|media|health).*$', 
            TemplateView.as_view(template_name='index.html')),
]

# Add static and media URL patterns for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
