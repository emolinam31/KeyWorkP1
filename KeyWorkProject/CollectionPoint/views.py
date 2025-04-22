from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import CV
from UserManagement.forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm
from UserManagement.models import JobSeekerProfile, EmployerProfile
import pytesseract
from PIL import Image
import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import re

# Configuración de Tesseract (usando la configuración del settings.py)
tesseract_cmd = getattr(settings, 'TESSERACT_CMD', None)
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    # Intentar detectar automáticamente la ubicación de Tesseract
    import shutil
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        print(f"Tesseract encontrado en: {tesseract_path}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        print("ADVERTENCIA: No se pudo encontrar Tesseract. La extracción OCR podría fallar.")

def index(request):
    return HttpResponse("¡Bienvenido a KeyWork! 🚀")

def extract_text_from_pdf(pdf_path):
    try:
        print(f"Intentando extraer texto de: {pdf_path}")
        pdf_reader = PdfReader(pdf_path)
        extracted_text = ""

        # Intentar extraer texto de cada página
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text() or ""
            extracted_text += page_text
            print(f"Página {i+1}: Extraídos {len(page_text)} caracteres")

        # Si no se extrajo texto, aplicar OCR
        if not extracted_text.strip():
            print("No se detectó texto en el PDF, aplicando OCR...")
            try:
                images = convert_from_path(pdf_path)
                print(f"PDF convertido a {len(images)} imágenes")
                for i, img in enumerate(images):
                    img_text = pytesseract.image_to_string(img, lang='spa+eng')
                    extracted_text += img_text
                    print(f"OCR en imagen {i+1}: Extraídos {len(img_text)} caracteres")
            except Exception as ocr_e:
                print(f"Error en OCR: {str(ocr_e)}")
                return f"Error en OCR del PDF: {str(ocr_e)}"

        return extracted_text.strip()
    except Exception as e:
        print(f"Error procesando PDF: {str(e)}")
        return f"Error procesando PDF: {str(e)}"

@login_required
def upload_cv(request):
    # Intentar obtener el perfil de JobSeeker
    try:
        jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        # Si no existe, posiblemente es un empleador
        messages.error(request, 'Solo los buscadores de empleo pueden subir hojas de vida.')
        return redirect('home')
        
    if request.method == 'POST':
        # Si hay un archivo enviado, procesarlo
        if request.FILES.get('file'):
            # Procesar el archivo subido
            upload_type = request.POST.get('upload_type', 'document')
            uploaded_file = request.FILES['file']

            # Validar tipo de archivo
            if upload_type == 'document' and not uploaded_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Para documentos, solo se aceptan archivos PDF.')
                return redirect('upload_cv')
            elif upload_type == 'image' and not any(uploaded_file.name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                messages.error(request, 'Para imágenes, solo se aceptan archivos JPG o PNG.')
                return redirect('upload_cv')

            # Guardar en el modelo
            try:
                cv = CV(
                    file=uploaded_file,
                    upload_type=upload_type
                )
                cv.save()

                extracted_text = ""

                # Si es un documento PDF, extraer texto
                if upload_type == 'document' and uploaded_file.name.endswith(".pdf"):
                    extracted_text = extract_text_from_pdf(cv.file.path)
                    cv.extracted_text = extracted_text
                    cv.save()

                # Si es una imagen, procesar con OCR
                elif upload_type == 'image':
                    try:
                        img = Image.open(cv.file.path)
                        extracted_text = pytesseract.image_to_string(img, lang='spa+eng')
                        cv.extracted_text = extracted_text
                        cv.save()
                        messages.success(request, '¡Imagen subida y texto extraído correctamente!')
                    except Exception as e:
                        messages.warning(request, 'CV subido pero la extracción de texto falló.')

                # Asociar el CV con el perfil del usuario
                try:
                    with transaction.atomic():
                        old_cv = jobseeker_profile.cv
                        jobseeker_profile.cv = cv
                        jobseeker_profile.has_cv = True
                        
                        # Extraer información del texto
                        if extracted_text:
                            jobseeker_profile = extract_and_update_profile_data(jobseeker_profile, extracted_text)
                        
                        jobseeker_profile.save()
                    
                    messages.success(request, '¡CV subido y asociado a tu perfil exitosamente!')
                except Exception as e:
                    import traceback
                    print(f"Error al asociar CV al perfil: {str(e)}")
                    print(traceback.format_exc())
                    messages.warning(request, f'CV subido pero no se pudo asociar al perfil: {str(e)}')

                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
                return redirect('upload_cv')
        else:
            # Si se está mostrando el formulario para seleccionar tipo
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
                
            # Mostrar el formulario para seleccionar archivo
            return render(request, 'upload_cv.html', {
                'upload_type': upload_type,
                'accept': accept,
                'title': title
            })
    else:
        # Verificar si el usuario ya tiene un CV
        has_cv = jobseeker_profile.has_cv
        
        # Mostrar opciones de tipo de archivo
        return render(request, 'upload_options.html', {
            'title': 'Subir Hoja de Vida',
            'has_cv': has_cv,
            'is_required': not has_cv
        })
        
def extract_and_update_profile_data(profile, text):
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

@login_required
def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
        
    # Verificar si el usuario tiene permiso para ver este CV
    try:
        jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
        if jobseeker_profile.cv != cv:
            messages.error(request, 'No tienes permiso para ver este CV.')
            return redirect('profile')
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'No se pudo verificar tu perfil.')
        return redirect('home')
    
    # Verificar acciones por GET
    action = request.GET.get('action', '')
    if action == 'correct':
        return render(request, 'correct_cv.html', {'cv': cv})
    elif action == 'delete':
        return render(request, 'confirm_delete_cv.html', {'cv': cv})
    
    
    # Si el método es POST, procesar la corrección del texto
    if request.method == 'POST' and 'corrected_text' in request.POST:
        # Guardar el texto corregido
        cv.extracted_text = request.POST['corrected_text']
        cv.save()
        
        # Actualizar el perfil con la información corregida
        try:
            # Obtener el perfil de JobSeeker
            jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
            
            # Extraer información del texto corregido para actualizar el perfil
            jobseeker_profile = extract_and_update_profile_data(jobseeker_profile, cv.extracted_text)
            jobseeker_profile.save()
            
            messages.success(request, '¡Texto corregido y perfil actualizado correctamente!')
        except JobSeekerProfile.DoesNotExist:
            messages.warning(request, 'Texto corregido pero no se pudo actualizar el perfil.')
    
    return render(request, 'cv_detail.html', {'cv': cv})

@login_required
def delete_cv(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    
    # Verificar que el usuario tiene permiso para eliminar este CV
    try:
        profile = request.user.profile
        if profile.cv == cv:
            # Desasociar el CV del perfil
            profile.cv = None
            profile.save()
            
            # Eliminar el CV de la base de datos
            cv.delete()
            messages.success(request, '¡CV eliminado exitosamente!')
        else:
            messages.error(request, 'No tienes permiso para eliminar este CV.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el CV: {str(e)}')
    
    return redirect('profile')

def process_ocr(request, pk):
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

def test_extraction(request):
    if not settings.DEBUG:
        return HttpResponse("Esta vista solo está disponible en modo DEBUG")
    
    context = {
        'pdf_extraction_works': False,
        'image_extraction_works': False,
        'errors': []
    }
    
    # Probar extracción de PDF
    try:
        # Crear un PDF simple para prueba
        from reportlab.pdfgen import canvas
        from tempfile import NamedTemporaryFile
        
        temp_pdf = NamedTemporaryFile(suffix='.pdf', delete=False)
        pdf_path = temp_pdf.name
        temp_pdf.close()
        
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 750, "Texto de prueba para OCR")
        c.save()
        
        # Extraer texto
        extracted_text = extract_text_from_pdf(pdf_path)
        context['pdf_extraction_works'] = "prueba" in extracted_text.lower()
        context['pdf_extracted_text'] = extracted_text
    except Exception as e:
        context['errors'].append(f"Error en PDF: {str(e)}")
    
    # Probar extracción de imagen
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear una imagen simple para prueba
        img = Image.new('RGB', (300, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10,10), "Texto de prueba para OCR en imagen", fill=(0,0,0))
        
        temp_img = NamedTemporaryFile(suffix='.png', delete=False)
        img_path = temp_img.name
        temp_img.close()
        
        img.save(img_path)
        
        # Extraer texto
        try:
            extracted_text = pytesseract.image_to_string(Image.open(img_path), lang='spa+eng')
            context['image_extraction_works'] = "prueba" in extracted_text.lower()
            context['image_extracted_text'] = extracted_text
        except Exception as tesseract_e:
            context['errors'].append(f"Error en Tesseract: {str(tesseract_e)}")
    except Exception as e:
        context['errors'].append(f"Error en imagen: {str(e)}")
    
    return render(request, 'test_extraction.html', context)

def extract_and_update_profile_data(profile, text):    
    text_lower = text.lower()
    lines = text.split('\n')
    
    # 1. Detectar nombre completo (generalmente al inicio del CV)
    if not profile.full_name:
        # Buscar en las primeras líneas del CV
        name_patterns = [
            r'^([A-ZÁ-Ú][a-zá-ú]+\s+[A-ZÁ-Ú][a-zá-ú]+(\s+[A-ZÁ-Ú][a-zá-ú]+)?)',  # Patrón para "Nombre Apellido"
            r'^(CV|CURRICULUM VITAE|HOJA DE VIDA)[:\s-]*([A-ZÁ-Ú][a-zá-ú]+\s+[A-ZÁ-Ú][a-zá-ú]+)'  # Patrón para "CV: Nombre Apellido"
        ]
        
        for i, line in enumerate(lines[:10]):  # Revisar solo las primeras 10 líneas
            for pattern in name_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    profile.full_name = match.group(1).strip()
                    break
            if profile.full_name:
                break
    
    # 2. Detectar título profesional
    if not profile.professional_title:
        # Buscar palabras clave de profesiones comunes
        professional_titles = [
            "ingeniero", "desarrollador", "programador", "diseñador", "analista", 
            "gerente", "director", "especialista", "consultor", "asistente",
            "arquitecto", "contador", "abogado", "médico", "profesor",
            "psicólogo", "administrador", "economista", "periodista"
        ]
        
        # Buscar patrones como "Ingeniero de Sistemas", "Desarrollador Web", etc.
        title_patterns = [
            r'(ingeniero\s+(?:de|en)\s+\w+)',
            r'(desarrollador\s+(?:de|en)\s+\w+)',
            r'(analista\s+(?:de|en)\s+\w+)',
            r'(\w+\s+senior)',
            r'(\w+\s+junior)',
            r'(licenciado\s+(?:de|en)\s+\w+)',
        ]
        
        # Buscar en los primeros párrafos
        first_paragraphs = ' '.join(lines[:15])
        
        for pattern in title_patterns:
            match = re.search(pattern, first_paragraphs, re.IGNORECASE)
            if match:
                profile.professional_title = match.group(1).title()
                break
        
        # Si no se encontró un patrón específico, buscar palabras clave
        if not profile.professional_title:
            for title in professional_titles:
                if title in text_lower:
                    # Buscar contexto alrededor del título
                    idx = text_lower.find(title)
                    start = max(0, idx - 20)
                    end = min(len(text_lower), idx + 50)
                    context = text_lower[start:end]
                    
                    # Extraer una frase coherente
                    words = context.split()
                    title_idx = -1
                    for i, word in enumerate(words):
                        if title in word:
                            title_idx = i
                            break
                    
                    if title_idx >= 0:
                        # Extraer hasta 5 palabras para formar el título
                        title_words = words[max(0, title_idx-1):min(len(words), title_idx+4)]
                        profile.professional_title = ' '.join([w.capitalize() for w in title_words])
                        break
    
    # 3. Detectar años de experiencia
    if not profile.years_experience:
        experience_patterns = [
            r'(\d+)\s+años\s+de\s+experiencia',
            r'experiencia\s+(?:de|:)\s+(\d+)\s+años',
            r'(\d+)\s+años\s+en\s+el\s+sector',
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    years = int(match.group(1))
                    if 0 <= years <= 50:  # Valor razonable de años
                        profile.years_experience = years
                        break
                except:
                    pass
    
    # 4. Detectar habilidades comunes
    common_skills = [
        "python", "java", "javascript", "html", "css", "django", "react", "angular", 
        "node.js", "sql", "marketing", "ventas", "comunicación", "liderazgo", 
        "desarrollo web", "gestión de proyectos", "excel", "word", "powerpoint",
        "photoshop", "illustrator", "php", "ruby", "c++", "c#", ".net", "aws",
        "docker", "kubernetes", "machine learning", "data science", "análisis de datos"
    ]
    
    # Buscar sección de habilidades
    skill_section_patterns = [
        r'(?:habilidades|skills|competencias)[\s:]+(.+?)(?:\n\n|\n\w+:)',
        r'(?:technical skills|conocimientos técnicos)[\s:]+(.+?)(?:\n\n|\n\w+:)'
    ]
    
    detected_skills = []
    
    # Primero intentar extraer de una sección específica
    for pattern in skill_section_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            skills_text = match.group(1)
            # Extraer habilidades de la sección encontrada
            potential_skills = re.findall(r'(\w+(?:\s+\w+){0,2})', skills_text)
            for skill in potential_skills:
                skill = skill.strip()
                if len(skill) > 3 and skill not in detected_skills:
                    detected_skills.append(skill.capitalize())
    
    # Si no se encontraron habilidades en secciones, buscar en todo el texto
    if not detected_skills:
        for skill in common_skills:
            if skill in text_lower:
                detected_skills.append(skill.capitalize())
    
    if detected_skills and not profile.skills:
        profile.skills = ", ".join(detected_skills)
    
    # 5. Detectar idiomas
    languages = ["inglés","español", "francés", "alemán", "italiano", "portugués", "chino", "japonés", "ruso"]
    level_terms = ["nativo", "fluido", "avanzado", "intermedio", "básico"]
    
    # Buscar sección de idiomas
    language_section_patterns = [
        r'(?:idiomas|languages)[\s:]+(.+?)(?:\n\n|\n\w+:)',
    ]
    
    detected_languages = []
    
    # Primero intentar extraer de una sección específica
    for pattern in language_section_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            lang_text = match.group(1)
            # Extraer idiomas con nivel si está disponible
            for lang in languages:
                if lang in lang_text:
                    # Buscar si hay un nivel asociado
                    for level in level_terms:
                        if level in lang_text:
                            detected_languages.append(f"{lang.capitalize()} ({level.capitalize()})")
                            break
                    else:
                        detected_languages.append(lang.capitalize())
    
    # Si no se encontraron idiomas en secciones, buscar en todo el texto
    if not detected_languages:
        for lang in languages:
            if lang in text_lower:
                detected_languages.append(lang.capitalize())
    
    if detected_languages and not profile.languages:
        profile.languages = ", ".join(detected_languages)
    
    # 6. Detectar educación
    if not profile.education:
        # Buscar sección de educación
        education_section_patterns = [
            r'(?:educación|education|formación académica)[\s:]+(.+?)(?:\n\n|\n\w+:)',
        ]
        
        for pattern in education_section_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                edu_text = match.group(1).strip()
                if len(edu_text) > 10:  # Asegurarse que tiene contenido significativo
                    profile.education = edu_text.capitalize()
                    break
    
    # 7. Detectar ubicación
    if not profile.location:
        location_patterns = [
            r'(?:dirección|location|ubicación)[\s:]+(.+?)(?:\n|\n\n)',
            r'(?:ciudad|city)[\s:]+(.+?)(?:\n|\n\n)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                profile.location = match.group(1).strip().capitalize()
                break
    
    # 8. Detectar número telefónico
    if not profile.phone_number:
        phone_patterns = [
            r'(?:teléfono|phone|celular|móvil|tel)[\s:]+(\+?\d[\d\s-]{8,})',
            r'(\+\d{1,3}\s?\d{3}[\s-]?\d{3}[\s-]?\d{4})',
            r'(\d{3}[\s-]?\d{3}[\s-]?\d{4})',
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                profile.phone_number = match.group(1).strip()
                break
    
    return profile