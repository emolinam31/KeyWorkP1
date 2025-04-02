from django.db import models
from django.contrib.auth.models import User
from CollectionPoint.models import CV

class UserProfile(models.Model):
    USER_TYPES = (
        ('employer', 'Empleador'),
        ('jobseeker', 'Buscador de Empleo'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Campos para empleadores
    company_name = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, null=True)
    
    # Campos para buscadores de empleo
    full_name = models.CharField(max_length=150, blank=True, null=True)
    professional_title = models.CharField(max_length=100, blank=True, null=True)
    years_experience = models.PositiveSmallIntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Campos para habilidades y educación
    skills = models.TextField(blank=True, null=True, help_text="Habilidades separadas por comas")
    education = models.TextField(blank=True, null=True)
    languages = models.CharField(max_length=200, blank=True, null=True, help_text="Idiomas separados por comas")
    
    # Relación con CV
    cv = models.ForeignKey(CV, on_delete=models.SET_NULL, blank=True, null=True, related_name='profiles')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    def skills_as_list(self):
        """Retorna las habilidades como una lista."""
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',')]
    
    def languages_as_list(self):
        """Retorna los idiomas como una lista."""
        if not self.languages:
            return []
        return [language.strip() for language in self.languages.split(',')]