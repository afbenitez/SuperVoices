# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from wsgiref.validate import validator
from xml.dom import ValidationErr
from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired,FileAllowed
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
	name        = StringField  (u'Nombre', validators=[DataRequired()])
	url_concurso    = StringField  (u'URL para el concurso')
	url_imagen = FileField(u'Imagen', validators=[Regexp(u'^[^/\\\\]\.jpg$')])
	fecha_inicio = DateTimeField(u'Fecha Inicio',id="fecha_inicio" ,format='%m/%d/%y', validators=[DataRequired()])
	fecha_fin = DateTimeField(u'Fecha Fin', format='%m/%d/%y',validators=[DataRequired()])
	valor_pago = DecimalField(u'Valor a pagar', validators=[DataRequired()])
	guion_voz = TextAreaField(u'Guión', validators=[DataRequired()])
	recomendaciones = TextAreaField(u'Recomendaciones')

class createVozForm(FlaskForm):
	name        = StringField  (u'name', validators=[DataRequired()])
	lastname    = StringField  (u'lastname', validators=[DataRequired()])
	email       = StringField  (u'email' , validators=[DataRequired(), Email(message='El correo no tiene el formato adecuado')])
	profile = FileField(u'profile', validators=[FileRequired(), FileAllowed(['mp3', 'ogg','wav'], 'Solo archivos de voz!')])
	observaciones = TextAreaField(u'Observaciones')
