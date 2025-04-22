from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
from .models import JobOfferDraft, CandidateMatch, EmployerMessage
from UserManagement.models import EmployerProfile, JobSeekerProfile
from JobSeekerPortal.models import JobOffer, JobApplication, Notification
from utils.openai_utils import get_embedding, calculate_similarity
from django.db.models import F

@login_required
def employer_dashboard(request):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden acceder a esta sección.')
        return redirect('home')
    
    # Obtener las ofertas de trabajo publicadas por este empleador
    job_offers = JobOffer.objects.filter(company=employer_profile.company_name)
    
    # Obtener los borradores de ofertas
    drafts = JobOfferDraft.objects.filter(employer=employer_profile)
    
    # Contar las aplicaciones recibidas
    applications_count = JobApplication.objects.filter(job_offer__in=job_offers).count()
    
    # Contar candidatos contactados
    contacted_candidates = CandidateMatch.objects.filter(job_offer__in=job_offers, contacted=True).count()
    
    return render(request, 'EmployerPortal/dashboard.html', {
        'profile': employer_profile,
        'job_offers': job_offers,
        'drafts': drafts,
        'applications_count': applications_count,
        'contacted_candidates': contacted_candidates
    })

@login_required
def create_job_offer(request):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden crear ofertas de trabajo.')
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        # Recopilar datos del formulario
        title = request.POST.get('title', '')
        company = employer_profile.company_name
        location = request.POST.get('location', '')
        description = request.POST.get('description', '')
        requirements = request.POST.get('requirements', '')
        salary_range = request.POST.get('salary_range', '')
        job_type = request.POST.get('job_type', '')
        remote = 'remote' in request.POST
        required_skills = request.POST.get('required_skills', '')
        years_experience = request.POST.get('years_experience', 0)
        
        if action == 'save_draft':
            # Guardar como borrador
            try:
                draft = JobOfferDraft.objects.create(
                    employer=employer_profile,
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    requirements=requirements,
                    salary_range=salary_range,
                    job_type=job_type,
                    remote=remote
                )
                messages.success(request, 'Borrador guardado exitosamente.')
                return redirect('employer_dashboard')
            except Exception as e:
                messages.error(request, f'Error al guardar el borrador: {str(e)}')
        
        elif action == 'publish':
            # Publicar directamente la oferta
            try:
                with transaction.atomic():
                    # Crear la oferta de trabajo
                    job_offer = JobOffer.objects.create(
                        title=title,
                        company=company,
                        location=location,
                        description=description,
                        requirements=requirements,
                        salary_range=salary_range,
                        job_type=job_type,
                        remote=remote,
                        expires_at=datetime.now() + timedelta(days=30),
                        active=True
                    )
                    messages.success(request, '¡Oferta de trabajo publicada exitosamente!')
                    return redirect('view_job_offer', job_id=job_offer.id)
            except Exception as e:
                messages.error(request, f'Error al publicar la oferta: {str(e)}')
    
    return render(request, 'EmployerPortal/create_job_offer.html')

@login_required
def edit_job_draft(request, draft_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden editar ofertas de trabajo.')
        return redirect('home')
    
    # Obtener el borrador
    draft = get_object_or_404(JobOfferDraft, id=draft_id, employer=employer_profile)
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        # Actualizar datos del borrador
        draft.title = request.POST.get('title', '')
        draft.location = request.POST.get('location', '')
        draft.description = request.POST.get('description', '')
        draft.requirements = request.POST.get('requirements', '')
        draft.salary_range = request.POST.get('salary_range', '')
        draft.job_type = request.POST.get('job_type', '')
        draft.remote = 'remote' in request.POST
        
        if action == 'save_draft':
            # Guardar como borrador
            try:
                draft.save()
                messages.success(request, 'Borrador actualizado exitosamente.')
                return redirect('employer_dashboard')
            except Exception as e:
                messages.error(request, f'Error al actualizar el borrador: {str(e)}')
        
        elif action == 'publish':
            # Publicar el borrador como oferta
            try:
                with transaction.atomic():
                    # Crear la oferta de trabajo desde el borrador
                    job_offer = JobOffer.objects.create(
                        title=draft.title,
                        company=draft.company,
                        location=draft.location,
                        description=draft.description,
                        requirements=draft.requirements,
                        salary_range=draft.salary_range,
                        job_type=draft.job_type,
                        remote=draft.remote,
                        expires_at=datetime.now() + timedelta(days=30),
                        active=True
                    )
                    # Eliminar el borrador
                    draft.delete()
                    
                    messages.success(request, '¡Oferta de trabajo publicada exitosamente!')
                    return redirect('view_job_offer', job_id=job_offer.id)
            except Exception as e:
                messages.error(request, f'Error al publicar la oferta: {str(e)}')
    
    return render(request, 'EmployerPortal/edit_job_draft.html', {'draft': draft})

@login_required
def view_job_offer(request, job_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden ver detalles de sus ofertas.')
        return redirect('home')
    
    # Obtener la oferta
    job_offer = get_object_or_404(JobOffer, id=job_id)
    
    # Verificar que la oferta pertenezca al empleador
    if job_offer.company != employer_profile.company_name:
        messages.error(request, 'No tiene permiso para ver esta oferta.')
        return redirect('employer_dashboard')
    
    # Obtener las aplicaciones para esta oferta
    applications = JobApplication.objects.filter(job_offer=job_offer).order_by('-applied_at')
    
    # Candidatos potenciales - solo seleccionamos campos que existen
    # Esta es la línea que necesita cambiarse para evitar el error
    potential_matches = CandidateMatch.objects.filter(job_offer=job_offer).only(
        'id', 'job_offer', 'job_seeker', 'match_score', 'contacted', 'created_at'
    ).order_by('-match_score')
    
    return render(request, 'EmployerPortal/view_job_offer.html', {
        'job': job_offer,
        'applications': applications,
        'potential_matches': potential_matches
    })

@login_required
def find_candidates(request):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden buscar candidatos.')
        return redirect('home')
    
    # Obtener explícitamente las ofertas ACTIVAS del empleador
    job_offers = JobOffer.objects.filter(
        company=employer_profile.company_name, 
        active=True
    )
    print(f"Número de ofertas activas para {employer_profile.company_name}: {job_offers.count()}")
    
    # Lógica de búsqueda (se implementará completamente más adelante)
    search_query = request.GET.get('search', '')
    skill_filter = request.GET.get('skills', '')
    
    # Búsqueda básica de candidatos
    candidates = JobSeekerProfile.objects.filter(profile_completed=True, has_cv=True)
    
    if search_query:
        candidates = candidates.filter(professional_title__icontains=search_query)
    
    if skill_filter:
        candidates = candidates.filter(skills__icontains=skill_filter)
    
    return render(request, 'EmployerPortal/find_candidates.html', {
        'candidates': candidates,
        'job_offers': job_offers,  # Asegúrate de que esto se está pasando
        'search_query': search_query,
        'skill_filter': skill_filter
    })
    
@login_required
def contact_candidate(request, candidate_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden contactar candidatos.')
        return redirect('home')
    
    # Obtener el candidato
    candidate = get_object_or_404(JobSeekerProfile, id=candidate_id)
    
    # Obtener las ofertas activas del empleador para seleccionar
    job_offers = JobOffer.objects.filter(company=employer_profile.company_name, active=True)
    
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')
        
        if not all([job_id, subject, message_text]):
            messages.error(request, 'Por favor complete todos los campos.')
            return render(request, 'EmployerPortal/contact_candidate.html', {
                'candidate': candidate,
                'job_offers': job_offers
            })
        
        try:
            job_offer = JobOffer.objects.get(id=job_id)
            
            # Crear el mensaje
            employer_message = EmployerMessage.objects.create(
                sender=employer_profile,
                recipient=candidate,
                related_job=job_offer,
                subject=subject,
                message=message_text
            )
            
            # Crear una notificación para el candidato
            notification = Notification.objects.create(
                recipient=candidate,
                title=f"Mensaje de {employer_profile.company_name} sobre {job_offer.title}",
                message=message_text,
                related_job=job_offer
            )
            
            # Si hay un match registrado, marcarlo como contactado
            CandidateMatch.objects.filter(
                job_offer=job_offer,
                job_seeker=candidate
            ).update(contacted=True)
            
            messages.success(request, f'Mensaje enviado exitosamente a {candidate.full_name or candidate.user.username}.')
            return redirect('find_candidates')
            
        except Exception as e:
            messages.error(request, f'Error al enviar el mensaje: {str(e)}')
    
    return render(request, 'EmployerPortal/contact_candidate.html', {
        'candidate': candidate,
        'job_offers': job_offers
    })

@login_required
def view_applications(request):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden ver aplicaciones.')
        return redirect('home')
    
    # Obtener las ofertas del empleador
    job_offers = JobOffer.objects.filter(company=employer_profile.company_name)
    
    # Obtener las aplicaciones para esas ofertas
    applications = JobApplication.objects.filter(job_offer__in=job_offers).order_by('-applied_at')
    
    # Filtrar por estado si se especifica
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    return render(request, 'EmployerPortal/view_applications.html', {
        'applications': applications,
        'status_filter': status_filter
    })

@login_required
def update_application(request, application_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden actualizar aplicaciones.')
        return redirect('home')
    
    # Obtener la aplicación
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Verificar que la oferta pertenezca al empleador
    if application.job_offer.company != employer_profile.company_name:
        messages.error(request, 'No tiene permiso para actualizar esta aplicación.')
        return redirect('view_applications')
    
    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        feedback = request.POST.get('feedback', '')
        
        if new_status in [s[0] for s in JobApplication._meta.get_field('status').choices]:
            # Actualizar el estado
            application.status = new_status
            application.save()
            
            # Crear notificación para el candidato
            status_display = dict(JobApplication._meta.get_field('status').choices)[new_status]
            notification_message = f"Su aplicación para {application.job_offer.title} ha sido actualizada a: {status_display}"
            if feedback:
                notification_message += f"\n\nComentarios: {feedback}"
            
            Notification.objects.create(
                recipient=application.job_seeker,
                title=f"Actualización de su aplicación - {application.job_offer.title}",
                message=notification_message,
                related_job=application.job_offer
            )
            
            messages.success(request, 'Aplicación actualizada exitosamente.')
            return redirect('view_applications')
        else:
            messages.error(request, 'Estado de aplicación inválido.')
    
    return render(request, 'EmployerPortal/update_application.html', {'application': application})

@login_required
def ats_match_candidates(request, job_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden usar el sistema ATS.')
        return redirect('home')
    
    # Obtener la oferta
    job_offer = get_object_or_404(JobOffer, id=job_id)
    
    # Verificar que la oferta pertenezca al empleador
    if job_offer.company != employer_profile.company_name:
        messages.error(request, 'No tiene permiso para acceder a esta oferta.')
        return redirect('employer_dashboard')
    
    try:
        print(f"Iniciando análisis ATS para oferta: {job_offer.title}")
        
        # Limpiar coincidencias previas para esta oferta
        CandidateMatch.objects.filter(job_offer=job_offer).delete()
        
        # Preparar texto de la oferta para embedding
        job_text = f"Título: {job_offer.title}. Descripción: {job_offer.description}. Requisitos: {job_offer.requirements}."
        if hasattr(job_offer, 'required_skills') and job_offer.required_skills:
            job_text += f" Habilidades requeridas: {job_offer.required_skills}."
        
        print("Generando embedding para la oferta...")
        
        # Generar embedding para la oferta
        job_embedding = get_embedding(job_text)
        
        if not job_embedding:
            messages.error(request, 'No se pudo generar el análisis para esta oferta. Intente nuevamente.')
            return redirect('view_job_offer', job_id=job_offer.id)
        
        # Buscar candidatos con CV
        candidates = JobSeekerProfile.objects.filter(has_cv=True)
        matches = []
        
        print(f"Analizando {candidates.count()} candidatos potenciales...")
        
        # Para cada candidato, calcular la puntuación de coincidencia
        for candidate in candidates:
            try:
                # Verificar que el CV tiene texto extraído
                if not candidate.cv or not candidate.cv.extracted_text:
                    print(f"Candidato {candidate.id} sin texto extraído, omitiendo...")
                    continue
                
                # Preparar texto del candidato
                candidate_text = f"Título profesional: {candidate.professional_title or ''}. "
                candidate_text += f"Habilidades: {candidate.skills or ''}. "
                candidate_text += f"Experiencia: {candidate.years_experience or 0} años. "
                candidate_text += f"Educación: {candidate.education or ''}. "
                candidate_text += f"CV: {candidate.cv.extracted_text}"
                
                # Generar embedding para el candidato
                candidate_embedding = get_embedding(candidate_text)
                
                if candidate_embedding:
                    # Calcular similitud
                    similarity_score = calculate_similarity(job_embedding, candidate_embedding)
                    
                    # Convertir a porcentaje
                    match_score = round(similarity_score * 100)
                    print(f"Match score para candidato {candidate.id}: {match_score}%")
                    
                    # Guardar match si la puntuación es mayor a 30%
                    if match_score > 30:
                        match = CandidateMatch.objects.create(
                            job_offer=job_offer,
                            job_seeker=candidate,
                            match_score=match_score,
                            contacted=False
                            # No incluimos job_embedding ni candidate_embedding
                        )
                        matches.append(match)
                        print(f"Match guardado para candidato {candidate.id}")
            except Exception as e:
                print(f"Error procesando candidato {candidate.id}: {str(e)}")
        
        if matches:
            messages.success(
                request, 
                f'Análisis completado. Se encontraron {len(matches)} candidatos potenciales.'
            )
        else:
            messages.info(
                request, 
                'No se encontraron candidatos que coincidan con los requisitos. Intente ampliar los criterios.'
            )
        
        return redirect('view_job_offer', job_id=job_offer.id)
    
    except Exception as e:
        import traceback
        print(f"Error en análisis ATS: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f'Error en análisis ATS: {str(e)}')
        return redirect('view_job_offer', job_id=job_offer.id)
    
@login_required
def edit_job_offer(request, job_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden editar ofertas de trabajo.')
        return redirect('home')
    
    # Obtener la oferta
    job_offer = get_object_or_404(JobOffer, id=job_id)
    
    # Verificar que la oferta pertenezca al empleador
    if job_offer.company != employer_profile.company_name:
        messages.error(request, 'No tiene permiso para editar esta oferta.')
        return redirect('employer_dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        # Actualizar datos de la oferta
        job_offer.title = request.POST.get('title', '')
        job_offer.location = request.POST.get('location', '')
        job_offer.description = request.POST.get('description', '')
        job_offer.requirements = request.POST.get('requirements', '')
        job_offer.salary_range = request.POST.get('salary_range', '')
        job_offer.job_type = request.POST.get('job_type', '')
        job_offer.remote = 'remote' in request.POST
        
        # Campos adicionales si existen
        if 'required_skills' in request.POST:
            job_offer.required_skills = request.POST.get('required_skills', '')
        
        try:
            job_offer.save()
            messages.success(request, 'Oferta de trabajo actualizada exitosamente.')
            return redirect('view_job_offer', job_id=job_offer.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar la oferta: {str(e)}')
    
    # Mostrar formulario para editar
    return render(request, 'EmployerPortal/edit_job_offer.html', {'job': job_offer})

@login_required
def delete_job_offer(request, job_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden eliminar ofertas de trabajo.')
        return redirect('home')
    
    # Obtener la oferta
    job_offer = get_object_or_404(JobOffer, id=job_id)
    
    # Verificar que la oferta pertenezca al empleador
    if job_offer.company != employer_profile.company_name:
        messages.error(request, 'No tiene permiso para eliminar esta oferta.')
        return redirect('employer_dashboard')
    
    if request.method == 'POST':
        # Eliminar la oferta
        job_title = job_offer.title  # Guardar el título para mensaje
        try:
            job_offer.delete()
            messages.success(request, f'La oferta "{job_title}" ha sido eliminada exitosamente.')
            return redirect('employer_dashboard')
        except Exception as e:
            messages.error(request, f'Error al eliminar la oferta: {str(e)}')
            return redirect('view_job_offer', job_id=job_id)
    
    # Mostrar página de confirmación
    return render(request, 'EmployerPortal/confirm_delete_job.html', {'job': job_offer})

@login_required
def toggle_job_status(request, job_id):
    # Verificar que el usuario sea un empleador
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Solo los empleadores pueden gestionar ofertas de trabajo.')
        return redirect('home')
    
    # Obtener la oferta
    job_offer = get_object_or_404(JobOffer, id=job_id)
    
    # Verificar que la oferta pertenezca al empleador
    if job_offer.company != employer_profile.company_name:
        messages.error(request, 'No tiene permiso para gestionar esta oferta.')
        return redirect('employer_dashboard')
    
    # Cambiar estado
    try:
        job_offer.active = not job_offer.active
        job_offer.save()
        
        status_text = "activada" if job_offer.active else "desactivada"
        messages.success(request, f'La oferta ha sido {status_text} exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al cambiar el estado de la oferta: {str(e)}')
    
    return redirect('view_job_offer', job_id=job_id)