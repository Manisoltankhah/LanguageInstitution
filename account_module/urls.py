from django.urls import path
from .views import UserRegistrationView, TeacherGatewayView, StudentGatewayView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('teacher-gateway/', TeacherGatewayView.as_view(), name='teacher-gateway'),
    path('student-gateway/', StudentGatewayView.as_view(), name='student-gateway'),
]