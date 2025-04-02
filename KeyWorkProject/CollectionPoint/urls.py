from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_cv, name='upload_cv'),
    path('cv/<int:pk>/', views.cv_detail, name='cv_detail'),
    path('cv/<int:pk>/process-ocr/', views.process_ocr, name='process_ocr'),
    path('cv/<int:pk>/delete/', views.delete_cv, name='delete_cv'),
]