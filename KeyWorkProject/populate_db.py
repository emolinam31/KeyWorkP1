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

# Datos de muestra expandidos a múltiples sectores laborales
JOB_TITLES = [
    # Tecnología
    "Desarrollador Web Frontend", "Desarrollador Web Backend", "Desarrollador Full Stack",
    "Ingeniero de Software", "Analista de Datos", "Científico de Datos", "DevOps Engineer",
    "Diseñador UX/UI", "Especialista en Ciberseguridad", "Administrador de Sistemas",
    "Ingeniero de IA", "Arquitecto de Software", "QA Automation Engineer",
    
    # Salud
    "Enfermero/a", "Médico General", "Fisioterapeuta", "Odontólogo", "Psicólogo Clínico",
    "Nutricionista", "Farmacéutico", "Radiólogo", "Auxiliar de Enfermería", "Terapeuta Ocupacional",
    
    # Finanzas y Administración
    "Contador", "Analista Financiero", "Gerente de Proyectos", "Asistente Administrativo",
    "Consultor Financiero", "Auditor", "Especialista en Recursos Humanos", "Analista de Riesgos",
    "Ejecutivo de Ventas", "Gerente de Operaciones", "Director Comercial", "Analista de Negocios",
    
    # Marketing y Comunicación
    "Especialista en Marketing Digital", "Community Manager", "Diseñador Gráfico",
    "Copywriter", "Periodista", "Relaciones Públicas", "SEO/SEM Specialist",
    "Content Manager", "Analista de Mercado", "Brand Manager",
    
    # Educación
    "Profesor de Primaria", "Profesor de Secundaria", "Tutor", "Pedagogo",
    "Coordinador Académico", "Director de Escuela", "Profesor Universitario",
    
    # Servicios y Turismo
    "Chef", "Recepcionista de Hotel", "Guía Turístico", "Agente de Viajes",
    "Gerente de Restaurante", "Personal de Servicio al Cliente", "Barista",
    
    # Construcción e Ingeniería
    "Arquitecto", "Ingeniero Civil", "Electricista", "Contratista", "Supervisor de Obra",
    "Ingeniero Mecánico", "Topógrafo", "Diseñador de Interiores", "Operador de Maquinaria Pesada",
    
    # Transporte y Logística
    "Conductor de Camión", "Gerente de Logística", "Operador de Almacén",
    "Analista de Cadena de Suministro", "Piloto", "Controlador de Tráfico Aéreo",
    
    # Arte y Entretenimiento
    "Actor/Actriz", "Productor Audiovisual", "Músico", "Fotógrafo", "Artista Plástico",
    "Editor de Video", "Técnico de Sonido", "Ilustrador", "Animador 3D"
]

SKILLS = [
    # Tecnología
    "Python", "Java", "JavaScript", "HTML", "CSS", "Django", "React", "Angular", 
    "Node.js", "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "Git", "C++",
    "C#", "PHP", "Ruby on Rails", "Swift", "Kotlin", "TypeScript", "REST API",
    "GraphQL", "Machine Learning", "Big Data", "Blockchain", "DevOps", "Linux",
    "Cloud Computing", "Network Security", "Agile Methodologies", "Scrum",
    
    # Salud
    "Primeros Auxilios", "Flebotomía", "Cuidado del Paciente", "ECG", "Anatomía",
    "Farmacología", "Fisioterapia", "Psicoterapia", "Diagnóstico Clínico", "Nutrición",
    "Odontología", "Radiología", "Cirugía", "Pediatría", "Geriatría", "Enfermería",
    
    # Finanzas y Administración
    "Excel Avanzado", "SAP", "Contabilidad", "Análisis Financiero", "Inversiones",
    "Gestión de Proyectos", "Presupuestos", "Normativa Fiscal", "Microsoft Office",
    "ERP", "CRM", "Nóminas", "Reclutamiento", "Liderazgo", "Gestión del Tiempo",
    "Negociación", "Resolución de Conflictos", "PRINCE2", "PMP", "ITIL", "Lean Six Sigma",
    
    # Marketing y Comunicación
    "Marketing Digital", "SEO", "SEM", "Google Analytics", "Facebook Ads",
    "Content Marketing", "Inbound Marketing", "Email Marketing", "Social Media",
    "Adobe Photoshop", "Adobe Illustrator", "Canva", "Copywriting", "Storytelling",
    "Redacción Publicitaria", "Planificación de Medios", "Branding", "Market Research",
    
    # Idiomas
    "Inglés", "Francés", "Alemán", "Chino Mandarín", "Italiano", "Portugués",
    "Japonés", "Ruso", "Árabe", "Coreano", "Lengua de Señas",
    
    # Educación
    "Pedagogía", "Didáctica", "Evaluación Educativa", "Psicología Infantil",
    "Educación Especial", "Metodología de Enseñanza", "Diseño Curricular",
    "E-learning", "Gestión Educativa", "TIC en Educación",
    
    # Habilidades Blandas
    "Comunicación Efectiva", "Trabajo en Equipo", "Inteligencia Emocional", "Empatía",
    "Resolución de Problemas", "Pensamiento Crítico", "Creatividad", "Adaptabilidad",
    "Gestión del Tiempo", "Organización", "Liderazgo", "Atención al Detalle",
    "Servicio al Cliente", "Toma de Decisiones", "Capacidad de Análisis",
    
    # Artes y Oficios
    "Fotografía", "Edición de Video", "Diseño Gráfico", "Ilustración", "Animación",
    "Producción Musical", "Carpintería", "Soldadura", "Pintura Artística", "Cerámica",
    "Costura", "Diseño de Modas", "Artes Culinarias", "Pastelería", "Jardinería",
    
    # Transporte y Logística
    "Licencia de Conducir Profesional", "Gestión de Almacenes", "Control de Inventario",
    "Transporte Internacional", "Cadena de Suministro", "Aduanas", "Logística Inversa",
    "Planificación de Rutas", "Operación de Montacargas", "Documentación de Transporte",
    
    # Ventas
    "Técnicas de Venta", "Negociación", "Cierre de Ventas", "Gestión de Cuentas",
    "Ventas B2B", "Ventas B2C", "Telemarketing", "Desarrollo de Clientes",
    "Gestión de Cartera de Clientes", "Merchandising"
]

COMPANIES = [
    # Tecnología
    "TechSolutions Inc.", "DataWorks", "Innovate Software", "WebDev Experts", 
    "Digital Solutions", "CreativeMinds", "CloudTech", "GreenTech Innovation",
    "Smart Systems", "Quantum Software", "CodeCraft", "CyberShield Security",
    
    # Salud
    "HealthPlus", "MediCare Group", "Vital Clinic", "BienSalud", "FarmaMed",
    "NutriVida", "Clínica Regional", "Hospital Metropolitano", "Centro Médico Aurora",
    
    # Finanzas
    "FinanceWorks", "InvestGroup", "Consultoría Financiera Global", "BancaSmart",
    "Capital Partners", "Gestión & Finanzas", "Auditoría Contable S.A.", "ConsultEcon",
    
    # Educación
    "EduTech Solutions", "Instituto Avanza", "Universidad Central", "Colegio Nuevo Futuro",
    "Centro de Formación Profesional", "Escuela Internacional", "Academia de Idiomas Global",
    
    # Retail y Consumo
    "MegaStore", "Supermercados La Economía", "FashionTrends", "ElectroHogar",
    "Todo Deportes", "FarmaExpress", "Muebles & Diseño", "ComidaFácil",
    
    # Servicios
    "CleanPro Services", "TransporteRápido", "Constructora Moderna", "Inmobiliaria Horizonte",
    "HotelStar", "Restaurante Gourmet", "Turismo Aventura", "Event Planning Solutions",
    
    # Industria y Manufactura
    "IndustriaMetal", "Textiles Modernos", "AutoParts Manufacturing", "AgroIndustrias",
    "PlásticosPro", "Cerámica Industrial", "Alimentos Procesados S.A.", "EnergíaSol",
    
    # Entretenimiento y Medios
    "MediaCreative", "Productora Audiovisual", "AgenciaPubli", "EditorialContenidos",
    "EstudioArte", "RadioFusión", "CinePro", "Diseño & Comunicación"
]

LOCATIONS = [
    # Colombia
    "Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bucaramanga", 
    "Pereira", "Manizales", "Santa Marta", "Villavicencio", "Pasto", "Neiva",
    "Armenia", "Popayán", "Ibagué", "Valledupar", "Montería", "Sincelejo",
    "Tunja", "Riohacha", "Quibdó", "San Andrés",
    
    # Modalidades
    "Remoto Colombia", "Remoto Internacional", "Híbrido", "Presencial"
]

JOB_TYPES = ["full_time", "part_time", "contract", "freelance", "internship"]

REQUIREMENTS_TEMPLATES = [
    "Buscamos profesionales con experiencia en {skills} y conocimiento en {extra_skill}.",
    "Se requiere experiencia mínima de {years} años trabajando con {skills}. Valorable conocimientos en {extra_skill}.",
    "El candidato ideal debe tener sólidos conocimientos en {skills} y capacidad para {extra_skill}.",
    "Imprescindible experiencia con {skills}. Se valorará positivamente {extra_skill}.",
    "Profesional con al menos {years} años de experiencia. Conocimientos avanzados en {skills} y {extra_skill}.",
    "Buscamos personas con habilidades demostradas en {skills}. Se requiere experiencia en {extra_skill}.",
    "Para este puesto es necesario dominar {skills}. Adicionalmente, se requiere experiencia en {extra_skill}.",
    "Requerimos profesional con competencias en {skills} y con capacidad para {extra_skill}.",
    "El perfil ideal cuenta con {years} años de experiencia en el sector, con conocimientos en {skills} y {extra_skill}.",
    "Valoramos experiencia previa con {skills} y formación específica en {extra_skill}."
]

DESCRIPTIONS_TEMPLATES = [
    "Empresa líder en el sector busca incorporar {job_title} para proyecto de {duration} meses. Trabajarás en un ambiente dinámico con las últimas tecnologías.",
    "Importante empresa del sector {sector} precisa incorporar {job_title}. Ofrecemos plan de carrera y excelente ambiente laboral.",
    "Únete a nuestro equipo como {job_title}. Buscamos personas apasionadas con ganas de crecer profesionalmente en un entorno innovador.",
    "Buscamos {job_title} para incorporación inmediata. Proyecto estable con posibilidad de contrato indefinido.",
    "¿Tienes experiencia como {job_title}? ¡Esta es tu oportunidad! Empresa en expansión busca ampliar su equipo técnico.",
    "En {company} estamos buscando {job_title} para unirse a nuestro equipo. Ofrecemos horario flexible y oportunidades de desarrollo profesional.",
    "Prestigiosa compañía en el sector {sector} requiere contratar {job_title}. Valoramos la proactividad y capacidad de aprendizaje.",
    "Estamos reclutando {job_title} para nuestra sede en {location}. Te ofrecemos un entorno colaborativo y orientado a resultados.",
    "Nuestra compañía busca incorporar talento como {job_title}. Brindamos capacitación continua y beneficios competitivos.",
    "Si eres {job_title} y buscas nuevos desafíos, tenemos la oportunidad perfecta. Ambiente innovador y proyectos interesantes te esperan."
]

NAMES = [
    "Juan Pérez", "María Rodríguez", "Carlos López", "Ana García", "Luis Martínez",
    "Laura González", "Pedro Sánchez", "Sofía Torres", "Miguel Ramírez", "Valentina Castro",
    "Andrés Vargas", "Daniela Morales", "Javier Ortiz", "Camila Jiménez", "Sebastián Ruiz",
    "Isabella Suárez", "Diego Gómez", "Gabriela Díaz", "Mateo Pardo", "Victoria Herrera",
    "Santiago Ospina", "Valeria Rojas", "Alejandro Parra", "Natalia Navarro", "Felipe Duarte",
    "Carolina Méndez", "Fernando Gutiérrez", "Paula Quintero", "Ricardo Correa", "Andrea Ríos",
    "Óscar Bermúdez", "Juliana Cardona", "Mauricio Salazar", "Catalina Restrepo", "Gustavo Castaño",
    "Mariana Velásquez", "Eduardo Acosta", "Luisa Echeverri", "Gabriel Jaramillo", "Sara Zapata",
    "Cristian Cifuentes", "Angélica Henao", "Roberto Mejía", "Diana Giraldo", "Mario Garzón"
]

PROFESSIONAL_TITLES = [
    # Tecnología
    "Ingeniero de Sistemas", "Desarrollador de Software", "Analista de Datos",
    "Diseñador Web", "Especialista en Marketing Digital", "Arquitecto de Software",
    "Científico de Datos", "Ingeniero DevOps", "Programador Full Stack",
    
    # Finanzas y Administración
    "Contador", "Administrador de Empresas", "Psicólogo Organizacional",
    "Economista", "Gerente de Proyectos", "Consultor de IT", "Analista Financiero",
    "Especialista en Recursos Humanos", "Asistente Administrativo", "Auditor",
    
    # Salud
    "Médico General", "Enfermero/a", "Fisioterapeuta", "Nutricionista", 
    "Psicólogo Clínico", "Odontólogo", "Farmacéutico", "Terapeuta Ocupacional",
    
    # Educación
    "Profesor", "Docente Universitario", "Pedagogo", "Orientador Educativo",
    "Coordinador Académico", "Tutor Virtual", "Especialista en E-learning",
    
    # Marketing y Comunicación
    "Diseñador Gráfico", "Community Manager", "Content Writer", "Periodista",
    "Especialista en Relaciones Públicas", "Brand Manager", "Publicista",
    
    # Otros Sectores
    "Ingeniero Civil", "Arquitecto", "Chef Profesional", "Abogado",
    "Consultor Ambiental", "Trabajador Social", "Técnico en Logística",
    "Gerente Comercial", "Asesor de Ventas", "Piloto Comercial"
]

EDUCATION_TEMPLATES = [
    "Pregrado en {degree}, Universidad de {university}.",
    "Maestría en {degree}, Universidad {university}.",
    "{degree}, Universidad {university}. {year}",
    "Ingeniero/a {degree}, Universidad {university}. {year}",
    "Profesional en {degree}, Universidad {university}.",
    "Licenciatura en {degree}, Universidad {university}, {year}.",
    "Técnico Profesional en {degree}, Instituto {university}, {year}.",
    "Tecnólogo en {degree}, {university}, {year}.",
    "Diplomado en {degree}, Universidad {university}.",
    "Especialización en {degree}, Universidad {university}, {year}."
]

DEGREES = [
    # Tecnología
    "Ingeniería de Sistemas", "Desarrollo de Software", "Ciencias de la Computación",
    "Ingeniería Informática", "Ciencia de Datos", "Seguridad Informática",
    "Inteligencia Artificial", "Administración de Redes", "Diseño Web",
    
    # Negocios y Administración
    "Administración de Empresas", "Contaduría Pública", "Economía",
    "Finanzas", "Comercio Internacional", "Marketing", "Gestión del Talento Humano",
    "Logística y Cadena de Suministro", "Administración Pública",
    
    # Ciencias Sociales y Humanidades
    "Psicología", "Comunicación Social", "Derecho", "Sociología",
    "Trabajo Social", "Antropología", "Filosofía", "Historia", "Periodismo",
    
    # Ciencias Naturales
    "Biología", "Química", "Física", "Matemáticas", "Estadística",
    "Microbiología", "Geología", "Ciencias Ambientales", "Biotecnología",
    
    # Salud
    "Medicina", "Enfermería", "Odontología", "Fisioterapia", "Nutrición y Dietética",
    "Terapia Ocupacional", "Farmacia", "Psicología Clínica", "Veterinaria",
    
    # Ingenierías
    "Ingeniería Civil", "Ingeniería Industrial", "Ingeniería Mecánica",
    "Ingeniería Eléctrica", "Ingeniería Química", "Ingeniería Ambiental",
    "Ingeniería de Alimentos", "Ingeniería Aeronáutica", "Ingeniería Biomédica",
    
    # Artes y Diseño
    "Diseño Gráfico", "Arquitectura", "Artes Plásticas", "Diseño Industrial",
    "Música", "Teatro", "Cine y Televisión", "Diseño de Modas", "Fotografía",
    
    # Educación
    "Licenciatura en Matemáticas", "Licenciatura en Lenguas", "Pedagogía",
    "Educación Infantil", "Educación Especial", "Docencia Universitaria"
]

UNIVERSITIES = [
    # Colombia
    "Los Andes", "Nacional de Colombia", "Javeriana", "del Rosario", "EAFIT",
    "del Valle", "UPB", "Externado", "del Norte", "ICESI", "de Antioquia",
    "de La Sabana", "Universidad de Medellín", "Pontificia Bolivariana",
    "Santo Tomás", "EAN", "Sergio Arboleda", "Tecnológica de Pereira",
    "de Cartagena", "del Cauca", "de Nariño", "Surcolombiana",
    
    # Instituciones Técnicas
    "SENA", "Politécnico Grancolombiano", "Universidad Cooperativa",
    "Fundación Universitaria del Área Andina", "Institución Universitaria Politécnico",
    "ECCI", "Unitécnica", "Escuela Colombiana de Ingeniería",
    
    # Internacionales
    "Harvard", "MIT", "Stanford", "Oxford", "Cambridge", "TEC de Monterrey",
    "Universidad de Buenos Aires", "Universidad de São Paulo", "Universidad Complutense",
    "Universidad Autónoma de México", "Universidad de Chile"
]

LANGUAGES = [
    "Español (Nativo)", "Inglés (Avanzado)", "Inglés (Intermedio)", "Inglés (Básico)",
    "Francés (Avanzado)", "Francés (Intermedio)", "Francés (Básico)",
    "Portugués (Avanzado)", "Portugués (Intermedio)", "Portugués (Básico)",
    "Alemán (Avanzado)", "Alemán (Intermedio)", "Alemán (Básico)",
    "Italiano (Avanzado)", "Italiano (Intermedio)", "Italiano (Básico)",
    "Chino Mandarín (Básico)", "Japonés (Básico)", "Ruso (Básico)",
    "Coreano (Básico)", "Árabe (Básico)"
]

SECTORS = [
    "tecnología", "salud", "finanzas", "educación", "retail", "construcción",
    "manufactura", "servicios", "transporte", "alimentación", "turismo",
    "entretenimiento", "energía", "agricultura", "minería", "telecomunicaciones",
    "arte y cultura", "científico", "gubernamental", "organizaciones sin ánimo de lucro",
    "consultoría", "legal", "farmacéutico", "automotriz", "inmobiliario"
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
    """,
    
    """
    # CURRICULUM VITAE
    
    ## DATOS PERSONALES
    Nombre: {full_name}
    Título Profesional: {professional_title}
    
    ## PERFIL
    {profile_summary}
    
    ## EXPERIENCIA LABORAL
    
    ### {company1} ({start_date1} - {end_date1})
    Cargo: {job_title1}
    Funciones:
    - {responsibility1}
    - {responsibility2}
    - {responsibility3}
    
    ### {company2} ({start_date2} - {end_date2})
    Cargo: {job_title2}
    Funciones:
    - {responsibility4}
    - {responsibility5}
    
    ## FORMACIÓN ACADÉMICA
    {education}
    
    ## COMPETENCIAS
    {skills}
    
    ## IDIOMAS
    {languages}
    
    ## REFERENCIAS
    Disponibles a solicitud
    """
]

RESPONSIBILITIES = [
    # Tecnología
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
    
    # Administración
    "Coordinación de equipos de trabajo",
    "Gestión de presupuestos y recursos financieros",
    "Planificación estratégica y establecimiento de objetivos",
    "Elaboración y presentación de informes gerenciales",
    "Supervisión y evaluación del desempeño del personal",
    "Administración de proyectos siguiendo metodologías ágiles",
    "Optimización de procesos administrativos y operativos",
    "Gestión de contratos y proveedores",
    "Implementación de políticas y procedimientos organizacionales",
    
    # Marketing y Comunicación
    "Desarrollo de estrategias de marketing",
    "Gestión de campañas publicitarias",
    "Creación y curación de contenido para redes sociales",
    "Diseño y ejecución de planes de comunicación",
    "Análisis de métricas y KPIs de marketing",
    "Organización de eventos corporativos",
    "Gestión de la identidad y reputación de marca",
    "Implementación de estrategias SEO/SEM",
    "Investigación de mercado y análisis de la competencia",
    
    # Recursos Humanos
    "Reclutamiento y selección de personal",
    "Diseño e implementación de programas de formación",
    "Gestión del desarrollo profesional de los empleados",
    "Administración de compensaciones y beneficios",
    "Resolución de conflictos laborales",
    "Implementación de políticas de diversidad e inclusión",
    "Gestión del clima laboral y cultura organizacional",
    "Administración de procesos de evaluación del desempeño",
    
    # Atención al Cliente
    "Atención y soporte al cliente",
    "Resolución de quejas y reclamaciones",
    "Seguimiento a la satisfacción del cliente",
    "Gestión de la cartera de clientes",
    "Capacitación a usuarios en el uso de productos/servicios",
    "Implementación de mejoras en la experiencia del cliente",
    
    # Ventas
    "Prospección y captación de nuevos clientes",
    "Negociación y cierre de ventas",
    "Elaboración de propuestas comerciales",
    "Seguimiento y fidelización de clientes",
    "Análisis del mercado y la competencia",
    "Cumplimiento de objetivos y cuotas de ventas",
    
    # Educación
    "Impartición de clases y talleres formativos",
    "Diseño y actualización de contenidos pedagógicos",
    "Evaluación y seguimiento del progreso de los estudiantes",
    "Coordinación con otros docentes y departamentos",
    "Atención a las necesidades individuales de aprendizaje",
    "Desarrollo de material didáctico innovador",
    
    # Salud
    "Diagnóstico y tratamiento de pacientes",
    "Elaboración de historias clínicas y seguimiento",
    "Coordinación con especialistas y otros profesionales de la salud",
    "Educación a pacientes sobre cuidados y prevención",
    "Participación en programas de salud pública",
    "Realización de procedimientos clínicos especializados",
    
    # Producción y Manufactura
    "Control de calidad en procesos productivos",
    "Supervisión de líneas de producción",
    "Gestión del inventario y almacén",
    "Implementación de mejoras en eficiencia productiva",
    "Mantenimiento preventivo de equipos",
    "Cumplimiento de normativas de seguridad industrial",
    
    # Logística
    "Coordinación de operaciones logísticas",
    "Gestión de rutas de distribución",
    "Optimización de la cadena de suministro",
    "Control de inventarios y gestión de almacenes",
    "Negociación con proveedores logísticos",
    "Seguimiento y trazabilidad de envíos"
]

PROFILE_SUMMARIES = [
    "Profesional con {years} años de experiencia en {field}. Especialista en {skill1} y {skill2}.",
    "Especialista en {field} con sólidos conocimientos en {skill1}, {skill2} y {skill3}.",
    "{job_title} con {years} años de experiencia en desarrollo de proyectos de {field}.",
    "Profesional apasionado por {field} con experiencia en {skill1} y {skill2}.",
    "Experto en {field} con enfoque en {skill1} y {skill2}. {years} años de experiencia.",
    "Profesional comprometido con {years} años de trayectoria en el sector de {field}, con especialización en {skill1}.",
    "{job_title} con experiencia liderando equipos y proyectos en el área de {field}, con habilidades en {skill1} y {skill2}.",
    "Especialista certificado en {skill1} y {skill2}, con amplia experiencia en proyectos de {field}.",
    "Profesional proactivo con formación en {field} y {years} años de experiencia aplicando {skill1} y {skill2}.",
    "Graduado en {field} con especialización en {skill1}. Experiencia demostrable en {skill2} y {skill3}."
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
    
    # Almacenar los nombres de usuario ya utilizados
    used_usernames = set()
    # Almacenar las compañías ya creadas
    used_companies = set()
    
    for i in range(num_employers):
        # Seleccionar una compañía que no esté ya utilizada
        while True:
            company_name = random.choice(COMPANIES)
            if company_name not in used_companies:
                used_companies.add(company_name)
                break
                
        # Generar un nombre de usuario base
        base_username = f"employer_{company_name.lower().replace(' ', '_')}"
        username = f"{base_username}_{i}"
        
        # Asegurarse de que el nombre de usuario sea único
        while User.objects.filter(username=username).exists() or username in used_usernames:
            # Generar un sufijo aleatorio
            random_suffix = get_random_string(5)
            username = f"{base_username}_{random_suffix}"
        
        # Registrar el nombre de usuario como utilizado
        used_usernames.add(username)
        
        try:
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
            
        except Exception as e:
            print(f"Error al crear empleador {company_name}: {str(e)}")
    
    return employers

def create_job_seekers(num_seekers=30):
    """Crea buscadores de empleo de muestra"""
    print(f"Creando {num_seekers} buscadores de empleo...")
    job_seekers = []
    
    # Lista para almacenar nombres de usuario ya utilizados
    used_usernames = set()
    
    for i in range(num_seekers):
        full_name = random.choice(NAMES)
        
        # Generar un nombre de usuario único
        base_username = f"jobseeker_{full_name.lower().replace(' ', '_')}"
        username = f"{base_username}_{i}"
        
        # Asegurarse de que el nombre de usuario sea único
        while User.objects.filter(username=username).exists() or username in used_usernames:
            # Agregar un string aleatorio al nombre de usuario para hacerlo único
            random_suffix = get_random_string(5)
            username = f"{base_username}_{random_suffix}"
        
        # Registrar el nombre de usuario como utilizado
        used_usernames.add(username)
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123"
        )
        
        # Seleccionar habilidades aleatorias según perfil profesional
        professional_title = random.choice(PROFESSIONAL_TITLES)
        
        # Determinar categoría profesional para seleccionar habilidades relevantes
        if any(tech in professional_title.lower() for tech in ["ingeniero", "desarrollador", "programador", "datos", "software"]):
            skill_pool = [s for s in SKILLS if s in ["Python", "Java", "JavaScript", "HTML", "CSS", "Django", "React", "Angular", 
                "Node.js", "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "Git", "C++", "Machine Learning"]] + random.sample(SKILLS, 15)
        elif any(health in professional_title.lower() for health in ["médico", "enfermero", "fisio", "odontólogo", "psicólogo", "salud"]):
            skill_pool = [s for s in SKILLS if s in ["Primeros Auxilios", "Flebotomía", "Cuidado del Paciente", "ECG", "Anatomía",
                "Farmacología", "Fisioterapia", "Psicoterapia", "Diagnóstico Clínico", "Nutrición"]] + random.sample(SKILLS, 15)
        elif any(business in professional_title.lower() for business in ["contador", "administrador", "economista", "financiero", "recursos humanos"]):
            skill_pool = [s for s in SKILLS if s in ["Excel Avanzado", "SAP", "Contabilidad", "Análisis Financiero", "Inversiones",
                "Gestión de Proyectos", "Presupuestos", "ERP", "CRM", "Nóminas"]] + random.sample(SKILLS, 15)
        elif any(marketing in professional_title.lower() for marketing in ["marketing", "diseñador", "community", "publicista"]):
            skill_pool = [s for s in SKILLS if s in ["Marketing Digital", "SEO", "SEM", "Google Analytics", "Facebook Ads",
                "Content Marketing", "Adobe Photoshop", "Adobe Illustrator", "Canva", "Copywriting"]] + random.sample(SKILLS, 15)
        else:
            skill_pool = random.sample(SKILLS, 25)
        
        # Seleccionar habilidades aleatorias
        skills = random.sample(skill_pool, random.randint(5, 10))
        
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
            professional_title=professional_title,
            date_of_birth=generate_random_date(start_years_ago=40, end_years_ago=20),
            phone_number=f"+57 3{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
            location=random.choice(LOCATIONS),
            bio=f"Profesional con experiencia en {', '.join(skills[:2])}. Interesado en {random.choice(['desarrollo profesional', 'nuevos desafíos', 'proyectos innovadores', 'crecimiento laboral', 'aportar valor a organizaciones'])}.",
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
        print(f"  Creado buscador: {full_name} - {professional_title}")
    
    return job_seekers

def create_cv_for_job_seeker(job_seeker, skills):
    """Crea un CV para un buscador de empleo"""
    # Generar texto del CV
    company1 = random.choice(COMPANIES)
    company2 = random.choice(COMPANIES)
    job_title1 = random.choice(JOB_TITLES)
    job_title2 = random.choice(JOB_TITLES)
    
    # Obtener los años de experiencia del job seeker (o usar 5 como valor predeterminado)
    total_exp_years = job_seeker.years_experience or 5
    
    # Fechas de experiencia - Asegurar rangos válidos
    # Primera experiencia laboral (más antigua)
    first_job_years = min(total_exp_years // 2, 5)  # Mitad de la experiencia total, máximo 5 años
    first_job_end_years_ago = max(2, total_exp_years - first_job_years)
    first_job_start_years_ago = first_job_end_years_ago + first_job_years
    
    # Segunda experiencia laboral (más reciente)
    second_job_start_years_ago = min(first_job_end_years_ago - 0.5, 3)  # Empieza poco después de terminar el primer trabajo
    
    # Generar fechas asegurando que los rangos sean válidos
    try:
        first_job_start = datetime.now() - timedelta(days=int(365 * first_job_start_years_ago))
        first_job_end = datetime.now() - timedelta(days=int(365 * first_job_end_years_ago))
        second_job_start = datetime.now() - timedelta(days=int(365 * second_job_start_years_ago))
        
        # Formatear fechas
        start_date1 = first_job_start.strftime("%b %Y")
        end_date1 = first_job_end.strftime("%b %Y")
        start_date2 = second_job_start.strftime("%b %Y")
        end_date2 = "Presente"
    except Exception as e:
        # En caso de error con las fechas, usar fechas genéricas
        print(f"Error generando fechas para CV: {str(e)}")
        start_date1 = "Ene 2018"
        end_date1 = "Dic 2020"
        start_date2 = "Feb 2021"
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
        years=job_seeker.years_experience or random.randint(1, 8),
        field=random.choice(["tecnología", "desarrollo web", "análisis de datos", "marketing digital"]),
        job_title=job_seeker.professional_title or "Profesional",
        skill1=skills[0] if skills else "habilidades técnicas",
        skill2=skills[1] if len(skills) > 1 else "competencias profesionales",
        skill3=skills[2] if len(skills) > 2 else "trabajo en equipo"
    )
    
    # Preparar todos los valores posibles para el formato
    format_values = {
        # Datos básicos del CV
        'company1': company1,
        'company2': company2,
        'job_title1': job_title1,
        'job_title2': job_title2,
        'start_date1': start_date1,
        'end_date1': end_date1,
        'start_date2': start_date2,
        'end_date2': end_date2,
        
        # Responsabilidades
        'responsibility1': responsibilities[0],
        'responsibility2': responsibilities[1],
        'responsibility3': responsibilities[2],
        'responsibility4': responsibilities[3],
        'responsibility5': responsibilities[4],
        'responsibility6': responsibilities[5],
        
        # Información del perfil
        'full_name': job_seeker.full_name or f"Candidato {job_seeker.id}",
        'professional_title': job_seeker.professional_title or "Profesional",
        'education': job_seeker.education or "Educación universitaria",
        'skills': job_seeker.skills or ", ".join(skills),
        'languages': job_seeker.languages or "Español (Nativo), Inglés (Intermedio)",
        'profile_summary': profile_summary,
        'location': job_seeker.location or "Ciudad",
        'phone_number': job_seeker.phone_number or "+57 123 456 7890",
        'email': job_seeker.user.email,
        'years_experience': job_seeker.years_experience or 3,
        
        # Otros campos que podrían usarse en las plantillas
        'date_of_birth': job_seeker.date_of_birth.strftime("%d/%m/%Y") if job_seeker.date_of_birth else "01/01/1990",
        'bio': job_seeker.bio or "Profesional con experiencia en el sector",
    }
    
    # Generar texto del CV usando una plantilla
    try:
        cv_text = random.choice(CV_TEMPLATES).format(**format_values)
    except KeyError as e:
        # Si falta alguna clave, imprimir el error y usar una plantilla simplificada
        print(f"Error al formatear plantilla de CV: Falta la clave {e}")
        cv_text = f"""
        # CV de {format_values['full_name']}
        
        ## Información Personal
        - Nombre: {format_values['full_name']}
        - Título Profesional: {format_values['professional_title']}
        - Email: {format_values['email']}
        - Teléfono: {format_values['phone_number']}
        
        ## Experiencia Laboral
        
        ### {format_values['company1']}
        {format_values['job_title1']} | {format_values['start_date1']} - {format_values['end_date1']}
        
        - {format_values['responsibility1']}
        - {format_values['responsibility2']}
        
        ### {format_values['company2']}
        {format_values['job_title2']} | {format_values['start_date2']} - {format_values['end_date2']}
        
        - {format_values['responsibility3']}
        - {format_values['responsibility4']}
        
        ## Educación
        {format_values['education']}
        
        ## Habilidades
        {format_values['skills']}
        
        ## Idiomas
        {format_values['languages']}
        """
    
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
    
def create_job_offers(employers, num_offers=80):
    """Crea ofertas de trabajo de muestra"""
    print(f"Creando {num_offers} ofertas de trabajo...")
    job_offers = []
    
    for i in range(num_offers):
        # Seleccionar empleador aleatorio
        employer = random.choice(employers)
        
        # Seleccionar título aleatorio para el sector del empleador
        sector = employer.industry
        
        if "tecnología" in sector.lower() or "software" in sector.lower() or "it" in sector.lower():
            title_pool = [j for j in JOB_TITLES if any(tech in j.lower() for tech in ["desarrollador", "ingeniero", "programador", "software", "datos"])]
        elif "salud" in sector.lower() or "médico" in sector.lower():
            title_pool = [j for j in JOB_TITLES if any(health in j.lower() for health in ["médico", "enfermero", "fisio", "salud", "clínico"])]
        elif "finanzas" in sector.lower() or "contable" in sector.lower():
            title_pool = [j for j in JOB_TITLES if any(finance in j.lower() for finance in ["financiero", "contador", "auditor", "economista"])]
        elif "educación" in sector.lower() or "académico" in sector.lower():
            title_pool = [j for j in JOB_TITLES if any(edu in j.lower() for edu in ["profesor", "docente", "tutor", "educación"])]
        else:
            title_pool = JOB_TITLES
        
        if not title_pool:
            title_pool = JOB_TITLES
            
        title = random.choice(title_pool)
        
        # Seleccionar habilidades aleatorias para requisitos
        if "desarrollador" in title.lower() or "ingeniero" in title.lower() or "programador" in title.lower():
            skill_pool = [s for s in SKILLS if s in ["Python", "Java", "JavaScript", "HTML", "CSS", "Django", "React", "Angular", 
                "Node.js", "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "Git", "C++", "Machine Learning"]]
        elif "médico" in title.lower() or "enfermero" in title.lower() or "fisio" in title.lower():
            skill_pool = [s for s in SKILLS if s in ["Primeros Auxilios", "Flebotomía", "Cuidado del Paciente", "ECG", "Anatomía",
                "Farmacología", "Fisioterapia", "Psicoterapia", "Diagnóstico Clínico", "Nutrición"]]
        elif "marketing" in title.lower() or "diseñador" in title.lower():
            skill_pool = [s for s in SKILLS if s in ["Marketing Digital", "SEO", "SEM", "Google Analytics", "Facebook Ads",
                "Content Marketing", "Adobe Photoshop", "Adobe Illustrator", "Canva", "Copywriting"]]
        else:
            skill_pool = SKILLS
        
        if len(skill_pool) < 10:
            skill_pool.extend(random.sample(SKILLS, 10))
        
        required_skills = random.sample(skill_pool, random.randint(3, 7))
        
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
            sector=sector,
            company=employer.company_name,
            location=random.choice(LOCATIONS)
        )
        
        # Fecha de expiración (entre 15 y 60 días en el futuro)
        expires_at = datetime.now() + timedelta(days=random.randint(15, 60))
        
        # Decidir si la oferta es remota
        is_remote = "remoto" in title.lower() or random.random() < 0.3
        
        # Generar rango salarial
        min_salary = random.randint(1, 5) * 1000000
        max_salary = min_salary + random.randint(1, 5) * 500000
        salary_range = f"${min_salary/1000000:.1f} - ${max_salary/1000000:.1f} millones"
        
        # Crear oferta de trabajo
        job_offer = JobOffer.objects.create(
            title=title,
            company=employer.company_name,
            location=employer.company_location,
            description=description,
            requirements=requirements,
            required_skills=", ".join(required_skills),
            salary_range=salary_range,
            job_type=random.choice(JOB_TYPES),
            remote=is_remote,
            expires_at=expires_at,
            active=True
        )
        
        job_offers.append(job_offer)
        print(f"  Creada oferta: {title} - {employer.company_name}")
    
    return job_offers

def create_applications(job_seekers, job_offers, num_applications=150):
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
    
    # Asegurarse de que no excedemos el número solicitado
    pairs = pairs[:num_applications]
    
    applications = []
    for seeker, offer in pairs:
        # Definir motivación aleatoria
        motivations = [
            f"interés en {offer.company}",
            f"desarrollo profesional en el sector de {seeker.professional_title}",
            f"aplicar mis habilidades en {', '.join(seeker.skills.split(', ')[:2]) if seeker.skills else 'el área'}",
            "nuevos retos profesionales",
            f"crecimiento laboral en {offer.location}",
            "trabajo en un ambiente innovador"
        ]
        
        motivation = random.choice(motivations)
        
        # Generar carta de presentación
        cover_letter = f"""
        Estimado/a Responsable de Selección de {offer.company},
        
        Me dirijo a ustedes con interés en la posición de {offer.title} que he visto publicada en KeyWork. 
        Considero que mi experiencia en {', '.join(random.sample(seeker.skills.split(', '), min(2, len(seeker.skills.split(', ')))))} 
        y mis {seeker.years_experience or 'varios'} años de experiencia me convierten en un buen candidato para esta posición.
        
        Me entusiasma especialmente la oportunidad de {motivation}.
        
        {random.choice([
            f"Mi experiencia trabajando con {random.choice(seeker.skills.split(', ')) if seeker.skills else 'diversas tecnologías'} se alinea perfectamente con sus requisitos.",
            f"Considero que mi formación en {seeker.education if seeker.education else 'mi campo'} me ha preparado para asumir este desafío.",
            f"En mi experiencia previa, he demostrado habilidades para {random.choice(['resolver problemas complejos', 'trabajar en equipo', 'adaptarme a entornos cambiantes', 'aprender nuevas tecnologías'])}, lo cual sería valioso para este puesto."
        ])}
        
        Quedo a su disposición para ampliar cualquier información que consideren necesaria.
        
        Saludos cordiales,
        {seeker.full_name}
        """
        
        # Decidir el estado de la aplicación (con proporción realista)
        status_weights = [
            ('applied', 0.4),      # 40% en estado inicial
            ('in_review', 0.3),    # 30% en revisión
            ('interview', 0.15),   # 15% en entrevista
            ('rejected', 0.1),     # 10% rechazadas
            ('accepted', 0.05)     # 5% aceptadas
        ]
        
        status = random.choices([s[0] for s in status_weights], 
                              weights=[s[1] for s in status_weights], 
                              k=1)[0]
        
        # Fecha de aplicación (entre 1 y 15 días atrás)
        applied_at = datetime.now() - timedelta(days=random.randint(1, 15))
        
        # Crear aplicación
        application = JobApplication.objects.create(
            job_seeker=seeker,
            job_offer=offer,
            cover_letter=cover_letter,
            status=status,
            applied_at=applied_at
        )
        
        applications.append(application)
        print(f"  Creada aplicación: {seeker.full_name} → {offer.title} ({status})")
    
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
    try:
        print("Creando empleadores...")
        employers = create_employers(15)
        
        print("Creando buscadores de empleo...")
        job_seekers = create_job_seekers(50)
        
        print("Creando ofertas de trabajo...")
        job_offers = create_job_offers(employers, 80)
        
        print("Creando aplicaciones...")
        applications = create_applications(job_seekers, job_offers, 150)
        
        print("\nPoblación de la base de datos completada con éxito.")
        print(f"  Empleadores creados: {len(employers)}")
        print(f"  Buscadores de empleo creados: {len(job_seekers)}")
        print(f"  Ofertas de trabajo creadas: {len(job_offers)}")
        print(f"  Aplicaciones creadas: {len(applications)}")
    
    except Exception as e:
        import traceback
        print(f"Error durante la población de la base de datos: {str(e)}")
        traceback.print_exc()
        
if __name__ == "__main__":
    run()