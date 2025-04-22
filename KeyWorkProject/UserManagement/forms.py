from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import JobSeekerProfile, EmployerProfile

class CustomUserCreationForm(UserCreationForm):
    USER_TYPES = (
        ('employer', 'Empleador - Quiero publicar vacantes'),
        ('jobseeker', 'Candidato - Quiero encontrar trabajo'),
    )
    
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        required=True,
        widget=forms.RadioSelect(),
        label='¿Cómo usarás KeyWork?'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')

class JobSeekerProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Fecha de nacimiento'
    )
    
    class Meta:
        model = JobSeekerProfile
        fields = (
            'full_name', 
            'professional_title', 
            'years_experience',
            'date_of_birth',
            'phone_number',
            'location',
            'bio',
            'skills',
            'education',
            'languages',
            'availability',
            'desired_salary',
            'remote_work',
        )
        labels = {
            'full_name': 'Nombre completo',
            'professional_title': 'Título profesional',
            'years_experience': 'Años de experiencia',
            'phone_number': 'Número de teléfono',
            'location': 'Ubicación',
            'bio': 'Biografía',
            'skills': 'Habilidades',
            'education': 'Educación',
            'languages': 'Idiomas',
            'availability': 'Disponibilidad',
            'desired_salary': 'Salario deseado',
            'remote_work': 'Disponible para trabajo remoto',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_title': forms.TextInput(attrs={'class': 'form-control'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ejemplo: Python, Django, SQL, Marketing Digital'}),
            'education': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Ejemplo: Licenciatura en Sistemas, Universidad Nacional (2018-2022)'}),
            'languages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ejemplo: Español (Nativo), Inglés (Avanzado), Francés (Básico)'}),
            'availability': forms.Select(attrs={'class': 'form-control'}),
            'desired_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '100000', 'placeholder': '2000000'}),
            'remote_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'industry', 'company_size', 'company_website', 'company_description', 'company_location')
        labels = {
            'company_name': 'Nombre de la empresa',
            'industry': 'Industria',
            'company_size': 'Tamaño de la empresa',
            'company_website': 'Sitio web',
            'company_description': 'Descripción',
            'company_location': 'Ubicación'
        }
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tecnología, Salud, Educación'}),
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.ejemplo.com'}),
            'company_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'company_location': forms.TextInput(attrs={'class': 'form-control'}),
        }