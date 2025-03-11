# KeyWorkProject/CollectionPoint/views.py (versión con modelo)
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CV

def index(request):
    return HttpResponse("¡Bienvenido a KeyWork! 🚀")

def upload_cv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload_type = request.POST.get('upload_type', 'document')
        uploaded_file = request.FILES['file']
        
        # Guardar en el modelo
        cv = CV(
            file=uploaded_file,
            upload_type=upload_type
        )
        cv.save()
        
        messages.success(request, 'CV uploaded successfully!')
        return redirect('home')
    
    return redirect('home')