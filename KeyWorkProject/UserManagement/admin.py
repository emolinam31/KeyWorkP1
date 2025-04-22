from django.contrib import admin
from .models import JobSeekerProfile, EmployerProfile

class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'professional_title', 'has_cv', 'created_at')
    list_filter = ('has_cv', 'profile_completed')
    search_fields = ('user__username', 'full_name', 'professional_title', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'full_name', 'profile_completed', 'created_at', 'updated_at')
        }),
        ('Información profesional', {
            'fields': ('professional_title', 'years_experience', 'skills', 'education', 'languages')
        }),
        ('Información de contacto', {
            'fields': ('date_of_birth', 'phone_number', 'location', 'bio')
        }),
        ('Preferencias laborales', {
            'fields': ('availability', 'desired_salary', 'remote_work')
        }),
        ('CV', {
            'fields': ('cv', 'has_cv')
        }),
    )

class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'industry', 'company_size', 'created_at')
    list_filter = ('profile_completed', 'company_size')
    search_fields = ('user__username', 'company_name', 'industry')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'profile_completed', 'created_at', 'updated_at')
        }),
        ('Información de la empresa', {
            'fields': ('company_name', 'industry', 'company_size', 'company_website', 
                      'company_description', 'company_logo', 'company_location')
        }),
    )

admin.site.register(JobSeekerProfile, JobSeekerProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)