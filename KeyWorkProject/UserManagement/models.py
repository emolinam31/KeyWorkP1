from django.db import models
from django.contrib.auth.models import User
from CollectionPoint.models import CV

class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="%(class)s_profile")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_completed = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class JobSeekerProfile(BaseProfile):
    # Información personal
    full_name = models.CharField(max_length=150, blank=True, null=True)
    professional_title = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Habilidades y experiencia
    years_experience = models.PositiveSmallIntegerField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Habilidades separadas por comas")
    education = models.TextField(blank=True, null=True)
    languages = models.CharField(max_length=200, blank=True, null=True, help_text="Idiomas separados por comas")
    
    # Preferencias de trabajo
    AVAILABILITY_CHOICES = (
        ('immediate', 'Inmediata'),
        ('2_weeks', '2 semanas'),
        ('1_month', '1 mes'),
        ('negotiable', 'Negociable'),
    )
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, blank=True, null=True)
    desired_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    remote_work = models.BooleanField(default=False, verbose_name="Disponible para trabajo remoto")
    
    # Relación con CV
    cv = models.ForeignKey(CV, on_delete=models.SET_NULL, blank=True, null=True, related_name='jobseeker_profiles')
    has_cv = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.full_name or self.user.username} (Candidato)"
    
    def skills_as_list(self):
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',')]
    
    def languages_as_list(self):
        if not self.languages:
            return []
        return [language.strip() for language in self.languages.split(',')]
    
    class Meta:
        verbose_name = "Perfil de Candidato"
        verbose_name_plural = "Perfiles de Candidatos"
        indexes = [
            models.Index(fields=['profile_completed']),
            models.Index(fields=['has_cv']),
        ]

class EmployerProfile(BaseProfile):
    company_name = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 empleados'),
        ('11-50', '11-50 empleados'),
        ('51-200', '51-200 empleados'),
        ('201-500', '201-500 empleados'),
        ('501-1000', '501-1000 empleados'),
        ('1000+', 'Más de 1000 empleados'),
    )
    company_size = models.CharField(max_length=10, choices=COMPANY_SIZE_CHOICES, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_location = models.CharField(max_length=150, blank=True, null=True)
    
    def __str__(self):
        return f"{self.company_name or self.user.username} (Empleador)"
    
    class Meta:
        verbose_name = "Perfil de Empleador"
        verbose_name_plural = "Perfiles de Empleadores"
        indexes = [
            models.Index(fields=['profile_completed']),
        ]