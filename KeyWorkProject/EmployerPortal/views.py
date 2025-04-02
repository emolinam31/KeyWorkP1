from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

def employer_portal(request):
    """Vista principal del portal del empleador"""
    return render(request, 'employerpage.html')

def upload_vacancy(request):
    """Vista para subir una nueva vacante"""
    # Esta es una vista temporal. Aquí implementarás el formulario de creación de vacantes
    if request.method == 'POST':
        # Procesar el formulario cuando lo implementes
        messages.success(request, "¡Vacante creada exitosamente!")
        return redirect('employer_portal')
    
    # Por ahora, solo muestra un mensaje temporal
    return HttpResponse("Página para subir una nueva vacante - En construcción")

def find_candidate(request):
    """Vista para buscar candidatos"""
    # Esta es una vista temporal. Aquí implementarás la búsqueda con algoritmo de similitud de coseno
    return HttpResponse("Página para buscar candidatos - En construcción")

def notify_candidate(request):
    """Vista para notificar a un candidato"""
    # Esta es una vista temporal.
    return HttpResponse("Página para notificar candidatos - En construcción")

def vacancy_detail(request, vacancy_id):
    """Vista para ver detalles de una vacante"""
    # Esta es una vista temporal. Aquí mostrarás los detalles de la vacante con el ID proporcionado
    return HttpResponse(f"Detalles de la vacante {vacancy_id} - En construcción")