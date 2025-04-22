from django.db import models
from django.contrib.auth.models import User
from UserManagement.models import JobSeekerProfile

class JobOffer(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    required_skills = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Tiempo completo'),
        ('part_time', 'Medio tiempo'),
        ('contract', 'Contrato'),
        ('freelance', 'Freelance'),
        ('internship', 'Pasantía'),
    ])
    remote = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.company}"
    
    class Meta:
        ordering = ['-created_at']

class JobApplication(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('applied', 'Aplicado'),
        ('in_review', 'En revisión'),
        ('interview', 'Entrevista'),
        ('rejected', 'Rechazado'),
        ('accepted', 'Aceptado'),
    ], default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job_offer.title}"
    
    class Meta:
        unique_together = ('job_seeker', 'job_offer')

class Notification(models.Model):
    recipient = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_job = models.ForeignKey(JobOffer, on_delete=models.SET_NULL, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notificación para {self.recipient.user.username}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']