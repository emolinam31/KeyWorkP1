# KeyWork - Plataforma de Búsqueda de Empleo con IA
KeyWork es una aplicación web desarrollada en Django que permite a los buscadores de empleo subir sus CVs en diferentes formatos y a los empleadores publicar ofertas de trabajo. La plataforma utiliza inteligencia artificial para extraer información de los CVs y generar coincidencias óptimas entre candidatos y ofertas laborales.
#Características Principales
## Para Buscadores de Empleo

- Registro y gestión de perfil profesional
- Carga de CV en múltiples formatos (PDF, imagen)
- Extracción automática de información del CV
- Búsqueda y aplicación a ofertas de trabajo
- Sistema de notificaciones para comunicaciones de empleadores

## Para Empleadores

- Gestión de perfil de empresa
- Publicación y gestión de ofertas de trabajo
- Sistema de coincidencia automática de candidatos (ATS)
- Herramientas para contactar candidatos potenciales
- Gestión de aplicaciones recibidas

# Requisitos del Sistema

- python 3.12 o superior
- Django 5.1.6 o superior
- Base de datos SQLite (por defecto) o PostgreSQL para producción
- Conexión a Internet para la integración con OpenAI API

# Instalación
## 1. Preparar el entorno
Primero, clone el repositorio y prepare un entorno virtual:
bashgit clone https://github.com/your-username/KeyWork.git
cd KeyWork
python -m venv venv
Active el entorno virtual:
En Windows:
venv\Scripts\activate
En macOS/Linux:
source venv/bin/activate
## 2. Instalar dependencias
Instale las dependencias necesarias para el proyecto:
pip install django==5.1.6
pip install reportlab
pip install pdf2image
pip install PyPDF2
pip install pytesseract
pip install Pillow
pip install openai
pip install python-dotenv
pip install numpy
## 3. Configurar OpenAI API
Cree un archivo .env en la raíz del proyecto (mismo nivel que manage.py) con su clave API de OpenAI:
OPENAI_API_KEY=su_clave_api_aqui
## 4. Configurar Tesseract OCR
Para la extracción de texto de imágenes, necesita instalar Tesseract OCR:
En Windows:

Descargue e instale Tesseract desde https://github.com/UB-Mannheim/tesseract/wiki
Asegúrese de que la ruta a tesseract.exe esté en PATH o configúrelo en settings.py

En macOS:
bashbrew install tesseract
En Linux:
bashsudo apt install tesseract-ocr
sudo apt install libtesseract-dev
## 5. Configurar la Base de Datos
Aplique las migraciones para configurar la base de datos:
bashpython manage.py makemigrations
python manage.py migrate
## 6. Crear un Superusuario
Cree un superusuario para administrar la plataforma:
bashpython manage.py createsuperuser
## 7. Ejecutar el Servidor de Desarrollo
Inicie el servidor de desarrollo:
bashpython manage.py runserver
Ahora puede acceder a la aplicación en http://127.0.0.1:8000/
Arquitectura del Proyecto
# KeyWork está organizado en cuatro aplicaciones de Django principales:

- UserManagement: Gestión de usuarios, perfiles de buscadores de empleo y empleadores.
- CollectionPoint: Gestión de CVs, extracción de texto y procesamiento.
- JobSeekerPortal: Portal para buscadores de empleo, ofertas de trabajo y aplicaciones.
- EmployerPortal: Portal para empleadores, gestión de ofertas y sistema ATS.

## Integración con OpenAI
El proyecto utiliza la API de OpenAI para:

Generar embeddings de ofertas de trabajo y CVs
Calcular similitud entre embeddings para encontrar coincidencias
Proporcionar resultados ordenados por porcentaje de compatibilidad

La configuración se gestiona a través del módulo utils/openai_utils.py.
Funcionalidades Técnicas Destacadas
Extracción de Texto de Documentos
El sistema puede extraer texto de varios formatos:

## Documentos PDF: Utilizando PyPDF2 para la extracción directa y pdf2image + Tesseract OCR para PDFs basados en imágenes.
Imágenes: Procesamiento OCR con Pillow y Tesseract.

## Sistema de Coincidencia ATS
El Applicant Tracking System (ATS) funciona mediante los siguientes pasos:

Extracción de información relevante de las ofertas de trabajo
Generación de embeddings vectoriales con OpenAI
Procesamiento de CVs y perfiles de candidatos
Cálculo de similitud del coseno entre vectores
Ordenamiento de candidatos según porcentaje de coincidencia

Notificaciones en Tiempo Real
Sistema de notificaciones que permite:

Alertar a candidatos cuando son contactados
Informar sobre cambios en el estado de aplicaciones
Proporcionar información relevante sobre oportunidades

# Estructura de la Base de Datos
El modelo de datos incluye las siguientes entidades principales:

- User: Usuarios de la plataforma (Django auth)
- JobSeekerProfile: Perfiles de buscadores de empleo
- EmployerProfile: Perfiles de empleadores
- CV: Documentos subidos por candidatos
- JobOffer: Ofertas de trabajo publicadas
- JobApplication: Aplicaciones a ofertas
- Notification: Sistema de notificaciones
- CandidateMatch: Resultados del sistema ATS

# Despliegue en Producción
Para desplegar en producción, se recomiendan los siguientes pasos adicionales:

# Configurar una base de datos PostgreSQL
Implementar un servidor web como Nginx o Apache
Utilizar Gunicorn como servidor WSGI
Configurar variables de entorno para producción
Implementar HTTPS mediante Let's Encrypt
Configurar un servicio de correo electrónico

# Datos de Prueba
Para probar la aplicación con datos de ejemplo, ejecute:
python populate_db.py
Este script creará:

Empleadores de prueba con perfiles completos
Buscadores de empleo con CVs
Ofertas de trabajo variadas
Algunas aplicaciones de ejemplo

# Contribución al Proyecto
Para contribuir al desarrollo de KeyWork:

Cree un fork del repositorio
Cree una rama para su funcionalidad
Desarrolle y pruebe su código
Envíe un pull request con descripción detallada
