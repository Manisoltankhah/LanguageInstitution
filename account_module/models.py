import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    """
    Custom User model to include additional fields like user type, current term, and gender.
    """
    USER_TYPE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    current_term = models.ForeignKey('Term', on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    national_id = models.CharField(max_length=10, blank=True, null=True)
    parent_number = models.CharField(max_length=11, blank=True, null=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def promote_to_next_term(self):
        """
        Promotes the student to the next term ONLY if they have passed the current term.
        Ensures students from the same class remain classmates in the next term.
        Creates 12 sessions for the new class using bulk creation.
        """
        # Check if user is a student
        if self.user_type != 'student':
            print(f"{self.first_name} {self.last_name} is not a student. Cannot promote.")
            return False

        # Check if current term is set
        if not self.current_term:
            print(f"{self.first_name} {self.last_name} has no current term assigned. Cannot promote.")
            return False

        # Check if student passed the term
        try:
            academic_record = AcademicRecord.objects.get(student=self, term=self.current_term)
            if not academic_record.passed:
                print(f"{self.first_name} {self.last_name} did not pass the current term. Cannot promote.")
                return False
        except AcademicRecord.DoesNotExist:
            print(f"No academic record found for {self.first_name} {self.last_name}. Cannot promote.")
            return False

        # Promote to the next term if there is a higher one
        try:
            next_term = Term.objects.get(order=self.current_term.order + 1)
        except Term.DoesNotExist:
            print(f"No higher term available for {self.first_name} {self.last_name}. Cannot promote.")
            return False

        # Identify the current class of the student
        try:
            current_class = Class.objects.get(term=self.current_term, students=self)
        except Class.DoesNotExist:
            print(
                f"{self.first_name} {self.last_name} is not enrolled in any class for the current term. Cannot promote."
            )
            return False

        # Find or create the corresponding next class for the current class
        base_class_name = current_class.name.split(' - ')[0]
        next_class_name = f"{base_class_name} - {next_term.name} - {current_class.gender.capitalize()}"
        next_class, created = Class.objects.get_or_create(
            name=next_class_name,
            term=next_term,
            gender=current_class.gender,
        )

        if created:
            print(f"Created new class: {next_class.name}")
            create_sessions_for_class(next_class)  # Call as a standalone function

        # Remove the student from the current class
        current_class.students.remove(self)
        print(f"Removed {self.first_name} {self.last_name} from {current_class.name}")

        # Add the student to the next class
        next_class.students.add(self)
        print(f"Added {self.first_name} {self.last_name} to {next_class.name}")

        # Update the student's current term
        self.current_term = next_term
        self.save()
        print(f"Promoted {self.first_name} {self.last_name} to {next_term.name}.")
        return True

    def save(self, *args, **kwargs):
        self.username = self.national_id
        if not self.slug:
            base_slug = slugify(self.username)
            self.slug = base_slug
            while User.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name()}/{self.username}"


class Term(models.Model):
    """
    Represents an academic term (e.g., Semester 1, Semester 2).
    """
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    slug = models.SlugField(db_index=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Class(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes_taught')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='classes_in_term')
    students = models.ManyToManyField(User, related_name='enrolled_classes', blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=100)

    def save(self, *args, **kwargs):
        # If no teacher is assigned, assign a default teacher (e.g., admin user)
        if not self.teacher_id:
            try:
                default_teacher = User.objects.filter(user_type='teacher').first()
                if default_teacher:
                    self.teacher = default_teacher
                else:
                    raise ValueError("No teacher exists in the system. Please create a teacher first.")
            except User.DoesNotExist:
                raise ValueError("No teacher exists in the system. Please create a teacher first.")

        self.slug = slugify(self.name)
        # Call the parent save method to save the class instance first
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AcademicRecord(models.Model):
    """
    Represents an academic record for a student in a specific term.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='academic_records')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='academic_records_in_term')
    passed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if the student has a score for this term
        try:
            score = Score.objects.get(student=self.student, term=self.term)
            if score.total_score > 70:
                self.passed = True
            else:
                self.passed = False
        except Score.DoesNotExist:
            self.passed = False

        # Save the academic record
        super().save(*args, **kwargs)

        # Promote the student to the next term if they passed
        if self.passed:
            self.student.promote_to_next_term()

    def __str__(self):
        return f"{self.student.username} - {self.term.name} - Passed: {self.passed}"


class AttendanceSession(models.Model):
    """
    Represents an attendance session for a specific class.
    """
    session_number = models.PositiveIntegerField()
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_sessions')

    def __str__(self):
        return f"Session {self.session_number} - {self.class_obj.name}"


class AttendanceRecord(models.Model):
    """
    Represents an attendance record for a student in a specific session.
    """
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {'Present' if self.present else 'Absent'}"


class Score(models.Model):
    """
    Represents scores for a student in a specific term.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='scores_in_term')
    quiz_1 = models.FloatField(blank=True, null=True)
    quiz_2 = models.FloatField(blank=True, null=True)
    oral_or_listening = models.FloatField(blank=True, null=True)
    class_activity = models.FloatField(blank=True, null=True)
    final = models.FloatField(blank=True, null=True)

    @property
    def total_score(self):
        """
        Calculate the total score based on the individual components.
        """
        return sum(filter(None, [
            self.quiz_1,
            self.quiz_2,
            self.oral_or_listening,
            self.class_activity,
            self.final
        ]))

    def save(self, *args, **kwargs):
        # Call the parent save method to save the score first
        super().save(*args, **kwargs)

        # Ensure an AcademicRecord exists for this student and term
        academic_record, created = AcademicRecord.objects.get_or_create(
            student=self.student,
            term=self.term,
            defaults={'passed': False}  # Default to not passed
        )

        # If the AcademicRecord was just created, update it based on the score
        if created:
            if self.total_score > 70:
                academic_record.passed = True
            else:
                academic_record.passed = False
            academic_record.save()

    def __str__(self):
        return f"{self.student.username} - Total: {self.total_score}"


def create_sessions_for_class(new_class):
    """
    Creates 12 sessions for a given class using bulk creation.
    """
    sessions = [
        AttendanceSession(
            session_number=i + 1,
            class_obj=new_class,
        )
        for i in range(12)
    ]
    AttendanceSession.objects.bulk_create(sessions)
    print(f"Created 12 sessions for {new_class.name}")