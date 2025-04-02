# Generated by Django 5.1.6 on 2025-04-02 16:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('CollectionPoint', '0003_alter_cv_upload_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('employer', 'Empleador'), ('jobseeker', 'Buscador de Empleo')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True)),
                ('company_size', models.CharField(blank=True, max_length=50, null=True)),
                ('full_name', models.CharField(blank=True, max_length=150, null=True)),
                ('professional_title', models.CharField(blank=True, max_length=100, null=True)),
                ('years_experience', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('location', models.CharField(blank=True, max_length=150, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('skills', models.TextField(blank=True, help_text='Habilidades separadas por comas', null=True)),
                ('education', models.TextField(blank=True, null=True)),
                ('languages', models.CharField(blank=True, help_text='Idiomas separados por comas', max_length=200, null=True)),
                ('cv', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='CollectionPoint.cv')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
