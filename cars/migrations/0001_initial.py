# Generated by Django 4.2.19 on 2025-03-28 09:34

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
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_number', models.CharField(max_length=20, unique=True)),
                ('make', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('year', models.IntegerField()),
                ('mileage', models.IntegerField()),
                ('engine_size', models.DecimalField(decimal_places=1, max_digits=3)),
                ('fuel_type', models.CharField(choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric'), ('hybrid', 'Hybrid'), ('lpg', 'LPG')], max_length=10)),
                ('mot_expiry_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cars', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommended_date', models.DateField()),
                ('recommended_mileage', models.IntegerField(blank=True, null=True)),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('scheduled', 'Scheduled'), ('completed', 'Completed'), ('declined', 'Declined')], default='pending', max_length=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_recommendations', to='cars.car')),
                ('service_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.servicetype')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_date', models.DateField()),
                ('mileage_at_service', models.IntegerField()),
                ('price_paid', models.DecimalField(decimal_places=2, max_digits=8)),
                ('notes', models.TextField(blank=True, null=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_history', to='cars.car')),
                ('service_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.servicetype')),
            ],
            options={
                'ordering': ['-service_date'],
            },
        ),
    ]
