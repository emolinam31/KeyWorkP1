from django.db import models

class CV(models.Model):
    UPLOAD_TYPES = (
        ('document', 'Document (PDF)'),
        ('image', 'Photo (JPG, PNG)'),
        ('audio', 'Voice Recording'),
    )
    
    file = models.FileField(upload_to='cvs/')
    upload_type = models.CharField(max_length=20, choices=UPLOAD_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_upload_type_display()} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    