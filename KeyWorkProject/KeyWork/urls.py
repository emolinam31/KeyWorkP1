from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Páginas principales
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    
    # Apps
    path('collection/', include('CollectionPoint.urls')),  # URLs para la subida y procesamiento de CVs
    path('employer/', include('EmployerPortal.urls')),  # URLs para el portal de empleadores
    path('user/', include('UserManagement.urls')),  # URLs para la gestión de usuarios
    path('jobseeker/', include('JobSeekerPortal.urls')),
    
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)