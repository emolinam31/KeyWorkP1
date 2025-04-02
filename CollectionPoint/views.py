from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
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

def upload_cv(request):
    """Sube un CV, lo almacena y extrae texto si es PDF o imagen."""
    if request.method == 'POST' and request.FILES.get('file'):
        upload_type = request.POST.get('upload_type', 'document')
        uploaded_file = request.FILES['file']

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

        messages.success(request, 'CV uploaded successfully!')
        return redirect('cv_detail', pk=cv.pk)

    return redirect('home')

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

        messages.success(request, 'Text extraction completed successfully!')
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        print(error_msg)
        cv.extracted_text = "OCR processing failed. You may need to install Tesseract OCR."
        cv.save()
        messages.error(request, error_msg)

    return redirect('cv_detail', pk=cv.pk)
