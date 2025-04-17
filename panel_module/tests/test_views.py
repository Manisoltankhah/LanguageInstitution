from django.test import TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from account_module.models import User, Class, Term, AttendanceSession, AttendanceRecord, Score
from panel_module.views import (
    TeacherPanelView, TeacherActiveCoursesView, ClassSessionsView, TakeAttendanceView,
    AttendanceSuccessView, TeacherActiveCoursesForScoresView, ScoresStudentsView,
    SetScoreView, StudentPanelView, StudentActiveCoursesView, StudentAttendanceDetailView,
    StudentScoreActiveCoursesView, StudentScoreDetailView
)
from panel_module.forms import ScoreForm

User = get_user_model()


class URLTests(TestCase):
    def test_teacher_panel_url_resolves(self):
        url = reverse('teacher_panel', args=['teacher-slug'])
        self.assertEqual(url, '/teacher-panel/teacher-slug/')
        self.assertEqual(resolve(url).func.view_class, TeacherPanelView)

    def test_attendance_active_courses_url_resolves(self):
        url = reverse('attendance_active_courses', args=['teacher-slug'])
        self.assertEqual(url, '/teacher-panel/teacher-slug/attendance/')
        self.assertEqual(resolve(url).func.view_class, TeacherActiveCoursesView)

    def test_attendance_sessions_url_resolves(self):
        url = reverse('attendance_sessions', args=['teacher-slug', 'class-slug'])
        self.assertEqual(url, '/teacher-panel/teacher-slug/attendance/class-slug/sessions/')
        self.assertEqual(resolve(url).func.view_class, ClassSessionsView)

    def test_attendance_taking_url_resolves(self):
        url = reverse('attendance_taking', args=['teacher-slug', 'class-slug', 1])
        self.assertEqual(url, '/teacher-panel/teacher-slug/attendance/class-slug/sessions/1/')
        self.assertEqual(resolve(url).func.view_class, TakeAttendanceView)

    def test_attendance_success_url_resolves(self):
        url = reverse('attendance_success')
        self.assertEqual(url, '/teacher-panel/attendance/successful/')
        self.assertEqual(resolve(url).func.view_class, AttendanceSuccessView)

    def test_score_active_courses_url_resolves(self):
        url = reverse('score_active_courses', args=['teacher-slug'])
        self.assertEqual(url, '/teacher-panel/teacher-slug/score/')
        self.assertEqual(resolve(url).func.view_class, TeacherActiveCoursesForScoresView)

    def test_score_students_url_resolves(self):
        url = reverse('score_students', args=['teacher-slug', 'class-slug'])
        self.assertEqual(url, '/teacher-panel/teacher-slug/score/class-slug/')
        self.assertEqual(resolve(url).func.view_class, ScoresStudentsView)

    def test_score_taking_url_resolves(self):
        url = reverse('score_taking', args=['teacher-slug', 'class-slug', 'student-slug'])
        self.assertEqual(url, '/teacher-panel/teacher-slug/attendance/class-slug/student-slug/')
        self.assertEqual(resolve(url).func.view_class, SetScoreView)

    def test_student_panel_url_resolves(self):
        url = reverse('student_panel', args=['student-slug'])
        self.assertEqual(url, '/student-panel/student-slug/')
        self.assertEqual(resolve(url).func.view_class, StudentPanelView)

    def test_attendance_course_url_resolves(self):
        url = reverse('attendance_course', args=['student-slug'])
        self.assertEqual(url, '/student-panel/student-slug/attendance/')
        self.assertEqual(resolve(url).func.view_class, StudentActiveCoursesView)

    def test_attendance_info_url_resolves(self):
        url = reverse('attendance_info', args=['student-slug', 'class-slug'])
        self.assertEqual(url, '/student-panel/student-slug/attendance/class-slug/')
        self.assertEqual(resolve(url).func.view_class, StudentAttendanceDetailView)

    def test_score_courses_url_resolves(self):
        url = reverse('score_courses', args=['student-slug'])
        self.assertEqual(url, '/student-panel/student-slug/score/')
        self.assertEqual(resolve(url).func.view_class, StudentScoreActiveCoursesView)

    def test_score_detail_url_resolves(self):
        url = reverse('score_detail', args=['student-slug', 'class-slug'])
        self.assertEqual(url, '/student-panel/student-slug/score/class-slug/')
        self.assertEqual(resolve(url).func.view_class, StudentScoreDetailView)


class TeacherPanelViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male',
            password='testpass123',
            slug='teacher-slug'
        )
        self.term = Term.objects.create(name="Term 1", order=1)
        self.class_obj = Class.objects.create(
            name="Class A",
            gender='male',
            teacher=self.teacher,
            term=self.term,
            slug='class-slug'
        )
        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            password='testpass123',
            current_term=self.term,
            slug='student-slug'
        )
        self.class_obj.students.add(self.student)
        self.session = AttendanceSession.objects.create(
            session_number=1,
            class_obj=self.class_obj
        )

    def test_teacher_panel_view(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('teacher_panel', args=[self.teacher.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/teacher_panel.html')
        self.assertEqual(response.context['current_teacher'], self.teacher)

    def test_teacher_active_courses_view(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('attendance_active_courses', args=[self.teacher.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/teacher_active_courses.html')
        self.assertIn(self.class_obj, response.context['classes'])

    def test_class_sessions_view(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('attendance_sessions', args=[self.teacher.slug, self.class_obj.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/class_sessions.html')
        self.assertEqual(response.context['class_obj'], self.class_obj)
        self.assertIn(self.session, response.context['sessions'])

    def test_take_attendance_view_get(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('attendance_taking', args=[self.teacher.slug, self.class_obj.slug, self.session.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/take_attendance.html')
        self.assertEqual(len(response.context['students_with_attendance']), 1)

    def test_take_attendance_view_post(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse('attendance_taking', args=[self.teacher.slug, self.class_obj.slug, self.session.id]),
            {f'student_{self.student.id}': 'on'}
        )
        self.assertRedirects(response, reverse('attendance_success'))
        record = AttendanceRecord.objects.get(session=self.session, student=self.student)
        self.assertTrue(record.present)

    def test_attendance_success_view(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('attendance_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/attendance_success.html')

    def test_teacher_active_courses_for_scores_view(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('score_active_courses', args=[self.teacher.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/teacher_active_courses_for_scores.html')
        self.assertIn(self.class_obj, response.context['classes'])

    def test_scores_students_view(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('score_students', args=[self.teacher.slug, self.class_obj.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/scores_Students.html')
        self.assertIn(self.student, response.context['students'])

    def test_set_score_view_get(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('score_taking', args=[self.teacher.slug, self.class_obj.slug, self.student.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_panel/set_score.html')
        self.assertIsInstance(response.context['score_form'], ScoreForm)

    def test_set_score_view_post(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse('score_taking', args=[self.teacher.slug, self.class_obj.slug, self.student.slug]),
            {
                'quiz_1': 20,
                'quiz_2': 20,
                'oral_or_listening': 10,
                'class_activity': 10,
                'final': 30
            }
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Scores saved successfully.')
        self.assertTrue(Score.objects.filter(student=self.student).exists())


class StudentPanelViewsTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male',
            password='testpass123'
        )
        self.term = Term.objects.create(name="Term 1", order=1)
        self.class_obj = Class.objects.create(
            name="Class A",
            gender='male',
            teacher=self.teacher,
            term=self.term,
            slug='class-slug'
        )
        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            password='testpass123',
            current_term=self.term,
            slug='student-slug'
        )
        self.class_obj.students.add(self.student)
        self.session = AttendanceSession.objects.create(
            session_number=1,
            class_obj=self.class_obj
        )
        self.attendance_record = AttendanceRecord.objects.create(
            session=self.session,
            student=self.student,
            present=True
        )
        self.score = Score.objects.create(
            student=self.student,
            term=self.term,
            quiz_1=20,
            quiz_2=20,
            oral_or_listening=10,
            class_activity=10,
            final=30
        )

    def test_student_panel_view(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('student_panel', args=[self.student.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_panel/student_panel.html')
        self.assertEqual(response.context['current_student'], self.student)

    def test_student_active_courses_view(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('attendance_course', args=[self.student.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_panel/student_active_course.html')
        self.assertIn(self.class_obj, response.context['classes'])

    def test_student_attendance_detail_view(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('attendance_info', args=[self.student.slug, self.class_obj.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_panel/student_attendance_detail.html')
        self.assertIn(self.attendance_record, response.context['sessions_info'])

    def test_student_score_active_courses_view(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('score_courses', args=[self.student.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_panel/student_score_active_course.html')
        self.assertIn(self.term, response.context['previous_terms'])

    def test_student_score_detail_view(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('score_detail', args=[self.student.slug, self.class_obj.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_panel/student_score_detail.html')
        self.assertIn(self.score, response.context['scores'])