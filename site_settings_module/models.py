from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='uploads/logo')
    about_us = models.TextField()
    rules = models.TextField()
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=11)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f'{self.site_name}/{self.phone_number}'
