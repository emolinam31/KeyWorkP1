# KeyWorkProject/populate_db.py
import os
import django
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KeyWork.settings')
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth.models import User
from UserManagement.models import JobSeekerProfile, EmployerProfile
from JobSeekerPortal.models import JobOffer, JobApplication
from CollectionPoint.models import CV
from django.utils.crypto import get_random_string

# Datos de muestra
JOB_TITLES = [
    "Desarrollador Web Frontend", "Desarrollador Web Backend", "Desarrollador Full Stack",
    "Ingeniero de Software", "Analista de Datos", "Científico de Datos", 
    "Diseñador UX/UI", "Gerente de Proyectos", "Especialista en Marketing Digital",
    "Contador", "Asistente Administrativo", "Recursos Humanos", "Asesor Financiero",
    "Ingeniero de DevOps", "Ingeniero de QA", "Especialista de Ciberseguridad",
    "Analista de Negocios", "Consultor SAP", "Arquitecto de Software"
]

SKILLS = [
    "Python", "Java", "JavaScript", "HTML", "CSS", "Django", "React", "Angular", 
    "Node.js", "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "Git", "Excel",
    "Power BI", "Tableau", "Marketing Digital", "SEO", "SEM", "Photoshop", 
    "Illustrator", "Figma", "Sketch", "JIRA", "Scrum", "Agile", "Comunicación",
    "Liderazgo", "Trabajo en equipo", "Resolución de problemas", "Office"
]

COMPANIES = [
    "TechSolutions Inc.", "DataWorks", "Innovate Software", "WebDev Experts", 
    "Digital Solutions", "CreativeMinds", "CloudTech", "FinanceWorks",
    "HealthTech Inc.", "EduTech Solutions", "GreenEnergy Systems", "Smart Construction",
    "LogisticsPlus", "MarketingPro", "TalentFinders", "GlobalConsulting",
    "SecurityPlus", "MobileDev", "AIExperts", "BlockchainTech"
]

LOCATIONS = [
    "Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena",
    "Bucaramanga", "Pereira", "Manizales", "Pasto", "Villavicencio",
    "Remoto Colombia", "Remoto Internacional"
]

JOB_TYPES = ["full_time", "part_time", "contract", "freelance", "internship"]

REQUIREMENTS_TEMPLATES = [
    "Buscamos profesionales con experiencia en {skills} y conocimiento en {extra_skill}.",
    "Se requiere experiencia mínima de {years} años trabajando con {skills}. Valorable conocimientos en {extra_skill}.",
    "El candidato ideal debe tener sólidos conocimientos en {skills} y capacidad para {extra_skill}.",
    "Imprescindible experiencia con {skills}. Se valorará positivamente {extra_skill}.",
    "Profesional con al menos {years} años de experiencia. Conocimientos avanzados en {skills} y {extra_skill}."
]

DESCRIPTIONS_TEMPLATES = [
    "Empresa líder en el sector busca incorporar {job_title} para proyecto de {duration} meses. Trabajarás en un ambiente dinámico con las últimas tecnologías.",
    "Importante empresa del sector {sector} precisa incorporar {job_title}. Ofrecemos plan de carrera y excelente ambiente laboral.",
    "Únete a nuestro equipo como {job_title}. Buscamos personas apasionadas con ganas de crecer profesionalmente en un entorno innovador.",
    "Buscamos {job_title} para incorporación inmediata. Proyecto estable con posibilidad de contrato indefinido.",
    "¿Tienes experiencia como {job_title}? ¡Esta es tu oportunidad! Empresa en expansión busca ampliar su equipo técnico."
]

NAMES = [
    "Juan Pérez", "María Rodríguez", "Carlos López", "Ana García", "Luis Martínez",
    "Laura González", "Pedro Sánchez", "Sofía Torres", "Miguel Ramírez", "Valentina Castro",
    "Andrés Vargas", "Daniela Morales", "Javier Ortiz", "Camila Jiménez", "Sebastián Ruiz",
    "Isabella Suárez", "Diego Gómez", "Gabriela Díaz", "Mateo Pardo", "Victoria Herrera",
    "Santiago Ospina", "Valeria Rojas", "Alejandro Parra", "Natalia Navarro", "Felipe Duarte"
]

PROFESSIONAL_TITLES = [
    "Ingeniero de Sistemas", "Desarrollador de Software", "Analista de Datos",
    "Diseñador Web", "Especialista en Marketing Digital", "Arquitecto de Software",
    "Científico de Datos", "Ingeniero DevOps", "Programador Full Stack",
    "Contador", "Administrador de Empresas", "Psicólogo Organizacional",
    "Economista", "Gerente de Proyectos", "Consultor de IT"
]

EDUCATION_TEMPLATES = [
    "Pregrado en {degree}, Universidad de {university}.",
    "Maestría en {degree}, Universidad {university}.",
    "{degree}, Universidad {university}. {year}",
    "Ingeniero/a {degree}, Universidad {university}. {year}",
    "Profesional en {degree}, Universidad {university}."
]

DEGREES = [
    "Ingeniería de Sistemas", "Desarrollo de Software", "Ciencias de la Computación",
    "Diseño Gráfico", "Marketing", "Administración de Empresas", "Contaduría",
    "Economía", "Psicología", "Ingeniería Industrial", "Diseño UX/UI",
    "Ciencia de Datos", "Ingeniería Informática", "Comunicación Social"
]

UNIVERSITIES = [
    "Los Andes", "Nacional", "Javeriana", "del Rosario", "EAFIT",
    "del Valle", "UPB", "Externado", "del Norte", "ICESI",
    "Antioquia", "Sabana", "Univalle", "UNAL", "UTadeo"
]

LANGUAGES = [
    "Español (Nativo)", "Inglés (Avanzado)", "Inglés (Intermedio)", "Inglés (Básico)",
    "Francés (Básico)", "Francés (Intermedio)", "Portugués (Básico)", "Alemán (Básico)"
]

CV_TEMPLATES = [
    """
    # Experiencia Laboral
    
    ## {company1}
    {job_title1} | {start_date1} - {end_date1}
    
    - {responsibility1}
    - {responsibility2}
    - {responsibility3}
    
    ## {company2}
    {job_title2} | {start_date2} - {end_date2}
    
    - {responsibility4}
    - {responsibility5}
    - {responsibility6}
    
    # Educación
    
    {education}
    
    # Habilidades
    
    {skills}
    
    # Idiomas
    
    {languages}
    """,
    
    """
    # PERFIL PROFESIONAL
    
    {profile_summary}
    
    # EXPERIENCIA PROFESIONAL
    
    * {job_title1} en {company1}
      {start_date1} - {end_date1}
      {responsibility1}
      {responsibility2}
    
    * {job_title2} en {company2}
      {start_date2} - {end_date2}
      {responsibility4}
      {responsibility5}
    
    # EDUCACIÓN
    
    {education}
    
    # HABILIDADES TÉCNICAS
    
    {skills}
    
    # IDIOMAS
    
    {languages}
    """
]

RESPONSIBILITIES = [
    "Desarrollo de aplicaciones web utilizando {skill1} y {skill2}",
    "Mantenimiento y mejora de sistemas existentes",
    "Diseño e implementación de nuevas funcionalidades",
    "Optimización del rendimiento de aplicaciones",
    "Colaboración con equipos de diseño y producto",
    "Implementación de buenas prácticas de desarrollo",
    "Realización de pruebas y debugging",
    "Participación en reuniones de planificación y revisión",
    "Investigación de nuevas tecnologías y herramientas",
    "Documentación de código y procesos",
    "Gestión de bases de datos y APIs",
    "Análisis y visualización de datos",
    "Desarrollo de estrategias de marketing",
    "Administración de recursos humanos",
    "Gestión financiera y contable",
    "Coordinación de equipos de trabajo",
    "Atención y soporte al cliente",
    "Diseño de interfaces de usuario",
    "Implementación de estrategias SEO/SEM",
    "Administración de servidores y sistemas"
]

PROFILE_SUMMARIES = [
    "Profesional con {years} años de experiencia en {field}. Especialista en {skill1} y {skill2}.",
    "Especialista en {field} con sólidos conocimientos en {skill1}, {skill2} y {skill3}.",
    "{job_title} con {years} años de experiencia en desarrollo de proyectos de {field}.",
    "Profesional apasionado por {field} con experiencia en {skill1} y {skill2}.",
    "Experto en {field} con enfoque en {skill1} y {skill2}. {years} años de experiencia."
]

def generate_random_date(start_years_ago=5, end_years_ago=0):
    """Genera una fecha aleatoria entre start_years_ago y end_years_ago"""
    start_date = datetime.now() - timedelta(days=365*start_years_ago)
    end_date = datetime.now() - timedelta(days=365*end_years_ago)
    delta = end_date - start_date
    return start_date + timedelta(days=random.randint(0, delta.days))

def create_employers(num_employers=10):
    """Crea empleadores de muestra"""
    print(f"Creando {num_employers} empleadores...")
    employers = []
    
    for i in range(num_employers):
        company_name = random.choice(COMPANIES)
        username = f"employer_{company_name.lower().replace(' ', '_')}_{i}"
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123"
        )
        
        # Crear perfil de empleador
        employer = EmployerProfile.objects.create(
            user=user,
            company_name=company_name,
            industry=random.choice(["Tecnología", "Finanzas", "Salud", "Educación", "Manufactura"]),
            company_size=random.choice(["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]),
            company_website=f"https://www.{company_name.lower().replace(' ', '')}.com",
            company_description=f"Empresa líder en el sector de {random.choice(['tecnología', 'servicios', 'consultoría'])}",
            company_location=random.choice(LOCATIONS),
            profile_completed=True
        )
        
        employers.append(employer)
        print(f"  Creado empleador: {company_name}")
    
    return employers

def create_job_seekers(num_seekers=30):
    """Crea buscadores de empleo de muestra"""
    print(f"Creando {num_seekers} buscadores de empleo...")
    job_seekers = []
    
    for i in range(num_seekers):
        full_name = random.choice(NAMES)
        username = f"jobseeker_{full_name.lower().replace(' ', '_')}_{i}"
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123"
        )
        
        # Seleccionar habilidades aleatorias
        skills = random.sample(SKILLS, random.randint(3, 8))
        
        # Generar educación aleatoria
        degree = random.choice(DEGREES)
        university = random.choice(UNIVERSITIES)
        year = random.randint(2010, 2023)
        education = random.choice(EDUCATION_TEMPLATES).format(
            degree=degree,
            university=university,
            year=year
        )
        
        # Seleccionar idiomas aleatorios
        langs = random.sample(LANGUAGES, random.randint(1, 3))
        
        # Crear perfil de buscador de empleo
        job_seeker = JobSeekerProfile.objects.create(
            user=user,
            full_name=full_name,
            professional_title=random.choice(PROFESSIONAL_TITLES),
            date_of_birth=generate_random_date(start_years_ago=40, end_years_ago=20),
            phone_number=f"+57 3{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
            location=random.choice(LOCATIONS),
            bio=f"Profesional con experiencia en {', '.join(skills[:2])}. Interesado en {random.choice(['desarrollo de software', 'análisis de datos', 'diseño web', 'marketing digital'])}.",
            years_experience=random.randint(0, 15),
            skills=", ".join(skills),
            education=education,
            languages=", ".join(langs),
            availability=random.choice(['immediate', '2_weeks', '1_month', 'negotiable']),
            desired_salary=random.randint(1500000, 8000000),
            remote_work=random.choice([True, False]),
            profile_completed=True
        )
        
        # Crear CV para el buscador
        create_cv_for_job_seeker(job_seeker, skills)
        
        job_seekers.append(job_seeker)
        print(f"  Creado buscador: {full_name}")
    
    return job_seekers

def create_cv_for_job_seeker(job_seeker, skills):
    """Crea un CV para un buscador de empleo"""
    # Generar texto del CV
    company1 = random.choice(COMPANIES)
    company2 = random.choice(COMPANIES)
    job_title1 = random.choice(JOB_TITLES)
    job_title2 = random.choice(JOB_TITLES)
    
    # Fechas de experiencia
    start_date1 = generate_random_date(start_years_ago=10, end_years_ago=5).strftime("%b %Y")
    end_date1 = generate_random_date(start_years_ago=5, end_years_ago=2).strftime("%b %Y")
    start_date2 = generate_random_date(start_years_ago=5, end_years_ago=1).strftime("%b %Y")
    end_date2 = "Presente"
    
    # Seleccionar responsabilidades aleatorias y formatearlas
    resp_skills = random.sample(skills, min(4, len(skills)))
    responsibilities = random.sample(RESPONSIBILITIES, 6)
    for i, resp in enumerate(responsibilities[:3]):
        try:
            responsibilities[i] = resp.format(
                skill1=resp_skills[0], 
                skill2=resp_skills[1] if len(resp_skills) > 1 else resp_skills[0]
            )
        except:
            pass
    
    # Generar resumen de perfil
    profile_summary = random.choice(PROFILE_SUMMARIES).format(
        years=job_seeker.years_experience,
        field=random.choice(["tecnología", "desarrollo web", "análisis de datos", "marketing digital"]),
        job_title=job_seeker.professional_title,
        skill1=skills[0] if skills else "",
        skill2=skills[1] if len(skills) > 1 else "",
        skill3=skills[2] if len(skills) > 2 else ""
    )
    
    # Generar texto del CV usando una plantilla
    cv_text = random.choice(CV_TEMPLATES).format(
        company1=company1,
        company2=company2,
        job_title1=job_title1,
        job_title2=job_title2,
        start_date1=start_date1,
        end_date1=end_date1,
        start_date2=start_date2,
        end_date2=end_date2,
        responsibility1=responsibilities[0],
        responsibility2=responsibilities[1],
        responsibility3=responsibilities[2],
        responsibility4=responsibilities[3],
        responsibility5=responsibilities[4],
        responsibility6=responsibilities[5],
        education=job_seeker.education,
        skills=job_seeker.skills,
        languages=job_seeker.languages,
        profile_summary=profile_summary
    )
    
    # Crear el objeto CV
    cv = CV.objects.create(
        file=None,  # No tenemos archivo real
        upload_type='document',
        extracted_text=cv_text
    )
    
    # Asociar CV al perfil
    job_seeker.cv = cv
    job_seeker.has_cv = True
    job_seeker.save()

def create_job_offers(employers, num_offers=50):
    """Crea ofertas de trabajo de muestra"""
    print(f"Creando {num_offers} ofertas de trabajo...")
    job_offers = []
    
    for i in range(num_offers):
        # Seleccionar empleador aleatorio
        employer = random.choice(employers)
        
        # Seleccionar título aleatorio
        title = random.choice(JOB_TITLES)
        
        # Seleccionar habilidades aleatorias para requisitos
        required_skills = random.sample(SKILLS, random.randint(3, 7))
        
        # Generar requisitos con template
        requirements = random.choice(REQUIREMENTS_TEMPLATES).format(
            skills=", ".join(required_skills[:3]),
            extra_skill=random.choice(SKILLS),
            years=random.randint(1, 5)
        )
        
        # Generar descripción con template
        description = random.choice(DESCRIPTIONS_TEMPLATES).format(
            job_title=title,
            duration=random.randint(3, 18),
            sector=random.choice(["tecnología", "financiero", "salud", "educación"])
        )
        
        # Fecha de expiración (entre 15 y 60 días en el futuro)
        expires_at = datetime.now() + timedelta(days=random.randint(15, 60))
        
        # Crear oferta de trabajo
        job_offer = JobOffer.objects.create(
            title=title,
            company=employer.company_name,
            location=random.choice(LOCATIONS),
            description=description,
            requirements=requirements,
            salary_range=f"${random.randint(1, 10)}.{random.randint(0, 9)}{random.randint(0, 9)}0.000 - ${random.randint(10, 20)}.{random.randint(0, 9)}{random.randint(0, 9)}0.000",
            job_type=random.choice(JOB_TYPES),
            remote=random.choice([True, False]),
            expires_at=expires_at,
            active=True
        )
        
        job_offers.append(job_offer)
        print(f"  Creada oferta: {title} - {employer.company_name}")
    
    return job_offers

def create_applications(job_seekers, job_offers, num_applications=100):
    """Crea aplicaciones a ofertas de trabajo de muestra"""
    print(f"Creando {num_applications} aplicaciones...")
    total_possible = min(num_applications, len(job_seekers) * len(job_offers))
    
    # Generar pares únicos de (buscador, oferta)
    pairs = []
    for _ in range(total_possible):
        seeker = random.choice(job_seekers)
        offer = random.choice(job_offers)
        
        # Evitar duplicados
        if (seeker, offer) not in pairs:
            pairs.append((seeker, offer))
    
    applications = []
    for seeker, offer in pairs[:num_applications]:
        # Generar carta de presentación
        cover_letter = f"""
        Estimado/a Responsable de Selección de {offer.company},
        
        Me dirijo a ustedes con interés en la posición de {offer.title} que he visto publicada en KeyWork. 
        Considero que mi experiencia en {', '.join(random.sample(seeker.skills.split(', '), min(2, len(seeker.skills.split(', ')))))} 
        y mis {seeker.years_experience} años de experiencia me convierten en un buen candidato para esta posición.
        
        Me entusiasma especialmente la oportunidad de {random.choice(['trabajar en proyectos desafiantes', 'formar parte de un equipo innovador', 'desarrollar nuevas habilidades', 'contribuir al crecimiento de su empresa'])}.
        
        Quedo a su disposición para ampliar cualquier información que consideren necesaria.
        
        Saludos cordiales,
        {seeker.full_name}
        """
        
        # Crear aplicación
        application = JobApplication.objects.create(
            job_seeker=seeker,
            job_offer=offer,
            cover_letter=cover_letter,
            status=random.choice(['applied', 'in_review', 'interview', 'rejected', 'accepted']),
            applied_at=generate_random_date(start_years_ago=1, end_years_ago=0)
        )
        
        applications.append(application)
        print(f"  Creada aplicación: {seeker.full_name} → {offer.title}")
    
    return applications

def run():
    """Ejecuta la población de la base de datos"""
    print("Iniciando población de la base de datos...")
    
    # Limpiar datos existentes si es necesario
    should_delete = input("¿Desea eliminar los datos existentes? (s/n): ").strip().lower()
    if should_delete == 's':
        print("Eliminando datos existentes...")
        JobApplication.objects.all().delete()
        JobOffer.objects.all().delete()
        
        # Obtener todos los job seekers para eliminar sus CVs
        seekers = JobSeekerProfile.objects.all()
        for seeker in seekers:
            if seeker.cv:
                cv_id = seeker.cv.id
                seeker.cv = None
                seeker.has_cv = False
                seeker.save()
                CV.objects.filter(id=cv_id).delete()
        
        # Eliminar usuarios (esto eliminará perfiles por cascade)
        User.objects.filter(username__startswith='employer_').delete()
        User.objects.filter(username__startswith='jobseeker_').delete()
    
    # Crear datos
    employers = create_employers(10)
    job_seekers = create_job_seekers(30)
    job_offers = create_job_offers(employers, 50)
    applications = create_applications(job_seekers, job_offers, 100)
    
    print("\nPoblación de la base de datos completada con éxito.")
    print(f"  Empleadores creados: {len(employers)}")
    print(f"  Buscadores de empleo creados: {len(job_seekers)}")
    print(f"  Ofertas de trabajo creadas: {len(job_offers)}")
    print(f"  Aplicaciones creadas: {len(applications)}")

if __name__ == "__main__":
    run()