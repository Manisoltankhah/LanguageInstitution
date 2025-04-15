from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.contrib import messages
from account_module.models import User, Class, AttendanceSession, AttendanceRecord, Score, Term
from .forms import ScoreForm


# Teacher Panel Views
class TeacherPanelView(TemplateView):
    template_name = 'teacher_panel/teacher_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_teacher = self.request.user
        context['current_teacher'] = current_teacher
        return context


class TeacherActiveCoursesView(TemplateView):
    template_name = 'teacher_panel/teacher_active_courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_teacher = self.request.user

        # Filter classes taught by the current teacher and having at least one student
        classes = Class.objects.filter(teacher=current_teacher, students__isnull=False).distinct()

        context['current_teacher'] = current_teacher
        context['classes'] = classes
        return context


class ClassSessionsView(TemplateView):
    template_name = 'teacher_panel/class_sessions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the teacher by their slug
        teacher_slug = self.kwargs.get('teacher_slug')
        teacher = get_object_or_404(User, slug=teacher_slug)

        # Retrieve the class by its slug and ensure it belongs to the teacher
        class_slug = self.kwargs.get('class_slug')
        class_obj = get_object_or_404(Class, slug=class_slug, teacher=teacher)

        # Retrieve all sessions for the class
        sessions = class_obj.attendance_sessions.all()

        # Add data to the context
        context['teacher'] = teacher
        context['class_obj'] = class_obj
        context['sessions'] = sessions

        return context


class TakeAttendanceView(View):
    def get(self, request, teacher_slug, class_slug, pk):
        teacher = get_object_or_404(User, slug=teacher_slug, user_type='teacher')
        class_obj = get_object_or_404(Class, slug=class_slug)
        session = get_object_or_404(AttendanceSession, pk=pk, class_obj=class_obj)

        if teacher != class_obj.teacher:
            return render(request, 'error.html', {'message': 'You are not authorized to take attendance for this class.'})

        students = User.objects.filter(user_type='student', current_term=class_obj.term)
        students_with_attendance = []
        for student in students:
            attendance_record = AttendanceRecord.objects.filter(session=session, student=student).first()
            is_present = attendance_record.present if attendance_record else False
            students_with_attendance.append({'student': student, 'is_present': is_present})

        return render(request, 'teacher_panel/take_attendance.html', {
            'teacher': teacher,
            'class_obj': class_obj,
            'session': session,
            'students_with_attendance': students_with_attendance
        })

    def post(self, request, teacher_slug, class_slug, pk):
        teacher = get_object_or_404(User, slug=teacher_slug, user_type='teacher')
        class_obj = get_object_or_404(Class, slug=class_slug)
        session = get_object_or_404(AttendanceSession, pk=pk, class_obj=class_obj)

        if teacher != class_obj.teacher:
            return render(request, 'error.html', {'message': 'You are not authorized to take attendance for this class.'})

        students = User.objects.filter(user_type='student', current_term=class_obj.term)
        for student in students:
            present = request.POST.get(f'student_{student.id}') == 'on'
            AttendanceRecord.objects.update_or_create(
                session=session,
                student=student,
                defaults={'present': present}
            )
        return redirect('attendance_success')


class AttendanceSuccessView(View):
    def get(self, request):
        return render(request, 'teacher_panel/attendance_success.html')


class TeacherActiveCoursesForScoresView(TemplateView):
    template_name = 'teacher_panel/teacher_active_courses_for_scores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_teacher = self.request.user

        # Filter classes taught by the current teacher and having at least one student
        classes = Class.objects.filter(teacher=current_teacher, students__isnull=False).distinct()

        context['current_teacher'] = current_teacher
        context['classes'] = classes
        return context


class ScoresStudentsView(TemplateView):
    template_name = 'teacher_panel/scores_Students.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the teacher by their slug
        teacher_slug = self.kwargs.get('teacher_slug')
        teacher = get_object_or_404(User, slug=teacher_slug)

        # Retrieve the class by its slug and ensure it belongs to the teacher
        class_slug = self.kwargs.get('class_slug')
        class_obj = get_object_or_404(Class, slug=class_slug, teacher=teacher)
        students = class_obj.students.filter(user_type='student')

        context['teacher'] = teacher
        context['class_obj'] = class_obj
        context['students'] = students
        return context


class SetScoreView(View):
    def get(self, request, teacher_slug, class_slug, student_slug):
        score_form = ScoreForm()
        context = {'score_form': score_form}
        return render(request, 'teacher_panel/set_score.html', context)

    def post(self, request, teacher_slug, class_slug, student_slug):
        teacher = get_object_or_404(User, slug=teacher_slug, user_type='teacher')
        class_obj = get_object_or_404(Class, slug=class_slug)
        student = get_object_or_404(User, slug=student_slug, user_type='student')

        if teacher != class_obj.teacher:
            return render(request, 'error.html', {'message': 'You are not authorized to access this page.'})

        score_form = ScoreForm(request.POST)
        if score_form.is_valid():
            score = score_form.save(commit=False)
            score.student = student
            score.term = class_obj.term
            score.save()
            messages.success(request, 'Scores saved successfully.')
            return redirect(reverse('score_students', args=[teacher.slug, class_obj.slug]))
        context = {'score_form': score_form}
        return render(request, 'teacher_panel/set_score.html', context)


# Student Panel Views
class StudentPanelView(TemplateView):
    template_name = 'student_panel/student_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_student = self.request.user
        context['current_student'] = current_student
        return context


class StudentActiveCoursesView(TemplateView):
    template_name = 'student_panel/student_active_course.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_student = self.request.user
        classes = Class.objects.filter(students=current_student)
        context['current_student'] = current_student
        context['classes'] = classes
        return context


class StudentAttendanceDetailView(TemplateView):
    template_name = 'student_panel/student_attendance_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_student = self.request.user
        class_obj = get_object_or_404(Class, students=current_student)
        sessions_info = AttendanceRecord.objects.filter(session__class_obj=class_obj, student_id=current_student.id)
        context['current_student'] = current_student
        context['sessions_info'] = sessions_info
        context['class_obj'] = class_obj
        return context


class StudentScoreActiveCoursesView(TemplateView):
    template_name = 'student_panel/student_score_active_course.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_student = self.request.user

        # Retrieve all terms where the student has scores
        terms_with_scores = (
            Score.objects.filter(student=current_student)
            .values_list('term', flat=True)
            .distinct()
        )

        # Retrieve the Term objects for those terms
        previous_terms = Term.objects.filter(id__in=terms_with_scores).order_by('-order')

        # Debugging: Print the terms to verify
        print("Previous Terms:", previous_terms)

        # Add data to the context
        context['current_student'] = current_student
        context['previous_terms'] = previous_terms
        return context


class StudentScoreDetailView(TemplateView):
    template_name = 'student_panel/student_score_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_student = self.request.user
        # class_obj = get_object_or_404(Class, students=current_student)
        scores = Score.objects.filter(student_id=current_student.id)
        context['current_student'] = current_student
        context['scores'] = scores
        # context['class_obj'] = class_obj
        return context