from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobOffer, JobApplication, Notification
from UserManagement.models import JobSeekerProfile

@login_required
def job_listings(request):
    # Obtener todas las ofertas activas
    jobs = JobOffer.objects.filter(active=True)
    
    # Verificar si el usuario es un JobSeeker
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Esta sección es solo para buscadores de empleo.")
        return redirect('home')
    
    # Obtener las aplicaciones del usuario para saber a qué trabajos ya aplicó
    user_applications = JobApplication.objects.filter(job_seeker=profile).values_list('job_offer_id', flat=True)
    
    # Contar notificaciones no leídas
    unread_notifications_count = Notification.objects.filter(recipient=profile, read=False).count()
    
    return render(request, 'jobseeker_portal/job_listings.html', {
        'jobs': jobs,
        'user_applications': user_applications,
        'unread_notifications_count': unread_notifications_count
    })

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id, active=True)
    
    # Verificar si el usuario es un JobSeeker
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Esta sección es solo para buscadores de empleo.")
        return redirect('home')
    
    # Verificar si ya aplicó a este trabajo
    already_applied = JobApplication.objects.filter(job_seeker=profile, job_offer=job).exists()
    
    # Contar notificaciones no leídas
    unread_notifications_count = Notification.objects.filter(recipient=profile, read=False).count()
    
    return render(request, 'jobseeker_portal/job_detail.html', {
        'job': job,
        'already_applied': already_applied,
        'unread_notifications_count': unread_notifications_count
    })

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id, active=True)
    
    # Verificar si el usuario es un JobSeeker
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Esta sección es solo para buscadores de empleo.")
        return redirect('home')
    
    # Verificar si ya aplicó a este trabajo
    if JobApplication.objects.filter(job_seeker=profile, job_offer=job).exists():
        messages.warning(request, "Ya has aplicado a esta oferta anteriormente.")
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        
        # Crear la aplicación
        application = JobApplication.objects.create(
            job_seeker=profile,
            job_offer=job,
            cover_letter=cover_letter
        )
        
        messages.success(request, "¡Has aplicado exitosamente a esta oferta!")
        return redirect('job_detail', job_id=job.id)
    
    return render(request, 'jobseeker_portal/apply_job.html', {
        'job': job
    })

@login_required
def my_applications(request):
    # Verificar si el usuario es un JobSeeker
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Esta sección es solo para buscadores de empleo.")
        return redirect('home')
    
    # Obtener todas las aplicaciones del usuario
    applications = JobApplication.objects.filter(job_seeker=profile).order_by('-applied_at')
    
    # Contar notificaciones no leídas
    unread_notifications_count = Notification.objects.filter(recipient=profile, read=False).count()
    
    return render(request, 'jobseeker_portal/my_applications.html', {
        'applications': applications,
        'unread_notifications_count': unread_notifications_count
    })

@login_required
def notifications(request):
    # Verificar si el usuario es un JobSeeker
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Esta sección es solo para buscadores de empleo.")
        return redirect('home')
    
    # Obtener todas las notificaciones del usuario
    notifications_list = Notification.objects.filter(recipient=profile).order_by('-created_at')
    
    # Marcar todas como leídas
    Notification.objects.filter(recipient=profile, read=False).update(read=True)
    
    return render(request, 'jobseeker_portal/notifications.html', {
        'notifications': notifications_list
    })