from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.contrib import messages
from .forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm
from .models import UserProfile
from CollectionPoint.models import CV
import traceback

def signupaccount(request):
    if request.method == 'GET':
        return render(request, 'user_management/signup.html', {'form': CustomUserCreationForm()})
    else:
        print("Procesando solicitud de registro POST")
        if request.POST['password1'] == request.POST['password2']:
            try:
                form = CustomUserCreationForm(request.POST)
                if form.is_valid():
                    print(f"Formulario válido. Tipo de usuario: {form.cleaned_data.get('user_type')}")
                    user = form.save()
                    login(request, user)
                    
                    # Redirigir a la página correspondiente según el tipo de usuario
                    if user.profile.user_type == 'employer':
                        print(f"Usuario {user.username} registrado como employer")
                        messages.success(request, '¡Cuenta creada exitosamente! Complete su perfil de empleador.')
                        return redirect('complete_employer_profile')
                    else:
                        print(f"Usuario {user.username} registrado como jobseeker")
                        messages.success(request, '¡Cuenta creada exitosamente! Complete su perfil de buscador de empleo.')
                        return redirect('complete_jobseeker_profile')
                else:
                    print(f"Errores en el formulario: {form.errors}")
                    return render(request, 'user_management/signup.html', {
                        'form': form,
                        'error': 'Por favor corrija los errores en el formulario.'
                    })
            except IntegrityError as e:
                print(f"Error de integridad: {str(e)}")
                return render(request, 'user_management/signup.html', {
                    'form': CustomUserCreationForm(),
                    'error': 'El nombre de usuario ya está en uso. Por favor elija otro.'
                })
            except Exception as e:
                print(f"Error inesperado en registro: {str(e)}")
                print(traceback.format_exc())
                return render(request, 'user_management/signup.html', {
                    'form': CustomUserCreationForm(),
                    'error': f'Error inesperado: {str(e)}'
                })
        else:
            print("Las contraseñas no coinciden")
            return render(request, 'user_management/signup.html', {
                'form': CustomUserCreationForm(),
                'error': 'Las contraseñas no coinciden.'
            })

def loginaccount(request):
    if request.method == 'GET':
        return render(request, 'user_management/login.html', {'form': AuthenticationForm()})
    else:
        print("Procesando solicitud de login POST")
        user = authenticate(request, 
                        username=request.POST['username'], 
                        password=request.POST['password'])
    
        if user is None:
            print(f"Autenticación fallida para usuario: {request.POST['username']}")
            return render(request, 'user_management/login.html', {
                'form': AuthenticationForm(),
                'error': 'El nombre de usuario y la contraseña no coinciden.'
            })
        else:
            login(request, user)
            print(f"Usuario {user.username} autenticado correctamente")
            # Redirigir según el tipo de usuario
            try:
                if user.profile.user_type == 'employer':
                    print(f"Redirigiendo a employer_portal")
                    return redirect('employer_portal')
                else:
                    print(f"Redirigiendo a home")
                    return redirect('home')  # Cambiar a jobseeker_portal cuando esté disponible
            except UserProfile.DoesNotExist:
                print(f"El usuario {user.username} no tiene perfil")
                # Si el usuario no tiene perfil, redirigir a la página de inicio
                return redirect('home')

def logoutaccount(request):
    username = request.user.username if request.user.is_authenticated else "Usuario anónimo"
    print(f"Cerrando sesión para {username}")
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('home')

@login_required
def complete_employer_profile(request):
    # Verificar que el usuario sea de tipo empleador
    try:
        if request.user.profile.user_type != 'employer':
            print(f"Usuario {request.user.username} intentó acceder a perfil de empleador siendo {request.user.profile.user_type}")
            messages.error(request, 'No tiene permisos para acceder a esta página.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        print(f"Usuario {request.user.username} no tiene perfil configurado")
        messages.error(request, 'No tiene un perfil configurado.')
        return redirect('home')
    
    if request.method == 'GET':
        form = EmployerProfileForm(instance=request.user.profile)
        return render(request, 'user_management/complete_employer_profile.html', {'form': form})
    else:
        try:
            print(f"Procesando solicitud POST para completar perfil de empleador para {request.user.username}")
            form = EmployerProfileForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                print(f"Formulario válido, guardando perfil")
                form.save()
                print(f"Perfil de empleador guardado correctamente")
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('employer_portal')
            else:
                print(f"Formulario inválido. Errores: {form.errors}")
                return render(request, 'user_management/complete_employer_profile.html', {'form': form})
        except Exception as e:
            print(f"Error al guardar el perfil de empleador: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error al guardar el perfil: {str(e)}')
            return render(request, 'user_management/complete_employer_profile.html', {'form': form})

@login_required
def complete_jobseeker_profile(request):
    # Verificar que el usuario sea de tipo buscador de empleo
    try:
        if request.user.profile.user_type != 'jobseeker':
            print(f"Usuario {request.user.username} intentó acceder a perfil de jobseeker siendo {request.user.profile.user_type}")
            messages.error(request, 'No tiene permisos para acceder a esta página.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        print(f"Usuario {request.user.username} no tiene perfil configurado")
        messages.error(request, 'No tiene un perfil configurado.')
        return redirect('home')
    
    if request.method == 'GET':
        # Obtener los CVs subidos por el usuario para mostrarlos en el formulario
        user_cvs = CV.objects.all()  # Temporalmente mostramos todos los CVs
        print(f"CVs disponibles: {list(user_cvs.values_list('id', 'upload_type'))}")
        
        # Inicializar el formulario con el perfil del usuario
        form = JobSeekerProfileForm(instance=request.user.profile)
        
        # Si no hay CVs disponibles, mostrar un mensaje
        if not user_cvs.exists():
            messages.info(request, 'No tiene CVs subidos. Puede subir uno desde la opción "Subir CV".')
        
        return render(request, 'user_management/complete_jobseeker_profile.html', {
            'form': form,
            'user_cvs': user_cvs
        })
    else:
        try:
            print(f"Procesando solicitud POST para completar perfil de jobseeker para {request.user.username}")
            form = JobSeekerProfileForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                print(f"Formulario válido, guardando perfil")
                profile = form.save(commit=False)
                
                # Verificar si se seleccionó un CV
                cv_id = request.POST.get('cv')
                if cv_id:
                    try:
                        profile.cv = CV.objects.get(id=cv_id)
                        print(f"CV seleccionado y asignado: {profile.cv}")
                    except CV.DoesNotExist:
                        print(f"No se encontró el CV con ID {cv_id}")
                        messages.warning(request, f'No se encontró el CV seleccionado.')
                
                # Si el perfil tiene un CV asignado, podemos extraer algunas habilidades
                if profile.cv and profile.cv.extracted_text and not profile.skills:
                    print("Extrayendo habilidades del texto del CV")
                    # Este es solo un ejemplo básico de extracción de habilidades
                    common_skills = [
                        "python", "java", "javascript", "html", "css", "django", "react", 
                        "angular", "node.js", "sql", "marketing", "ventas", "comunicación", 
                        "liderazgo", "excel", "word", "powerpoint", "análisis", "diseño"
                    ]
                    extracted_text = profile.cv.extracted_text.lower()
                    detected_skills = []
                    
                    for skill in common_skills:
                        if skill in extracted_text:
                            detected_skills.append(skill.capitalize())
                    
                    if detected_skills:
                        profile.skills = ", ".join(detected_skills)
                        print(f"Habilidades detectadas: {profile.skills}")
                        messages.info(request, f'Se detectaron automáticamente {len(detected_skills)} habilidades de su CV.')
                
                profile.save()
                print("Perfil guardado correctamente")
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('profile')
            else:
                print(f"Formulario inválido. Errores: {form.errors}")
                return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})
        except Exception as e:
            print(f"Error al guardar el perfil de jobseeker: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error al guardar el perfil: {str(e)}')
            return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})

@login_required
def profile_view(request):
    print(f"Mostrando perfil para usuario {request.user.username}")
    # Si el usuario no ha completado su perfil, redirigirlo a la página correspondiente
    try:
        profile = request.user.profile
        
        # Verificar si el perfil está completo (para jobseeker verificamos full_name, para employer company_name)
        if profile.user_type == 'jobseeker' and not profile.full_name:
            print("Perfil de jobseeker incompleto, redirigiendo...")
            messages.info(request, 'Por favor complete su perfil para continuar.')
            return redirect('complete_jobseeker_profile')
        elif profile.user_type == 'employer' and not profile.company_name:
            print("Perfil de employer incompleto, redirigiendo...")
            messages.info(request, 'Por favor complete el perfil de su empresa para continuar.')
            return redirect('complete_employer_profile')
        
        # Si el perfil está completo, mostrar la vista normal
        return render(request, 'user_management/profile.html')
        
    except UserProfile.DoesNotExist:
        print(f"Usuario {request.user.username} no tiene perfil")
        messages.error(request, 'No tiene un perfil configurado.')
        return redirect('home')