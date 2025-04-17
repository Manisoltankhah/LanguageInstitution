from django.test import TestCase
from django.contrib.auth import get_user_model
from account_module.models import Term, Class, AcademicRecord, Score, AttendanceSession, AttendanceRecord
import uuid

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        # Create terms
        self.term1 = Term.objects.create(name="Term 1", order=1)
        self.term2 = Term.objects.create(name="Term 2", order=2)

        # Create a teacher
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )

        # Create a student
        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            current_term=self.term1
        )

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.teacher.user_type, 'teacher')
        self.assertEqual(self.student.user_type, 'student')

    def test_full_name_method(self):
        self.assertEqual(self.teacher.full_name(), 'John Doe')
        self.assertEqual(self.student.full_name(), 'Jane Smith')

    def test_slug_autogeneration(self):
        self.assertTrue(self.teacher.slug)
        self.assertTrue(self.student.slug)

    def test_username_set_to_national_id(self):
        self.assertEqual(self.teacher.username, '1234567890')
        self.assertEqual(self.student.username, '0987654321')


class TermModelTest(TestCase):
    def setUp(self):
        self.term = Term.objects.create(name="First Term", order=1)

    def test_term_creation(self):
        self.assertEqual(Term.objects.count(), 1)
        self.assertEqual(self.term.slug, 'first-term')

    def test_term_str(self):
        self.assertEqual(str(self.term), "First Term")


class ClassModelTest(TestCase):
    def setUp(self):
        self.term = Term.objects.create(name="Term 1", order=1)
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )

    def test_class_creation(self):
        class_obj = Class.objects.create(
            name="Class A",
            gender='male',
            teacher=self.teacher,
            term=self.term
        )
        self.assertEqual(Class.objects.count(), 1)
        self.assertTrue(class_obj.slug)

    def test_class_str(self):
        class_obj = Class.objects.create(
            name="Class A",
            gender='male',
            teacher=self.teacher,
            term=self.term
        )
        self.assertEqual(str(class_obj), "Class A")

    def test_default_teacher_assignment(self):
        # Create another teacher to test default assignment
        teacher2 = User.objects.create_user(
            username='teacher2',
            national_id='2234567890',
            first_name='Sarah',
            last_name='Connor',
            user_type='teacher',
            gender='female'
        )

        class_obj = Class.objects.create(
            name="Class B",
            gender='female',
            term=self.term
            # No teacher specified
        )

        # Should assign one of the available teachers
        self.assertIn(class_obj.teacher, [self.teacher, teacher2])


class AcademicRecordModelTest(TestCase):
    def setUp(self):
        self.term1 = Term.objects.create(name="Term 1", order=1)
        self.term2 = Term.objects.create(name="Term 2", order=2)

        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            current_term=self.term1
        )

        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )

        self.class_obj = Class.objects.create(
            name="Class A",
            gender='female',
            teacher=self.teacher,
            term=self.term1
        )
        self.class_obj.students.add(self.student)

    def test_academic_record_creation(self):
        record = AcademicRecord.objects.create(
            student=self.student,
            term=self.term1,
            passed=False
        )
        self.assertEqual(AcademicRecord.objects.count(), 1)
        self.assertFalse(record.passed)

    def test_academic_record_str(self):
        record = AcademicRecord.objects.create(
            student=self.student,
            term=self.term1,
            passed=True
        )
        self.assertEqual(str(record), f"{self.student.username} - Term 1 - Passed: {record.passed}")

    def test_academic_record_auto_update_from_score(self):
        # Create a score that should pass the student
        score = Score.objects.create(
            student=self.student,
            term=self.term1,
            quiz_1=20,
            quiz_2=20,
            oral_or_listening=10,
            class_activity=10,
            final=30  # Total = 90
        )

        record = AcademicRecord.objects.get(student=self.student, term=self.term1)
        self.assertTrue(record.passed)

        # Update score to failing grade
        score.final = 10  # Total = 70 (assuming passing is >70)
        score.save()
        record.refresh_from_db()
        self.assertFalse(record.passed)


class ScoreModelTest(TestCase):
    def setUp(self):
        self.term = Term.objects.create(name="Term 1", order=1)
        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            current_term=self.term
        )

    def test_score_creation(self):
        score = Score.objects.create(
            student=self.student,
            term=self.term,
            quiz_1=10,
            quiz_2=10,
            oral_or_listening=5,
            class_activity=5,
            final=20
        )
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(score.total_score, 50)

    def test_total_score_property(self):
        score = Score.objects.create(
            student=self.student,
            term=self.term,
            quiz_1=15,
            quiz_2=15,
            oral_or_listening=10,
            class_activity=10,
            final=30
        )
        self.assertEqual(score.total_score, 80)

    def test_score_str(self):
        score = Score.objects.create(
            student=self.student,
            term=self.term,
            quiz_1=10,
            quiz_2=10,
            final=20
        )
        self.assertEqual(str(score), f"{self.student.username} - Total: 40")


class AttendanceSessionTest(TestCase):
    def setUp(self):
        self.term = Term.objects.create(name="Term 1", order=1)
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )
        self.class_obj = Class.objects.create(
            name="Class A",
            gender='male',
            teacher=self.teacher,
            term=self.term
        )

    def test_attendance_session_creation(self):
        session = AttendanceSession.objects.create(
            session_number=1,
            class_obj=self.class_obj
        )
        self.assertEqual(AttendanceSession.objects.count(), 1)
        self.assertEqual(str(session), "Session 1 - Class A")


class AttendanceRecordTest(TestCase):
    def setUp(self):
        self.term = Term.objects.create(name="Term 1", order=1)
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )
        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            current_term=self.term
        )
        self.class_obj = Class.objects.create(
            name="Class A",
            gender='female',
            teacher=self.teacher,
            term=self.term
        )
        self.class_obj.students.add(self.student)
        self.session = AttendanceSession.objects.create(
            session_number=1,
            class_obj=self.class_obj
        )

    def test_attendance_record_creation(self):
        record = AttendanceRecord.objects.create(
            session=self.session,
            student=self.student,
            present=True
        )
        self.assertEqual(AttendanceRecord.objects.count(), 1)
        self.assertTrue(record.present)
        self.assertEqual(str(record), f"{self.student.username} - Present")


class StudentPromotionTest(TestCase):
    def setUp(self):
        # Create terms
        self.term1 = Term.objects.create(name="Term 1", order=1)
        self.term2 = Term.objects.create(name="Term 2", order=2)
        self.term3 = Term.objects.create(name="Term 3", order=3)

        # Create teacher
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )

        # Create student
        self.student = User.objects.create_user(
            username='student1',
            national_id='0987654321',
            first_name='Jane',
            last_name='Smith',
            user_type='student',
            gender='female',
            current_term=self.term1
        )

        # Create classes
        self.class1 = Class.objects.create(
            name="Class A - Term 1 - Female",
            gender='female',
            teacher=self.teacher,
            term=self.term1
        )
        self.class1.students.add(self.student)

        self.class2 = Class.objects.create(
            name="Class A - Term 2 - Female",
            gender='female',
            teacher=self.teacher,
            term=self.term2
        )

        # Create sessions for class2
        from account_module.models import create_sessions_for_class
        create_sessions_for_class(self.class2)

    def test_promote_to_next_term_success(self):
        # Create a passing score
        Score.objects.create(
            student=self.student,
            term=self.term1,
            quiz_1=20,
            quiz_2=20,
            oral_or_listening=10,
            class_activity=10,
            final=30  # Total = 90
        )

        # Check promotion happened
        self.student.refresh_from_db()
        self.assertEqual(self.student.current_term, self.term2)

        # Check student was moved to the next class
        self.assertIn(self.student, self.class2.students.all())
        self.assertNotIn(self.student, self.class1.students.all())

        # Check sessions exist for the new class
        self.assertEqual(self.class2.attendance_sessions.count(), 12)

    def test_promote_to_next_term_fail_no_score(self):
        # Try to promote without any scores
        result = self.student.promote_to_next_term()
        self.assertFalse(result)
        self.student.refresh_from_db()
        self.assertEqual(self.student.current_term, self.term1)

    def test_promote_to_next_term_fail_low_score(self):
        # Create a failing score
        Score.objects.create(
            student=self.student,
            term=self.term1,
            quiz_1=10,
            quiz_2=10,
            oral_or_listening=5,
            class_activity=5,
            final=20  # Total = 50
        )

        # Check promotion didn't happen
        self.student.refresh_from_db()
        self.assertEqual(self.student.current_term, self.term1)

    def test_promote_to_next_term_fail_no_higher_term(self):
        # Student is already in the highest term
        self.student.current_term = self.term3
        self.student.save()

        # Create a passing score
        Score.objects.create(
            student=self.student,
            term=self.term3,
            quiz_1=20,
            quiz_2=20,
            oral_or_listening=10,
            class_activity=10,
            final=30  # Total = 90
        )

        # Try to promote
        result = self.student.promote_to_next_term()
        self.assertFalse(result)
        self.student.refresh_from_db()
        self.assertEqual(self.student.current_term, self.term3)

    def test_promote_to_next_term_fail_not_student(self):
        # Try to promote a teacher
        result = self.teacher.promote_to_next_term()
        self.assertFalse(result)

    def test_promote_to_next_term_fail_no_current_term(self):
        # Student with no current term
        student2 = User.objects.create_user(
            username='student2',
            national_id='1987654321',
            first_name='Alice',
            last_name='Johnson',
            user_type='student',
            gender='female',
            current_term=None
        )

        result = student2.promote_to_next_term()
        self.assertFalse(result)

    def test_promote_to_next_term_fail_not_in_class(self):
        # Student not enrolled in any class for current term
        student2 = User.objects.create_user(
            username='student2',
            national_id='1987654321',
            first_name='Alice',
            last_name='Johnson',
            user_type='student',
            gender='female',
            current_term=self.term1
        )

        # Create a passing score
        Score.objects.create(
            student=student2,
            term=self.term1,
            quiz_1=20,
            quiz_2=20,
            oral_or_listening=10,
            class_activity=10,
            final=30  # Total = 90
        )

        result = student2.promote_to_next_term()
        self.assertFalse(result)
        student2.refresh_from_db()
        self.assertEqual(student2.current_term, self.term1)


class CreateSessionsForClassTest(TestCase):
    def setUp(self):
        self.term = Term.objects.create(name="Term 1", order=1)
        self.teacher = User.objects.create_user(
            username='teacher1',
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            user_type='teacher',
            gender='male'
        )

    def test_create_sessions_for_class(self):
        class_obj = Class.objects.create(
            name="Class A",
            gender='male',
            teacher=self.teacher,
            term=self.term
        )

        # Call the function directly
        from account_module.models import create_sessions_for_class
        create_sessions_for_class(class_obj)

        # Check that 12 sessions were created
        self.assertEqual(class_obj.attendance_sessions.count(), 12)

        # Check session numbers are correct
        session_numbers = list(class_obj.attendance_sessions.values_list('session_number', flat=True))
        self.assertEqual(session_numbers, list(range(1, 13)))