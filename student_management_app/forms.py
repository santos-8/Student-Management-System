from django import forms
from student_management_app.models import Courses, SessionYearModel

class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(
        label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control","autocomplete":"off"})
    )
    password = forms.CharField(
        label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="First Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        label="Username", max_length=50, widget=forms.TextInput(attrs={"class": "form-control","autocomplete":"off"})
    )
    address = forms.CharField(
        label="Address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    course = forms.ChoiceField(label="Course", choices=[], widget=forms.Select(attrs={"class": "form-control"}))

    sex_choices = (("Male", "Male"), ("Female", "Female"))
    sex = forms.ChoiceField(label="Gender", choices=sex_choices, widget=forms.Select(attrs={"class": "form-control"}))

    session_year_id = forms.ChoiceField(label="Session Year", choices=[], widget=forms.Select(attrs={"class": "form-control"}))

    profile_pic = forms.FileField(
        label="Profile Pic", max_length=50, widget=forms.FileInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate course choices dynamically
        try:
            courses = Courses.objects.all()
            self.fields['course'].choices = [(course.id, course.course_name) for course in courses]
        except Exception:
            self.fields['course'].choices = []

        # Populate session choices dynamically
        try:
            sessions = SessionYearModel.objects.all()
            self.fields['session_year_id'].choices = [
                (ses.id, f"{ses.session_start_year} - {ses.session_end_year}") for ses in sessions
            ]
        except Exception:
            self.fields['session_year_id'].choices = []


class EditStudentForm(forms.Form):
    email = forms.EmailField(
        label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="First Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        label="Username", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address = forms.CharField(
        label="Address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    course = forms.ChoiceField(label="Course", choices=[], widget=forms.Select(attrs={"class": "form-control"}))

    sex_choices = (("Male", "Male"), ("Female", "Female"))
    sex = forms.ChoiceField(label="Gender", choices=sex_choices, widget=forms.Select(attrs={"class": "form-control"}))

    session_year_id = forms.ChoiceField(label="Session Year", choices=[], widget=forms.Select(attrs={"class": "form-control"}))

    profile_pic = forms.FileField(
        label="Profile Pic", max_length=50, widget=forms.FileInput(attrs={"class": "form-control"}), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate course choices dynamically
        try:
            courses = Courses.objects.all()
            self.fields['course'].choices = [(course.id, course.course_name) for course in courses]
        except Exception:
            self.fields['course'].choices = []

        # Populate session choices dynamically
        try:
            sessions = SessionYearModel.objects.all()
            self.fields['session_year_id'].choices = [
                (ses.id, f"{ses.session_start_year} - {ses.session_end_year}") for ses in sessions
            ]
        except Exception:
            self.fields['session_year_id'].choices = []
