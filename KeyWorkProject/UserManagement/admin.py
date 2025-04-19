# UserManagement/admin.py
from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'get_name', 'created_at')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'full_name', 'company_name', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'user_type', 'created_at', 'updated_at')
        }),
        ('Información de Empleador', {
            'classes': ('collapse',),
            'fields': ('company_name', 'industry', 'company_size', 'company_website', 
                      'company_description', 'company_logo', 'company_location')
        }),
        ('Información de Candidato', {
            'classes': ('collapse',),
            'fields': ('full_name', 'professional_title', 'years_experience', 'date_of_birth',
                      'phone_number', 'location', 'bio', 'availability', 'desired_salary', 
                      'remote_work', 'cv')
        }),
        ('Habilidades y Educación', {
            'classes': ('collapse',),
            'fields': ('skills', 'education', 'languages')
        }),
    )
    
    def get_name(self, obj):
        if obj.user_type == 'employer':
            return obj.company_name or "Sin nombre de empresa"
        return obj.full_name or "Sin nombre completo"
    get_name.short_description = 'Nombre'

admin.site.register(UserProfile, UserProfileAdmin)