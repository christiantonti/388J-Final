from tokenize import String
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import (
    StringField, IntegerField, SubmitField, TextAreaField, PasswordField,
     SelectField, DateTimeField, BooleanField, EmailField
)
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Regexp
)

from flask_app.utils_nodb import FormField


from .models import User

class RegistrationForm(FlaskForm):
    uid = StringField(
        "UID", validators=[InputRequired(), Length(min=9, max=9), Regexp("^\d{9}$")]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    phone = StringField("Phone", validators=[InputRequired(), Length(min=10, max=10), Regexp("^\d{10}$")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=24)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    fname = StringField("First Name", validators=[InputRequired(), Length(max=15), Regexp("^\w+$")])
    lname = StringField("Last Name", validators=[InputRequired(), Length(max=25), Regexp("^\w+$")])
    submit = SubmitField("Sign Up")

    def validate_username(self, uid):
        user = User.objects(uid=uid.data).first()
        if user is not None:
            raise ValidationError("UID is already registered!")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is already registered!")

# ***** MEMBER SEARCH *****
class MemberSearchForm(FlaskForm):
    query = StringField("Search for a user:", validators=[InputRequired(), Length(max=25), Regexp("^\w+$")])
    submit = SubmitField("Search")

# ***** ACCOUNT FORMS *****
class LoginForm(FlaskForm):
    uid = StringField("UID", validators=[InputRequired(), Length(min=9, max=9), Regexp("^\d{9}$")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=24)])
    submit = SubmitField("Login")

class UpdateAccountForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    phone = StringField("Phone", validators=[InputRequired(), Length(min=10, max=10), Regexp("^\d{10}$")])
    fname = StringField("First Name", validators=[InputRequired(), Length(max=15), Regexp("^\w+$")])
    lname = StringField("Last Name", validators=[InputRequired(), Length(max=25), Regexp("^\w+$")])
    submit = SubmitField("Update Info")

class UpdateProfilePicForm(FlaskForm):
    pfp = FileField(
        "Profile Picture", validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Images files only!")]
    )
    submit = SubmitField("Update Photo")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=24)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")

# ***** ADMIN FORMS *****
class PointsForm(FlaskForm):
    # choices will be dynamically filled in routes
    uid = SelectField("Select a Member", validators=[InputRequired()])
    points = IntegerField("Point Change", validators=[InputRequired(), NumberRange(min=-100, max=100)])
    reason = TextAreaField("Reason", validators=[InputRequired(), Length(min=4, max=150)])
    submit = SubmitField("Submit")

class ViewLogsForm(FlaskForm):
    uid = SelectField("Member", validators=[InputRequired()])
    submit = SubmitField("Submit")

# creates a custom form class and returns an instance of it
# (for form creation)
def createCustomCreationForm(num_fields, **kwargs):
    choices = [
        (FormField.STRING_FIELD.value, "String Field"),
        (FormField.INT_FIELD.value, "Number Field"),
        (FormField.BOOL_FIELD.value, "Checkbox Field"),
        (FormField.EMAIL_FIELD.value, "Email Field")]

    class CustomCreationForm(FlaskForm):
        name = StringField("Form Name", validators=[InputRequired(), Length(min=5, max=40)])
        due_date = DateTimeField("Due Date (Format: MM/DD/YY HH:MM) (24H Time)", format="%m/%d/%y %H:%M")
    
    # add custom fields
    for i in range(1, num_fields+1):
        # type select dropdown
        label = f"Field {i} Type:"
        field = SelectField(label, choices=choices, validators=[InputRequired()])
        setattr(CustomCreationForm, f"field{i}sel", field)
        label = f"Field {i} Label:"
        field = StringField(label, validators=[InputRequired(), Length(min=4, max=60)])
        setattr(CustomCreationForm, f"field{i}label", field)
    
    # now add submit
    submit = SubmitField("Create Form")
    setattr(CustomCreationForm, "submit", submit)
    
    return CustomCreationForm(**kwargs)

# creates a custom form based off a loaded FormObject
def LoadFormObject(form_obj, **kwargs):
    class CustomForm(FlaskForm):
        pass

    # create custom fields defined in form_obj
    for i in range(len(form_obj.fields)):
        field = form_obj.fields[i]
        label = form_obj.labels[i]
        # switch case on enum
        field_obj = None
        if field == FormField.STRING_FIELD.value:
            field_obj = StringField(label, validators=[InputRequired()])
        elif field == FormField.INT_FIELD.value:
            field_obj = IntegerField(label, validators=[InputRequired()])
        elif field == FormField.BOOL_FIELD.value:
            field_obj = BooleanField(label)
        elif field == FormField.EMAIL_FIELD.value:
            field_obj = EmailField(label, validators=[InputRequired()])
        setattr(CustomForm, f"field{i}", field_obj)

    # now add submit
    submit = SubmitField("Submit")
    setattr(CustomForm, "submit", submit)

    return CustomForm(**kwargs)

# ***** EVENT CREATION FORM *****
class EventCreationForm(FlaskForm):
    name = StringField("Event Name", validators=[InputRequired(), Length(min=5, max=80)])
    description = TextAreaField("Event Description", validators=[InputRequired(), Length(max=150)])
    start = DateTimeField("Start Time (Format: MM/DD/YY HH:MM) (24H Time)", format="%m/%d/%y %H:%M")
    end = DateTimeField("End Time (Format: MM/DD/YY HH:MM) (24H Time)", format="%m/%d/%y %H:%M")
    create_form = BooleanField("Generate Attendance Form?")
    submit = SubmitField("Submit")