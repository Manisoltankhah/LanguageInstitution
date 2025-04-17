from django.test import TestCase
from django.urls import reverse, resolve
from panel_module.views import (
    TeacherPanelView, TeacherActiveCoursesView, ClassSessionsView,
    TakeAttendanceView, AttendanceSuccessView, TeacherActiveCoursesForScoresView,
    ScoresStudentsView, SetScoreView, StudentPanelView, StudentActiveCoursesView,
    StudentAttendanceDetailView, StudentScoreActiveCoursesView, StudentScoreDetailView
)


class URLPatternTests(TestCase):
    def test_teacher_panel_url(self):
        url = reverse('teacher_panel', kwargs={'slug': 'teacher1'})
        self.assertEqual(url, '/teacher-panel/teacher1/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, TeacherPanelView)
        self.assertEqual(resolved.kwargs['slug'], 'teacher1')

    def test_attendance_active_courses_url(self):
        url = reverse('attendance_active_courses', kwargs={'slug': 'teacher1'})
        self.assertEqual(url, '/teacher-panel/teacher1/attendance/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, TeacherActiveCoursesView)
        self.assertEqual(resolved.kwargs['slug'], 'teacher1')

    def test_attendance_sessions_url(self):
        url = reverse('attendance_sessions', kwargs={
            'teacher_slug': 'teacher1',
            'class_slug': 'math101'
        })
        self.assertEqual(url, '/teacher-panel/teacher1/attendance/math101/sessions/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ClassSessionsView)
        self.assertEqual(resolved.kwargs['teacher_slug'], 'teacher1')
        self.assertEqual(resolved.kwargs['class_slug'], 'math101')

    def test_attendance_taking_url(self):
        url = reverse('attendance_taking', kwargs={
            'teacher_slug': 'teacher1',
            'class_slug': 'math101',
            'pk': 1
        })
        self.assertEqual(url, '/teacher-panel/teacher1/attendance/math101/sessions/1/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, TakeAttendanceView)
        self.assertEqual(resolved.kwargs['teacher_slug'], 'teacher1')
        self.assertEqual(resolved.kwargs['class_slug'], 'math101')
        self.assertEqual(resolved.kwargs['pk'], 1)

    def test_attendance_success_url(self):
        url = reverse('attendance_success')
        self.assertEqual(url, '/teacher-panel/attendance/successful/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, AttendanceSuccessView)

    def test_score_active_courses_url(self):
        url = reverse('score_active_courses', kwargs={'slug': 'teacher1'})
        self.assertEqual(url, '/teacher-panel/teacher1/score/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, TeacherActiveCoursesForScoresView)
        self.assertEqual(resolved.kwargs['slug'], 'teacher1')

    def test_score_students_url(self):
        url = reverse('score_students', kwargs={
            'teacher_slug': 'teacher1',
            'class_slug': 'math101'
        })
        self.assertEqual(url, '/teacher-panel/teacher1/score/math101/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ScoresStudentsView)
        self.assertEqual(resolved.kwargs['teacher_slug'], 'teacher1')
        self.assertEqual(resolved.kwargs['class_slug'], 'math101')

    def test_score_taking_url(self):
        url = reverse('score_taking', kwargs={
            'teacher_slug': 'teacher1',
            'class_slug': 'math101',
            'student_slug': 'student1'
        })
        self.assertEqual(url, '/teacher-panel/teacher1/attendance/math101/student1/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, SetScoreView)
        self.assertEqual(resolved.kwargs['teacher_slug'], 'teacher1')
        self.assertEqual(resolved.kwargs['class_slug'], 'math101')
        self.assertEqual(resolved.kwargs['student_slug'], 'student1')

    def test_student_panel_url(self):
        url = reverse('student_panel', kwargs={'slug': 'student1'})
        self.assertEqual(url, '/student-panel/student1/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, StudentPanelView)
        self.assertEqual(resolved.kwargs['slug'], 'student1')

    def test_attendance_course_url(self):
        url = reverse('attendance_course', kwargs={'slug': 'student1'})
        self.assertEqual(url, '/student-panel/student1/attendance/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, StudentActiveCoursesView)
        self.assertEqual(resolved.kwargs['slug'], 'student1')

    def test_attendance_info_url(self):
        url = reverse('attendance_info', kwargs={
            'student_slug': 'student1',
            'class_slug': 'math101'
        })
        self.assertEqual(url, '/student-panel/student1/attendance/math101/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, StudentAttendanceDetailView)
        self.assertEqual(resolved.kwargs['student_slug'], 'student1')
        self.assertEqual(resolved.kwargs['class_slug'], 'math101')

    def test_score_courses_url(self):
        url = reverse('score_courses', kwargs={'slug': 'student1'})
        self.assertEqual(url, '/student-panel/student1/score/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, StudentScoreActiveCoursesView)
        self.assertEqual(resolved.kwargs['slug'], 'student1')

    def test_score_detail_url(self):
        url = reverse('score_detail', kwargs={
            'student_slug': 'student1',
            'class_slug': 'math101'
        })
        self.assertEqual(url, '/student-panel/student1/score/math101/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, StudentScoreDetailView)
        self.assertEqual(resolved.kwargs['student_slug'], 'student1')
        self.assertEqual(resolved.kwargs['class_slug'], 'math101')