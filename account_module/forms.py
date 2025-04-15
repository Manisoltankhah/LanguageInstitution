from django import forms


from django import forms
from django.contrib.auth.hashers import make_password
from .models import User


class RegisterForm(forms.ModelForm):
    """
    A form for registering new users.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'user_type',
            'gender',
            'national_id',
            'parent_number',
            'password',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first_name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last_name'}),
            'user_type': forms.Select(choices=User.USER_TYPE_CHOICES, attrs={'class': 'form-select', 'id': 'schedule'}),
            'gender': forms.Select(choices=User.GENDER_CHOICES, attrs={'class': 'form-select', 'id': 'schedule'}),
            'national_id': forms.TextInput(attrs={'placeholder': 'Enter your national ID'}),
            'parent_number': forms.TextInput(attrs={'placeholder': 'Enter parent phone number'}),
        }

    def clean(self):
        """
        Validate the form data, ensuring passwords match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user instance with hashed password.
        """
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class GatewayForm(forms.Form):
    """
        Custom login form with additional styling or validation if needed.
        """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'نام کاربری را وارد کنید', 'id': 'username', 'class': 'user inputgeneral'}),
        label=""
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز ورود خود را وارد کنید', 'id': 'psw', 'class': 'inputgeneral'}),
        label=""
    )

