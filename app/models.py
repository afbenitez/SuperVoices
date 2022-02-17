# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app         import db
from flask_login import UserMixin

class UsuarioAdmin(db.Model,UserMixin):
	__tablename__ = 'usuarioadmin'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	nombre = db.Column(db.String(200))
	apellido = db.Column(db.String(200))

	def __init__(self,email,password,nombre,apellido):
		self.email=email
		self.password=password
		self.nombre=nombre
		self.apellido

	def __repr__(self):
		return str(self.id)+'-'+str(self.email)
		
	def save(self):
		# inject self into db session    
		db.session.add ( self )
		# commit change and save the object
		db.session.commit( )
		return self 


class Concurso(db.Model):
	__tablename__ = 'concurso'
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(200))
	url_imagen = db.Column(db.String(300))
	url_concurso = db.Column(db.String(300))
	fecha_inicio = db.Column(db.Date())
	fecha_fin = db.Column(db.Date())
	fecha_creacion = db.Column(db.DateTime())
	valor_pago = db.Column(db.Float)
	guion_voz = db.Column(db.String(1000))
	recomendaciones = db.Column(db.String(1000))
	email_admin = db.Column(db.String(100))
	voces = db.relationship('Voz', backref='concurso',lazy='dynamic')

class Voz(db.Model):
	__tablename__ = 'voz'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100))
	nombre = db.Column(db.String(200))
	apellido = db.Column(db.String(200))
	fecha_creacion = db.Column(db.DateTime())
	procesado = db.Column(db.Boolean)
	url_voz_original = db.Column(db.String(300))
	url_voz_convertida = db.Column(db.String(300))
	observaciones = db.Column(db.String(1000))
	concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id'))

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id       = db.Column(db.Integer,     primary_key=True)
    user     = db.Column(db.String(64),  unique = True)
    email    = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user       = user
        self.password   = password
        self.email      = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):

        # inject self into db session    
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self 
