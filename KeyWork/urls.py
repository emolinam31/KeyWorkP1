# KeyWorkProject/KeyWork/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('collection/', include('CollectionPoint.urls')),  # URLs para la subida y procesamiento de CVs
    # path('cv-processing/', include('cv_processing.urls')),  # Comentada o eliminada porque no se está utilizando
    # path('user/', include('UserManagement.urls')),  # URLs para la gestión de usuarios
    #path('notifications/', include('Notifications.urls')),  # URLs para notificaciones
    # path('job-seeker/', include('JobSeekerPortal.urls')),  # URLs para el portal de quien busca empleo
    # path('employer/', include('EmployerPortal.urls')),  # URLs para el portal de empleadores
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:  # Solo en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)