# script_create_jobs.py
import os
import django
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KeyWork.settings')
django.setup()

# Importar modelos después de configurar Django
from UserManagement.models import EmployerProfile
from JobSeekerPortal.models import JobOffer

# Datos de muestra s
JOB_TITLES = [
    "Desarrollador Web Frontend", "Desarrollador Web Backend", "Desarrollador Full Stack",
    "Ingeniero de Software", "Analista de Datos", "Diseñador UX/UI", "Gerente de Proyectos"
]

LOCATIONS = ["Bogotá", "Medellín", "Cali", "Remoto Colombia"]

JOB_TYPES = ["full_time", "part_time", "contract", "freelance", "internship"]

def create_job_offers(num_offers=10):
    """Crea ofertas de trabajo de muestra"""
    print(f"Creando {num_offers} ofertas de trabajo...")
    
    # Obtener empleadores existentes
    employers = EmployerProfile.objects.all()
    if not employers:
        print("Error: No hay empleadores en la base de datos.")
        return []
    
    job_offers = []
    for i in range(num_offers):
        try:
            # Seleccionar empleador aleatorio
            employer = random.choice(employers)
            
            # Crear oferta de trabajo
            job_offer = JobOffer.objects.create(
                title=random.choice(JOB_TITLES),
                company=employer.company_name,
                location=random.choice(LOCATIONS),
                description="Descripción de la oferta de trabajo",
                requirements="Requisitos para el puesto",
                salary_range=f"${random.randint(2, 10)} - ${random.randint(11, 20)} millones",
                job_type=random.choice(JOB_TYPES),
                remote=random.choice([True, False]),
                expires_at=datetime.now() + timedelta(days=30),
                active=True
            )
            
            job_offers.append(job_offer)
            print(f"  Creada oferta: {job_offer.title} - {employer.company_name}")
        except Exception as e:
            print(f"Error al crear oferta {i+1}: {str(e)}")
    
    return job_offers

if __name__ == "__main__":
    create_job_offers(10)
