from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.views import View
from account_module.forms import GatewayForm, RegisterForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


class UserRegistrationView(View):
    """
    Class-based view for user registration using the base View class.
    """
    template_name = 'register.html'

    def get(self, request):
        """
        Handle GET requests: Display the registration form.
        """
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Handle POST requests: Process the submitted form data.
        """
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save the user and display a success message
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            # Redirect based on user type
            if user.user_type == 'teacher':
                return redirect('teacher_panel')  # Redirect to teacher panel
            elif user.user_type == 'student':
                return redirect('student-gateway')  # Redirect to student panel
        else:
            # If the form is invalid, re-render the form with errors
            return render(request, self.template_name, {'form': form})


class StudentGatewayView(View):
    def get(self, request):
        # Render the login form for GET requests
        student_gateway_form = GatewayForm()
        return render(request, 'student_gateway.html', {'student_gateway_form': student_gateway_form})

    def post(self, request):
        # Process the login form submission
        student_gateway_form = GatewayForm(request.POST)
        if student_gateway_form.is_valid():
            username = student_gateway_form.cleaned_data.get('username')
            password = student_gateway_form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    if user.user_type == 'student':
                        # Log the user in and redirect to the student panel
                        login(request, user)
                        return redirect(reverse('student_panel', args=[user.slug]))
                    else:
                        student_gateway_form.add_error(None, 'شما زبان آموز نیستید')
                else:
                    # Add an error if the account is inactive
                    student_gateway_form.add_error(None, 'اکانت شما فعال سازی نشده')
            else:
                # Add an error if the credentials are invalid
                student_gateway_form.add_error(None, 'نام کاربری و رمز عبور اشتباه است')

        # If the form is invalid or authentication fails, re-render the form
        return render(request, 'student_gateway.html', {'student_gateway_form': student_gateway_form})


class TeacherGatewayView(View):

    def get(self, request):
        # Render the login form for GET requests
        teachers_gateway_form = GatewayForm()
        return render(request, 'teacher_gateway.html', {'teachers_gateway_form': teachers_gateway_form})

    def post(self, request):
        teachers_gateway_form = GatewayForm(request.POST)
        if teachers_gateway_form.is_valid():
            username = teachers_gateway_form.cleaned_data.get('username')
            password = teachers_gateway_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    if user.user_type == 'teacher':
                        login(request, user)
                        return redirect(reverse('teacher_panel', args=[user.slug]))
                    else:
                        teachers_gateway_form.add_error(None, 'شما جزو اساتید نیستید')
                else:
                    teachers_gateway_form.add_error(None, 'اکانت شما فعال سازی نشده')
            else:
                teachers_gateway_form.add_error(None, 'نام کاربری و رمز عبور اشتباه است')

        return render(request, 'teacher_gateway.html', context={'teachers_gateway_form': teachers_gateway_form})
