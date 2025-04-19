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
    """Extrae texto de un archivo PDF. Si no hay texto embebido, usa OCR."""
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
    """Sube un CV, lo almacena y extrae texto si es PDF o imagen."""
    if request.method == 'POST':
        # Procesar el archivo subido
        if request.FILES.get('file'):
            # Si hay un archivo, procesarlo
            upload_type = request.POST.get('upload_type', 'document')
            uploaded_file = request.FILES['file']

            # Guardar en el modelo
            cv = CV(
                file=uploaded_file,
                upload_type=upload_type
            )
            cv.save()
            print(f"CV guardado con ID: {cv.id}, Tipo: {upload_type}")

            extracted_text = ""

            # Si es un documento PDF, extraer texto con PyPDF2 y OCR si es necesario
            if upload_type == 'document' and uploaded_file.name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(cv.file.path)
                cv.extracted_text = extracted_text
                cv.save()
                print(f"Texto extraído y guardado para PDF")

            # Si es una imagen, procesar con OCR
            elif upload_type == 'image':
                try:
                    img = Image.open(cv.file.path)
                    extracted_text = pytesseract.image_to_string(img, lang='spa+eng')

                    # Guardar el texto extraído
                    cv.extracted_text = extracted_text
                    cv.save()
                    print(f"Texto extraído y guardado para imagen")

                    messages.success(request, 'Image uploaded and text extracted successfully!')
                except Exception as e:
                    print(f"OCR Error: {e}")
                    messages.warning(request, 'CV uploaded but text extraction failed.')

            # Si el usuario es un JobSeeker, asociar el CV con su perfil
            if request.user.is_authenticated:
                try:
                    # Obtener el perfil del usuario
                    profile = request.user.profile
                    print(f"Perfil obtenido para usuario {request.user.username}, tipo: {profile.user_type}")
                    
                    if profile.user_type == 'jobseeker':
                        # Asociar CV con el perfil en una transacción para garantizar la consistencia
                        with transaction.atomic():
                            print(f"Asignando CV {cv.id} a perfil {profile.id}")
                            old_cv = profile.cv
                            profile.cv = cv
                            
                            # Intentar extraer información básica del texto si existe
                            if extracted_text:
                                print(f"Extrayendo información del texto para el perfil")
                                extract_and_update_profile_data(profile, extracted_text)
                            
                            profile.save()
                            print(f"Perfil guardado correctamente. CV asignado: {profile.cv.id if profile.cv else None}")
                        
                        messages.success(request, '¡CV subido y asociado a tu perfil exitosamente!')
                        
                        # Si el usuario tenía un CV anterior y es diferente al nuevo, registrarlo en los logs
                        if old_cv and old_cv.id != cv.id:
                            print(f"El usuario tenía un CV anterior (ID: {old_cv.id}) que ha sido reemplazado")
                    else:
                        print(f"El usuario no es jobseeker, es {profile.user_type}")
                        messages.warning(request, 'Solo los usuarios con perfil de buscador de empleo pueden asociar un CV a su perfil.')
                except Exception as e:
                    import traceback
                    print(f"Error al asociar CV al perfil: {str(e)}")
                    print(traceback.format_exc())
                    messages.warning(request, f'CV subido pero no se pudo asociar al perfil: {str(e)}')

            messages.success(request, 'CV uploaded successfully!')
            return redirect('cv_detail', pk=cv.id)
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
        # Mostrar opciones de tipo de archivo
        return render(request, 'upload_options.html', {
            'title': 'Selecciona el tipo de CV que deseas subir'
        })
        
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

@login_required
def delete_cv(request, pk):
    """Eliminar un CV."""
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

def test_extraction(request):
    """Vista para probar la extracción de texto (solo para desarrollo)."""
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