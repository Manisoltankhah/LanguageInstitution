from django.contrib import admin
from . import models
admin.site.register(models.User)
admin.site.register(models.Score)
admin.site.register(models.Term)
admin.site.register(models.Class)
admin.site.register(models.AttendanceRecord)
admin.site.register(models.AttendanceSession)
admin.site.register(models.AcademicRecord)
