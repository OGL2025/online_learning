from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
from app.models import User  # FIXED: Changed 'Student' to 'User'

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    student_id = StringField('Student ID (ID Number)', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_student_id(self, student_id):
        # FIXED: Use User query
        user = User.query.filter_by(student_id=student_id.data).first()
        if user is not None:
            raise ValidationError('Please use a different Student ID.')

    def validate_email(self, email):
        # FIXED: Use User query
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class SubmissionForm(FlaskForm):
    file = FileField('Upload Assignment File', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip', 'py', 'pptx', 'xls', 'xlsx'], 'Invalid file type!')
    ])
    submit = SubmitField('Submit Assignment')

class DiscussionForm(FlaskForm):
    title = StringField('Topic Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post Discussion')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Add Comment')