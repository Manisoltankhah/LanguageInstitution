# Generated by Django 5.1.1 on 2025-04-17 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=100)),
                ('logo', models.ImageField(upload_to='uploads/logo')),
                ('about_us', models.TextField()),
                ('rules', models.TextField()),
                ('address', models.CharField(max_length=500)),
                ('phone_number', models.CharField(max_length=11)),
                ('email', models.EmailField(blank=True, max_length=254)),
            ],
        ),
    ]
