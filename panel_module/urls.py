from django.urls import path
from panel_module import views

urlpatterns = [
    path('teacher-panel/<slug:slug>/', views.TeacherPanelView.as_view(), name='teacher_panel'),

    # Attendance
    path('teacher-panel/<slug:slug>/attendance/', views.TeacherActiveCoursesView.as_view(), name='attendance_active_courses'),
    path('teacher-panel/<slug:teacher_slug>/attendance/<slug:class_slug>/sessions/', views.ClassSessionsView.as_view(), name='attendance_sessions'),
    path('teacher-panel/<slug:teacher_slug>/attendance/<slug:class_slug>/sessions/<int:pk>/', views.TakeAttendanceView.as_view(), name='attendance_taking'),
    path('teacher-panel/attendance/successful/', views.AttendanceSuccessView.as_view(), name='attendance_success'),

    # Score
    path('teacher-panel/<slug:slug>/score/', views.TeacherActiveCoursesForScoresView.as_view(), name='score_active_courses'),
    path('teacher-panel/<slug:teacher_slug>/score/<slug:class_slug>/', views.ScoresStudentsView.as_view(), name='score_students'),
    path('teacher-panel/<slug:teacher_slug>/attendance/<slug:class_slug>/<slug:student_slug>/', views.SetScoreView.as_view(), name='score_taking'),

    path('student-panel/<slug:slug>/', views.StudentPanelView.as_view(), name='student_panel'),
    path('student-panel/<slug:slug>/attendance/', views.StudentActiveCoursesView.as_view(), name='attendance_course'),
    path('student-panel/<slug:student_slug>/attendance/<slug:class_slug>/', views.StudentAttendanceDetailView.as_view(), name='attendance_info'),
    path('student-panel/<slug:slug>/score/', views.StudentScoreActiveCoursesView.as_view(), name='score_courses'),
    path('student-panel/<slug:student_slug>/score/<slug:class_slug>/', views.StudentScoreDetailView.as_view(), name='score_detail'),
]