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


class JobSeekerProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
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
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.TextInput(attrs={'placeholder': 'Ejemplo: Python, Django, SQL, Marketing Digital'}),
            'education': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ejemplo: Licenciatura en Sistemas, Universidad Nacional (2018-2022)'}),
            'languages': forms.TextInput(attrs={'placeholder': 'Ejemplo: Español (Nativo), Inglés (Avanzado), Francés (Básico)'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar los CVs disponibles
        self.fields['cv'].queryset = CV.objects.all()
        self.fields['cv'].required = False