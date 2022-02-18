# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
	username    = StringField  (u'Username')
	password    = PasswordField(u'Password')

class RegisterForm(FlaskForm):
	name        = StringField  (u'name')
	lastname    = StringField  (u'lastname')
	password    = PasswordField(u'password')
	email       = StringField  (u'email')
