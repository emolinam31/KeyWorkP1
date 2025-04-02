from django.urls import path
from . import views

urlpatterns = [
    path('', views.employer_portal, name='employer_portal'),
    path('upload-vacancy/', views.upload_vacancy, name='upload_vacancy'),
    path('find-candidate/', views.find_candidate, name='find_candidate'),
    path('notify-candidate/', views.notify_candidate, name='notify_candidate'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
]