from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from CollectionPoint.models import CV

class CustomUserCreationForm(UserCreationForm):
    USER_TYPES = (
        ('employer', 'Empleador - Quiero publicar vacantes'),
        ('jobseeker', 'Buscador de Empleo - Quiero encontrar trabajo'),
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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            user_type = self.cleaned_data.get('user_type')
            UserProfile.objects.create(
                user=user,
                user_type=user_type
            )
        return user


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('company_name', 'industry', 'company_size')
        labels = {
            'company_name': 'Nombre de la empresa',
            'industry': 'Industria',
            'company_size': 'Tamaño de la empresa'
        }
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tecnología, Salud, Educación'}),
            'company_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1-10, 11-50, 51-200'})
        }
        
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name:
            raise forms.ValidationError("Por favor, ingrese el nombre de su empresa.")
        return company_name


class JobSeekerProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Fecha de nacimiento'
    )
    
    class Meta:
        model = UserProfile
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
            'cv'
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
            'cv': 'Seleccionar CV subido'
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
            'cv': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar los CVs disponibles
        # En una versión más avanzada, deberías filtrar solo los CVs del usuario actual
        all_cvs = CV.objects.all()
        self.fields['cv'].queryset = all_cvs
        self.fields['cv'].required = False
        
        # Añadir logging para debugging
        import sys
        print(f"CVs disponibles para selección: {list(all_cvs.values_list('id', 'upload_type'))}", file=sys.stderr)
        
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name:
            raise forms.ValidationError("Por favor, ingrese su nombre completo.")
        return full_name