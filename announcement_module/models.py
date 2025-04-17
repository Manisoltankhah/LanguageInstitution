from django.db import models


class Announcements(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_date = models.DateField(auto_now_add=True)
    picture = models.ImageField(upload_to='uploads/announcements')

    def __str__(self):
        return f'{self.title}/{self.created_date}'