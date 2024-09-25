from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditorField


# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

class CreateNewList(FlaskForm):
    description= StringField("List Name", validators=[DataRequired(),Length(min=4, max=50)])
    submit = SubmitField("Create List")

class AddItemForm(FlaskForm):#use one text area and break on returns!!?
    description_1= StringField("To Do", validators=[DataRequired()])
    description_2= StringField("To Do")
    description_3= StringField("To Do")
    submit = SubmitField("Add Items")