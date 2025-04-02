from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import CV
import pytesseract
from PIL import Image
import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

# Configuración de Tesseract (ajusta la ruta según tu sistema)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# En Linux/Mac, asegúrate de tener instalado `tesseract-ocr` y usa `tesseract` directamente

def index(request):
    return HttpResponse("¡Bienvenido a KeyWork! 🚀")

def extract_text_from_pdf(pdf_path):
    """Extrae texto de un archivo PDF. Si no hay texto embebido, usa OCR."""
    try:
        pdf_reader = PdfReader(pdf_path)
        extracted_text = ""

        # Intentar extraer texto de cada página
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""

        # Si no se extrajo texto, aplicar OCR
        if not extracted_text.strip():
            print("No text detected, applying OCR...")
            images = convert_from_path(pdf_path)
            for img in images:
                extracted_text += pytesseract.image_to_string(img, lang='spa+eng')

        return extracted_text.strip()
    except Exception as e:
        print(f"PDF Processing Error: {e}")
        return "Error extracting text from PDF."

@login_required
def upload_cv(request):
    """Sube un CV, lo almacena y extrae texto si es PDF o imagen."""
    if request.method == 'POST':
        # Si se envió un botón desde la página home, mostrar formulario de subida
        if not request.FILES:
            upload_type = request.POST.get('upload_type', 'document')
            if upload_type == 'document':
                accept = '.pdf'
                title = 'Subir CV como documento PDF'
            elif upload_type == 'image':
                accept = '.jpg,.jpeg,.png'
                title = 'Subir CV como imagen'
            else:
                accept = '.mp3,.wav'
                title = 'Subir grabación de voz (Próximamente)'
                
            return render(request, 'upload_cv.html', {
                'upload_type': upload_type,
                'accept': accept,
                'title': title
            })
        
        # Procesar el archivo subido
        upload_type = request.POST.get('upload_type', 'document')
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            messages.error(request, 'No se ha seleccionado ningún archivo.')
            return redirect('home')

        # Guardar en el modelo
        cv = CV(
            file=uploaded_file,
            upload_type=upload_type
        )
        cv.save()

        extracted_text = ""

        # Si es un documento PDF, extraer texto con PyPDF2 y OCR si es necesario
        if upload_type == 'document' and uploaded_file.name.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(cv.file.path)
            cv.extracted_text = extracted_text
            cv.save()

        # Si es una imagen, procesar con OCR
        elif upload_type == 'image':
            try:
                img = Image.open(cv.file.path)
                extracted_text = pytesseract.image_to_string(img, lang='spa+eng')

                # Guardar el texto extraído
                cv.extracted_text = extracted_text
                cv.save()

                messages.success(request, 'Image uploaded and text extracted successfully!')
            except Exception as e:
                print(f"OCR Error: {e}")
                messages.warning(request, 'CV uploaded but text extraction failed.')

        # Si el usuario es un JobSeeker, asociar el CV con su perfil
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.user_type == 'jobseeker':
                    # Asociar CV con el perfil
                    profile.cv = cv
                    
                    # Intentar extraer información básica del texto si existe
                    if extracted_text:
                        # Esta es una implementación básica. Aquí es donde integrarías tu modelo de IA
                        # para extraer información más precisa
                        extract_and_update_profile_data(profile, extracted_text)
                    
                    profile.save()
                    messages.success(request, 'CV uploaded and associated with your profile!')
            except Exception as e:
                print(f"Profile association error: {e}")
                messages.warning(request, 'CV uploaded but profile association failed.')

        messages.success(request, 'CV uploaded successfully!')
        return redirect('cv_detail', pk=cv.pk)

    # Si es GET, redirigir a la página principal
    return redirect('home')

def extract_and_update_profile_data(profile, text):
    """
    Extrae información del texto del CV y actualiza el perfil del usuario.
    Esta es una implementación muy básica. Aquí es donde integrarías tu modelo de IA.
    """
    text_lower = text.lower()
    
    # Detectar habilidades comunes
    common_skills = [
        "python", "java", "javascript", "html", "css", "django", "react", "angular", 
        "node.js", "sql", "marketing", "ventas", "comunicación", "liderazgo", 
        "desarrollo web", "gestión de proyectos", "excel", "word", "powerpoint"
    ]
    
    detected_skills = []
    for skill in common_skills:
        if skill in text_lower:
            detected_skills.append(skill.capitalize())
    
    if detected_skills and not profile.skills:
        profile.skills = ", ".join(detected_skills)
    
    # Detectar lenguajes
    languages = ["inglés", "español", "francés", "alemán", "italiano", "portugués", "chino", "japonés"]
    detected_languages = []
    for lang in languages:
        if lang in text_lower:
            detected_languages.append(lang.capitalize())
    
    if detected_languages and not profile.languages:
        profile.languages = ", ".join(detected_languages)
    
    # Si no hay un título profesional, intentar extraer algo relevante
    # (Esta es una implementación muy básica)
    if not profile.professional_title:
        professional_titles = [
            "ingeniero", "desarrollador", "programador", "diseñador", "analista", 
            "gerente", "director", "especialista", "consultor", "asistente"
        ]
        
        for title in professional_titles:
            if title in text_lower:
                # Buscar el título y algunas palabras alrededor
                index = text_lower.find(title)
                start = max(0, index - 20)
                end = min(len(text_lower), index + 30)
                context = text_lower[start:end]
                
                # Si encontramos algo que parece un título, usarlo
                words = context.split()
                if len(words) >= 2:
                    profile.professional_title = " ".join(
                        word.capitalize() for word in words if len(word) > 2
                    )[:100]  # Limitar a 100 caracteres
                    break

def cv_detail(request, pk):
    """Vista para mostrar los detalles del CV y el texto extraído."""
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'cv_detail.html', {'cv': cv})

def process_ocr(request, pk):
    """Procesar o reprocesar una imagen existente con OCR."""
    cv = get_object_or_404(CV, pk=pk)

    if cv.upload_type != 'image':
        messages.error(request, 'Only images can be processed with OCR')
        return redirect('cv_detail', pk=cv.pk)

    try:
        # Procesar la imagen con OCR
        img = Image.open(cv.file.path)
        extracted_text = pytesseract.image_to_string(img, lang='spa+eng')

        # Guardar el texto extraído
        cv.extracted_text = extracted_text
        cv.save()
        
        # Si el usuario es un JobSeeker, actualizar su perfil con la información extraída
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.user_type == 'jobseeker' and profile.cv == cv:
                    extract_and_update_profile_data(profile, extracted_text)
                    profile.save()
            except Exception as e:
                print(f"Profile update error: {e}")

        messages.success(request, 'Text extraction completed successfully!')
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        print(error_msg)
        cv.extracted_text = "OCR processing failed. You may need to install Tesseract OCR."
        cv.save()
        messages.error(request, error_msg)

    return redirect('cv_detail', pk=cv.pk)