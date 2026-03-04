from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    """Public registration form — students & teachers self-register."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False, max_length=15)
    department = forms.CharField(required=False, max_length=100)
    student_id = forms.CharField(
        required=False,
        max_length=20,
        help_text="Required for students.",
    )
    role = forms.ChoiceField(
        choices=[
            (CustomUser.Role.STUDENT, 'Student'),
            (CustomUser.Role.TEACHER, 'Teacher'),
        ],
        initial=CustomUser.Role.STUDENT,
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'role', 'department', 'student_id', 'phone_number',
            'password1', 'password2',
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        student_id = cleaned_data.get('student_id')
        email = cleaned_data.get('email')

        # student must provide an ID
        if role == CustomUser.Role.STUDENT and not student_id:
            self.add_error('student_id', 'Student ID is required for students.')

        # email uniqueness enforced at registration
        if email:
            qs = CustomUser.objects.filter(email__iexact=email)
            if qs.exists():
                self.add_error('email', 'A user with that email already exists.')

        return cleaned_data

    def clean_email(self):
        # ensure normalized email
        email = self.cleaned_data.get('email')
        if email:
            return email.lower()
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 7:
                raise forms.ValidationError('Enter a valid phone number.')
            return phone
        return phone


class CustomLoginForm(AuthenticationForm):
    """Styled login form."""
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class AdminCreateUserForm(UserCreationForm):
    """Admin/Librarian creates any user including other librarians."""

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'role', 'department', 'student_id', 'phone_number',
            'is_approved', 'password1', 'password2',
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        student_id = cleaned_data.get('student_id')

        if role == CustomUser.Role.STUDENT and not student_id:
            self.add_error('student_id', 'Student ID is required for students.')

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = CustomUser.objects.filter(email__iexact=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('A user with that email already exists.')
            return email.lower()
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 7:
                raise forms.ValidationError('Enter a valid phone number.')
            return phone
        return phone


class ProfileUpdateForm(forms.ModelForm):
    """Members update their own profile."""

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email',
            'phone_number', 'department', 'profile_picture',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = CustomUser.objects.filter(email__iexact=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This email is already in use.')
            return email.lower()
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 7:
                raise forms.ValidationError('Enter a valid phone number.')
            return phone
        return phone

class AdminApproveUserForm(forms.ModelForm):
    """Quick form for admin to approve/reject and set role."""

    class Meta:
        model = CustomUser
        fields = ['role', 'is_approved']

    def clean(self):
        cleaned_data = super().clean()
        # nothing special yet but placeholder for future checks
        return cleaned_data