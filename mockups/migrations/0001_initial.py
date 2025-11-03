from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MockupJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(blank=True, max_length=100, null=True)),
                ('text', models.TextField()),
                ('font', models.CharField(blank=True, max_length=100, null=True)),
                ('text_color', models.CharField(default='#000000', max_length=7)),
                ('shirt_colors', models.JSONField(blank=True, default=list)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mockup_jobs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mockup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('font', models.CharField(blank=True, max_length=100, null=True)),
                ('text_color', models.CharField(default='#000000', max_length=7)),
                ('shirt_color', models.CharField(choices=[('yellow', 'yellow'), ('black', 'black'), ('white', 'white'), ('blue', 'blue')], max_length=10)),
                ('image', models.ImageField(upload_to='mockups/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mockups', to='mockups.mockupjob')),
            ],
        ),
    ]

