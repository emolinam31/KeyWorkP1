from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from .forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm
from .models import UserProfile

def signupaccount(request):
    if request.method == 'GET':
        return render(request, 'user_management/signup.html', {'form': CustomUserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                form = CustomUserCreationForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    login(request, user)
                    
                    # Redirigir a la página correspondiente según el tipo de usuario
                    if user.profile.user_type == 'employer':
                        messages.success(request, '¡Cuenta creada exitosamente! Complete su perfil de empleador.')
                        return redirect('complete_employer_profile')
                    else:
                        messages.success(request, '¡Cuenta creada exitosamente! Complete su perfil de buscador de empleo.')
                        return redirect('complete_jobseeker_profile')
                else:
                    return render(request, 'user_management/signup.html', {
                        'form': form,
                        'error': 'Por favor corrija los errores en el formulario.'
                    })
            except IntegrityError:
                return render(request, 'user_management/signup.html', {
                    'form': CustomUserCreationForm(),
                    'error': 'El nombre de usuario ya está en uso. Por favor elija otro.'
                })
        else:
            return render(request, 'user_management/signup.html', {
                'form': CustomUserCreationForm(),
                'error': 'Las contraseñas no coinciden.'
            })

def loginaccount(request):
    if request.method == 'GET':
        return render(request, 'user_management/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, 
                            username=request.POST['username'], 
                            password=request.POST['password'])
        
        if user is None:
            return render(request, 'user_management/login.html', {
                'form': AuthenticationForm(),
                'error': 'El nombre de usuario y la contraseña no coinciden.'
            })
        else:
            login(request, user)
            # Redirigir según el tipo de usuario
            try:
                if user.profile.user_type == 'employer':
                    return redirect('employer_portal')
                else:
                    return redirect('home')  # Cambiar a jobseeker_portal cuando esté disponible
            except UserProfile.DoesNotExist:
                # Si el usuario no tiene perfil, redirigir a la página de inicio
                return redirect('home')

def logoutaccount(request):
    logout(request)
    return redirect('home')

@login_required
def complete_employer_profile(request):
    # Verificar que el usuario sea de tipo empleador
    try:
        if request.user.profile.user_type != 'employer':
            messages.error(request, 'No tiene permisos para acceder a esta página.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'No tiene un perfil configurado.')
        return redirect('home')
    
    if request.method == 'GET':
        form = EmployerProfileForm(instance=request.user.profile)
        return render(request, 'user_management/complete_employer_profile.html', {'form': form})
    else:
        form = EmployerProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('employer_portal')
        else:
            return render(request, 'user_management/complete_employer_profile.html', {'form': form})

@login_required
def complete_jobseeker_profile(request):
    # Verificar que el usuario sea de tipo buscador de empleo
    try:
        if request.user.profile.user_type != 'jobseeker':
            messages.error(request, 'No tiene permisos para acceder a esta página.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'No tiene un perfil configurado.')
        return redirect('home')
    
    if request.method == 'GET':
        form = JobSeekerProfileForm(instance=request.user.profile)
        return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})
    else:
        try:
            form = JobSeekerProfileForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                profile = form.save(commit=False)
                
                # Si el perfil tiene un CV asignado, podemos extraer algunas habilidades
                if profile.cv and profile.cv.extracted_text and not profile.skills:
                    # Aquí podrías implementar una lógica para extraer habilidades del texto del CV
                    # Por ejemplo, buscar palabras clave comunes
                    # Este es solo un ejemplo básico
                    common_skills = ["python", "java", "javascript", "html", "css", 
                                    "django", "react", "angular", "node.js", "sql",
                                    "marketing", "ventas", "comunicación", "liderazgo"]
                    extracted_text = profile.cv.extracted_text.lower()
                    detected_skills = []
                    
                    for skill in common_skills:
                        if skill in extracted_text:
                            detected_skills.append(skill.capitalize())
                    
                    if detected_skills:
                        profile.skills = ", ".join(detected_skills)
                
                profile.save()
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('home')  # Cambiar a jobseeker_portal cuando esté disponible
            else:
                return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})
        except Exception as e:
            messages.error(request, f'Error al guardar el perfil: {str(e)}')
            return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'user_management/profile.html')