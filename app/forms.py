# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from wsgiref.validate import validator
from xml.dom import ValidationErr
from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField,DateTimeField,DecimalField
from wtforms.validators import InputRequired, Email, DataRequired, Regexp, EqualTo

class LoginForm(FlaskForm):
	username    = StringField  (u'Username', validators=[DataRequired()])
	password    = PasswordField(u'Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
	name        = StringField  (u'name', validators=[DataRequired()])
	lastname    = StringField  (u'lastname', validators=[DataRequired()])
	password    = PasswordField(u'password', validators=[DataRequired(),EqualTo('passwordConf',message='Las contraseñas deben coincidir')])
	email       = StringField  (u'email' , validators=[DataRequired(), Email(message='El correo no tiene el formato adecuado')])
	passwordConf = PasswordField(u'passwordConf', validators=[DataRequired()])

class createConcursoForm(FlaskForm):
	name        = StringField  (u'name', validators=[DataRequired()])
	url_concurso    = StringField  (u'url_concurso')
	url_imagen = FileField(u'url_imagen', validators=[Regexp(u'^[^/\\\\]\.jpg$')])
	fecha_inicio = DateTimeField(u'fecha_inicio', format='%m/%d/%y', validators=[DataRequired()])
	fecha_fin = DateTimeField(u'fecha_fin', format='%m/%d/%y',validators=[DataRequired()])
	valor_pago = DecimalField(u'valor_pago', validators=[DataRequired()])
	guion_voz = TextAreaField(u'guion_voz', validators=[DataRequired()])
	recomendaciones = TextAreaField(u'recomendaciones')
