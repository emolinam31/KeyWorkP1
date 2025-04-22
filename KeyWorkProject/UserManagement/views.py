from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.contrib import messages
from .forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm
from .models import JobSeekerProfile, EmployerProfile
from CollectionPoint.models import CV
import traceback

def signupaccount(request):
    if request.method == 'GET':
        return render(request, 'user_management/signup.html', {'form': CustomUserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                form = CustomUserCreationForm(request.POST)
                if form.is_valid():
                    user = form.save(commit=False)
                    user.email = form.cleaned_data['email']
                    user.save()
                    
                    # Crear el perfil según el tipo de usuario
                    user_type = form.cleaned_data.get('user_type')
                    
                    # Crear el perfil específico
                    if user_type == 'employer':
                        EmployerProfile.objects.create(user=user, profile_completed=False)
                        messages.success(request, '¡Cuenta creada exitosamente! Complete su perfil de empleador.')
                        login(request, user)
                        return redirect('complete_employer_profile')
                    else:
                        JobSeekerProfile.objects.create(user=user, profile_completed=False)
                        messages.success(request, '¡Cuenta creada exitosamente! Ahora suba su CV para continuar.')
                        login(request, user)
                        return redirect('upload_cv')
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
                        
@login_required
def upload_cv(request):
    # Verificar si el usuario es jobseeker
    user_type = request.GET.get('user_type', '')
    
    if user_type == 'jobseeker' or hasattr(request.user, 'jobseeker_profile'):
        # Es un buscador de empleo, puede continuar
        pass
    else:
        messages.error(request, 'Solo los buscadores de empleo pueden subir hojas de vida.')
        return redirect('home')
        
    if request.method == 'POST':
        # Si hay un archivo enviado, procesarlo
        if request.FILES.get('file'):
            # Procesar el archivo subido
            upload_type = request.POST.get('upload_type', 'document')
            uploaded_file = request.FILES['file']

            # Validar tipo de archivo
            if upload_type == 'document' and not uploaded_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Para documentos, solo se aceptan archivos PDF.')
                return redirect('upload_cv')
            elif upload_type == 'image' and not any(uploaded_file.name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                messages.error(request, 'Para imágenes, solo se aceptan archivos JPG o PNG.')
                return redirect('upload_cv')

            # Guardar en el modelo
            try:
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

                        messages.success(request, '¡Imagen subida y texto extraído correctamente!')
                    except Exception as e:
                        messages.warning(request, 'CV subido pero la extracción de texto falló.')

                # Asociar el CV con el perfil JobSeeker del usuario
                try:
                    # Obtener o crear el perfil de JobSeeker
                    jobseeker_profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
                    
                    with transaction.atomic():
                        old_cv = jobseeker_profile.cv
                        jobseeker_profile.cv = cv
                        jobseeker_profile.has_cv = True
                        
                        # Extraer información del texto para autocompletar el perfil
                        if extracted_text:
                            jobseeker_profile = extract_and_update_profile_data(jobseeker_profile, extracted_text)
                        
                        jobseeker_profile.save()
                    
                    messages.success(request, '¡CV subido y procesado exitosamente! Tu perfil ha sido actualizado automáticamente.')
                    
                    # Si el usuario tenía un CV anterior, eliminarlo
                    if old_cv and old_cv.id != cv.id:
                        # Opcionalmente eliminar el CV antiguo
                        pass

                except Exception as e:
                    messages.warning(request, f'CV subido pero no se pudo asociar al perfil: {str(e)}')

                return redirect('cv_detail', pk=cv.id)
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
                return redirect('upload_cv')
        else:
            # Si se está mostrando el formulario para seleccionar tipo
            upload_type = request.POST.get('upload_type', 'document')
            if upload_type == 'document':
                accept = '.pdf'
                title = 'Subir CV como documento PDF'
            elif upload_type == 'image':
                accept = '.jpg,.jpeg,.png'
                title = 'Subir CV como imagen'
            else:
                accept = '.mp3,.wav'
                title = 'Subir grabación de voz (Próximamente)'
                
            # Mostrar el formulario para seleccionar archivo
            return render(request, 'upload_cv.html', {
                'upload_type': upload_type,
                'accept': accept,
                'title': title
            })
    else:
        # Verificar si el usuario ya tiene un CV
        has_cv = False
        try:
            jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
            has_cv = jobseeker_profile.has_cv
        except JobSeekerProfile.DoesNotExist:
            pass
        
        # Mostrar opciones de tipo de archivo
        return render(request, 'upload_options.html', {
            'title': 'Subir Hoja de Vida',
            'has_cv': has_cv,
            'is_required': not has_cv
        })
        
def loginaccount(request):
    if request.method == 'GET':
        return render(request, 'user_management/login.html', {'form': AuthenticationForm()})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Intento de login: usuario={username}")
        
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is None:
                print(f"Autenticación fallida para: {username}")
                return render(request, 'user_management/login.html', {
                    'form': AuthenticationForm(),
                    'error': 'El nombre de usuario y la contraseña no coinciden.'
                })
            else:
                print(f"Usuario {user.username} autenticado correctamente")
                login(request, user)
                
                # Redirección simple
                return redirect('home')
        except Exception as e:
            print(f"Error durante la autenticación: {str(e)}")
            return render(request, 'user_management/login.html', {
                'form': AuthenticationForm(),
                'error': f'Error inesperado: {str(e)}'
            })
        
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
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'No tiene un perfil de empleador configurado.')
        return redirect('home')
    
    if request.method == 'GET':
        form = EmployerProfileForm(instance=employer_profile)
        return render(request, 'user_management/complete_employer_profile.html', {'form': form})
    else:
        try:
            form = EmployerProfileForm(request.POST, instance=employer_profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.profile_completed = True
                profile.save()
                
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('employer_dashboard')
            else:
                return render(request, 'user_management/complete_employer_profile.html', {'form': form})
        except Exception as e:
            import traceback
            print(f"Error al guardar el perfil de empleador: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error al guardar el perfil: {str(e)}')
            return render(request, 'user_management/complete_employer_profile.html', {'form': form})

@login_required
def complete_jobseeker_profile(request):
    try:
        # Obtener el perfil de JobSeeker
        jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        # Crear un nuevo perfil si no existe
        jobseeker_profile = JobSeekerProfile.objects.create(user=request.user)
    
    if request.method == 'GET':
        form = JobSeekerProfileForm(instance=jobseeker_profile)
        return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})
    else:
        try:
            form = JobSeekerProfileForm(request.POST, instance=jobseeker_profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.profile_completed = True
                profile.save()
                
                messages.success(request, 'Perfil actualizado correctamente.')
                
                # Si ya tiene CV, redirigir al perfil, sino a la subida de CV
                if profile.has_cv:
                    return redirect('profile')
                else:
                    return redirect('upload_cv')
            else:
                return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})
        except Exception as e:
            messages.error(request, f'Error al guardar el perfil: {str(e)}')
            return render(request, 'user_management/complete_jobseeker_profile.html', {'form': form})

@login_required
def profile_view(request):
    # Determinar el tipo de perfil
    try:
        jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
        # Es un buscador de empleo
        
        # Si el perfil no está completo, verificar si tiene CV
        if not jobseeker_profile.profile_completed:
            if jobseeker_profile.has_cv:
                # Si tiene CV pero el perfil no está completo, podría ser que
                # se extrajo automáticamente pero necesita revisión
                jobseeker_profile.profile_completed = True
                jobseeker_profile.save()
            else:
                # No tiene CV, redirigir a subir CV
                messages.info(request, 'Por favor suba su CV para continuar.')
                return redirect('upload_cv')
        
        # Mostrar el perfil del buscador de empleo
        return render(request, 'user_management/profile.html', {
            'profile_type': 'jobseeker',
            'jobseeker_profile': jobseeker_profile
        })
        
    except JobSeekerProfile.DoesNotExist:
        try:
            employer_profile = EmployerProfile.objects.get(user=request.user)
            # Es un empleador
            
            # Si el perfil no está completo
            if not employer_profile.profile_completed and not employer_profile.company_name:
                messages.info(request, 'Por favor complete su perfil de empresa.')
                return redirect('complete_employer_profile')
            
            # Mostrar el perfil del empleador
            return render(request, 'user_management/profile.html', {
                'profile_type': 'employer',
                'employer_profile': employer_profile
            })
            
        except EmployerProfile.DoesNotExist:
            # No tiene ningún tipo de perfil, error
            messages.error(request, 'No tiene un perfil configurado correctamente.')
            return redirect('home')
        
        
        
# Vista temporal para pruebas de autenticación
###       
    from django.http import HttpResponse
    from django.contrib.auth import authenticate, login
    from django.views.decorators.csrf import csrf_exempt  # Solo para pruebas

    @csrf_exempt  # Esta es solo para pruebas, no uses esto en producción
    def test_auth(request):
        """Vista temporal para probar la autenticación."""
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            print(f"Test Auth: Intentando autenticar usuario: {username}")
            
            # Intenta autenticar directamente
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # La autenticación fue exitosa
                login(request, user)
                return HttpResponse(f"Autenticación exitosa para {username}! Usuario está ahora logueado.")
            else:
                # La autenticación falló
                return HttpResponse(f"Autenticación fallida para {username}. Verifique credenciales.")
        
        # Formulario simple para GET
        return HttpResponse("""
        <form method="post">
            <label>Usuario: <input type="text" name="username"></label><br>
            <label>Contraseña: <input type="password" name="password"></label><br>
            <button type="submit">Probar</button>
        </form>
        """)
