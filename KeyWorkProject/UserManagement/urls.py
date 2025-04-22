from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('signup/', views.signupaccount, name='signup'),
    path('login/', views.loginaccount, name='login'),
    path('logout/', views.logoutaccount, name='logout'),
    
    # Perfiles
    path('profile/', views.profile_view, name='profile'),
    path('complete-employer-profile/', views.complete_employer_profile, name='complete_employer_profile'),
    path('complete-jobseeker-profile/', views.complete_jobseeker_profile, name='complete_jobseeker_profile'),
    
    
    # Url de prueba de autenticación (solo para desarrollo)
    #path('test-auth/', views.test_auth, name='test_auth'),
]