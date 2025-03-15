from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CV
import pytesseract
from PIL import Image
import os
from django.conf import settings

pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
        
        # Si es una imagen, procesar con OCR
        if upload_type == 'image':
            try:
                # Configurar Tesseract si está definido en settings
                if hasattr(settings, 'TESSERACT_CMD'):
                    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
                
                # Procesar la imagen con OCR
                img = Image.open(cv.file.path)
                extracted_text = pytesseract.image_to_string(img)
                
                # Guardar el texto extraído
                cv.extracted_text = extracted_text
                cv.save()
                
                # Mensaje de éxito específico para OCR
                messages.success(request, 'Image uploaded and text extracted successfully!')
                return redirect('cv_detail', pk=cv.pk)
            except Exception as e:
                print(f"OCR Error: {e}")
                messages.warning(request, 'CV uploaded but text extraction failed.')
        else:
            messages.success(request, 'CV uploaded successfully!')
        
        # Redireccionar a la página de detalle si es una imagen
        if upload_type == 'image':
            return redirect('cv_detail', pk=cv.pk)
        
        return redirect('home')
    
    return redirect('home')

def cv_detail(request, pk):
    """Vista para mostrar los detalles del CV y el texto extraído si es una imagen"""
    cv = get_object_or_404(CV, pk=pk)
    
    return render(request, 'CollectionPoint/cv_detail.html', {
        'cv': cv
    })

# En CollectionPoint/views.py
# En CollectionPoint/views.py
def process_ocr(request, pk):
    """Procesar o reprocesar una imagen existente con OCR"""
    cv = get_object_or_404(CV, pk=pk)
    
    if cv.upload_type != 'image':
        messages.error(request, 'Only images can be processed with OCR')
        return redirect('cv_detail', pk=cv.pk)
    
    try:
        # Intenta importar pytesseract
        import pytesseract
        from PIL import Image
        
        # Intentamos encontrar tesseract en varias rutas comunes
        possible_paths = [
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',
            '/usr/bin/tesseract'
        ]
        
        tesseract_found = False
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    tesseract_found = True
                    break
            except:
                continue
        
        if not tesseract_found:
            raise Exception("Tesseract not found in common locations")
        
        # Procesar la imagen con OCR
        img = Image.open(cv.file.path)
        extracted_text = pytesseract.image_to_string(img)
        
        # Guardar el texto extraído
        cv.extracted_text = extracted_text
        cv.save()
        
        messages.success(request, 'Text extraction completed successfully!')
    except Exception as e:
        # Proporcionar un mensaje de error más amigable
        error_msg = f"Could not process OCR: {str(e)}. Please make sure Tesseract OCR is installed."
        cv.extracted_text = "OCR processing failed. You may need to install Tesseract OCR."
        cv.save()
        messages.error(request, error_msg)
    
    return redirect('cv_detail', pk=cv.pk)