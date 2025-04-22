# EmployerPortal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.employer_dashboard, name='employer_dashboard'),
    path('create-job/', views.create_job_offer, name='create_job_offer'),
    path('edit-draft/<int:draft_id>/', views.edit_job_draft, name='edit_job_draft'),
    path('job/<int:job_id>/', views.view_job_offer, name='view_job_offer'),
    path('find-candidates/', views.find_candidates, name='find_candidates'),
    path('contact-candidate/<int:match_id>/', views.contact_candidate, name='contact_candidate'),
    path('applications/', views.view_applications, name='view_applications'),
    path('application/<int:application_id>/update/', views.update_application, name='update_application'),
]