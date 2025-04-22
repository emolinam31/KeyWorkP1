from django.contrib import admin
from .models import CV

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('upload_type', 'uploaded_at', 'file')
    list_filter = ('upload_type', 'uploaded_at')
    search_fields = ('file',)
    date_hierarchy = 'uploaded_at'