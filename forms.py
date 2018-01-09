from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    class_name = StringField('Class', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Instructor Sign In')


class SignInForm(FlaskForm):
    student_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class AddRoleplayForm(FlaskForm):
    roleplay_name = StringField('Name', validators=[DataRequired()])
    group_size = IntegerField('Group Size', validators=[DataRequired()])
    submit = SubmitField('Add Roleplay')


class AddSectionForm(FlaskForm):
    section_name = StringField('Name', validators=[DataRequired()])
    instructor_name = StringField('Instructor', validators=[DataRequired()])
    submit = SubmitField('Add Section')
