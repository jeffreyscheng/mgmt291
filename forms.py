from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
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
    roleplay_type = StringField('Type', validators=[DataRequired()])
    submit = SubmitField('Add Roleplay')
