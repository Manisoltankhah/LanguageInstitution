from django.contrib import admin
from . import models


class ReadOnlyAdmin(admin.ModelAdmin):
    # Disable add, edit, and delete functionality
    def has_add_permission(self, request):
        return False  # Disable adding new objects

    def has_change_permission(self, request, obj=None):
        return False  # Disable editing existing objects

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deleting objects


# Customize list_display for each model
class AcademicRecordAdmin(ReadOnlyAdmin):
    list_display = ('student', 'term', 'passed')


class AttendanceRecordAdmin(ReadOnlyAdmin):
    list_display = ('session', 'student', 'present')


class ScoreAdmin(ReadOnlyAdmin):
    list_display = ('student', 'term', 'quiz_1', 'quiz_1', 'quiz_2', 'oral_or_listening', 'class_activity', 'final', 'total_score')  # Replace with actual fields


# Register the model with the custom admin class
admin.site.register(models.User)
admin.site.register(models.Score, ScoreAdmin)
admin.site.register(models.Term)
admin.site.register(models.Class)
admin.site.register(models.AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(models.AttendanceSession)
admin.site.register(models.AcademicRecord, AcademicRecordAdmin)
