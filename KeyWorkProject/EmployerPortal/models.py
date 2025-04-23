from django.db import models
from django.contrib.auth.models import User
from UserManagement.models import EmployerProfile, JobSeekerProfile
from JobSeekerPortal.models import JobOffer, JobApplication

class JobOfferDraft(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Tiempo completo'),
        ('part_time', 'Medio tiempo'),
        ('contract', 'Contrato'),
        ('freelance', 'Freelance'),
        ('internship', 'Pasantía'),
    ])
    remote = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Borrador: {self.title} - {self.company}"
    
    def publish(self):
        
        from datetime import datetime, timedelta
        
        # Crear la oferta de trabajo
        job_offer = JobOffer.objects.create(
            title=self.title,
            company=self.company,
            location=self.location,
            description=self.description,
            requirements=self.requirements,
            salary_range=self.salary_range,
            job_type=self.job_type,
            remote=self.remote,
            expires_at=datetime.now() + timedelta(days=30),
            active=True
        )
        
        return job_offer

class CandidateMatch(models.Model):
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    match_score = models.FloatField()  # Puntuación de coincidencia (0-100)
    contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    job_embedding = models.TextField(blank=True, null=True)  # Añadir este campo
    candidate_embedding = models.TextField(blank=True, null=True)  # Añadir este campo
    
    def __str__(self):
        return f"Match: {self.job_seeker.user.username} - {self.job_offer.title} ({self.match_score}%)"
    
    class Meta:
        unique_together = ('job_offer', 'job_seeker')
        ordering = ['-match_score']

class EmployerMessage(models.Model):
    sender = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    recipient = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    related_job = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Mensaje de {self.sender.user.username} a {self.recipient.user.username} sobre {self.related_job.title}"
    
    def create_notification(self):
        
        from JobSeekerPortal.models import Notification
        
        notification = Notification.objects.create(
            recipient=self.recipient,
            title=f"Mensaje de {self.sender.company_name} sobre {self.related_job.title}",
            message=self.message,
            related_job=self.related_job
        )
        
        return notification