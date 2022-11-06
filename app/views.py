# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os
import logging
import json
from datetime import datetime
from sqlalchemy import desc, false, true
from werkzeug.datastructures import CombinedMultiDict

# Flask modules

from flask import render_template, request, url_for, redirect, send_from_directory, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

from werkzeug.utils import secure_filename

# App modules
from app import app, lm, db, bc
from app.models import Concurso, Users, UsuarioAdmin, Voz
from app.forms import LoginForm, RegisterForm, createConcursoForm, createVozForm, updateConcursoForm

# App schemas

from app.schemas import concurso_schema, concursos_schema, voces_schema, voz_schema, usuario_schema, usuarios_schema

# provide login manager with load_user callback

MSG_USER_SUCCESS = "Usuario creado exitosamente"
LABEL_CREATE_DATE = "Fecha de Creación"
URL_LIST_VOICE = "home/listVoices.html"

@lm.user_loader
def load_user(user_id):
    return UsuarioAdmin.query.get(int(user_id))

# Logout user


@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user


@app.route('/register.html', methods=['GET', 'POST'])
def register():
    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None
    success = False

    if request.method == 'GET':

        return render_template('accounts/register.html', form=form, msg=msg)

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        name = request.form.get('name', '', type=str)
        lastname = request.form.get('lastname', '', type=str)
        password = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)

        # filter User out of database through username
        user_by_email = UsuarioAdmin.query.filter_by(email=email).first()

        if user_by_email:
            msg = 'Error: Ya existe un usuario con este correo!'

        else:

            pw_hash = bc.generate_password_hash(password)

            user = UsuarioAdmin(email, pw_hash, name, lastname)

            user.save()

            msg = MSG_USER_SUCCESS
            success = True

    else:
        msg = ''

    return render_template('accounts/register.html', form=form, msg=msg, success=success)

# Authenticate user


@app.route('/login.html', methods=['GET', 'POST'])
def login():

    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)

        # filter User out of database through username
        user = UsuarioAdmin.query.filter_by(email=username).first()

        if user:

            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('concAdm'))
            else:
                msg = "Contraseña incorrecta, intente de nuevo"
        else:
            msg = "Usuario desconocido"

    return render_template('accounts/login.html', form=form, msg=msg)

# Register a new contest


@app.route('/cConcurso.html', methods=['GET', 'POST'])
def cConcurso():

    # declare the Registration Form
    form = createConcursoForm(request.form)

    msg = None
    success = False

    if request.method == 'GET':

        return render_template('home/cConcurso.html', form=form, msg=msg)

    # check if both http method is POST and form is valid on submit
    if request.method == 'POST':

        # assign form data to variables
        name = request.form.get('name', '', type=str)
        url_concurso = request.form.get('url_concurso', '', type=str)
        fecha_inicio = request.form.get('fecha_inicio', '')
        fecha_fin = request.form.get('fecha_fin', '')
        valor_pago = request.form.get('valor_pago', '')
        guion_voz = request.form.get('guion_voz', '')
        recomendaciones = request.form.get('recomendaciones', '')
        # format

        print(name, fecha_fin, fecha_inicio)
    # convert from string format to datetime format

        print(type(fecha_inicio))

        # filter User out of database through username
        # user_by_email = Concurso.query.filter_by(email=email).first()

        # if user_by_email:
        #    msg = 'Error: Ya existe un usuario con este correo!'

        user = Concurso(nombre=name, url_concurso=url_concurso, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, valor_pago=valor_pago,
                        guion_voz=guion_voz, recomendaciones=recomendaciones, email_admin=current_user.email, fecha_creacion=datetime.now())
        db.session.add(user)
        db.session.commit()
        print('!!!!!!', user.nombre, user.email_admin, user.fecha_creacion,
              user.fecha_fin, user.fecha_inicio, user.guion_voz)

        msg = MSG_USER_SUCCESS
        success = True

    else:
        msg = ''

    return render_template('home/cConcurso.html', form=form, msg=msg, success=success)


# Form to load user voice
@app.route('/concursos/<urlConcurso>/ingresarVoz', methods=['GET', 'POST'])
def ingresarVoz(urlConcurso):
    concurso = Concurso.query.filter_by(url_concurso=urlConcurso).first()
    if concurso:
        # declare the Registration Form

        form = createVozForm(request.form)

        msg = None
        success = False

        if request.method == 'GET':

            return render_template('home/cVoices.html', form=form, msg=msg)

            # check if both http method is POST and form is valid on submit
        if request.method == 'POST':
            # assign form data to variables
            name = request.form.get('name', '', type=str)
            lastname = request.form.get('lastname', '', type=str)
            email = request.form.get('email', '', type=str)
            observaciones = request.form.get('observaciones', ' ', type=str)
            print("request.files")
            file = request.files['profile']
            print(request.files['profile'])

            voz = Voz(email=email, nombre=name, apellido=lastname,
                      observaciones=observaciones, fecha_creacion=datetime.now(), procesado=0)
            print(voz.email, voz.nombre, voz.apellido, voz.observaciones,
                  voz.fecha_creacion, voz.procesado, '!!!!!!!')
            # crearVozUsuario(concurso,file,voz)
            # voz.save(concurso,file)
            crearVozUsuario(concurso, file, voz)
            msg = MSG_USER_SUCCESS
            success = True

        else:
            msg = ''

        return render_template('home/vozCargada.html')
    else:
        return render_template('home/page-404.html'), 404


def crearVozUsuario(concurso, file, voz):
    filename = secure_filename(file.filename)
    file_url = os.path.join(
        app.root_path, 'static/Archivos_Originales', filename)
    file.save(file_url)
    # Guardar voz
    voz.url_voz_original = file_url
    concurso.voces.append(voz)
    db.session.add(concurso)
    db.session.commit()

# App main route + generic routing


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    try:

        if not path.endswith('.html'):
            path += '.html'

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template('home/' + path)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')

def traerConcursos():
    concursos = Concurso.query.filter_by(email_admin=current_user.email).all()
    objtemp = concursos_schema.dump(concursos)
    for s in objtemp:
        s['ID'] = s.pop('id')
        s['Nombre'] = s.pop('nombre')
        s['Fecha de Inicio'] = s.pop('fecha_inicio')
        s['Fecha de Finalización'] = s.pop('fecha_fin')
        s[LABEL_CREATE_DATE] = s.pop('fecha_creacion')
        s['Valor pagado al ganador'] = s.pop('valor_pago')
        s['Url concurso'] = s.pop('url_concurso')
        s.pop("url_imagen", None)
        s.pop("guion_voz", None)
        s.pop("recomendaciones", None)
        s.pop("email_admin", None)

    return objtemp


@app.route('/concAdm.html')
def concAdm():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('home/concAdm.html', datos=traerConcursos())

# Form to load user voice
@app.route('/concursos/<urlConcurso>', methods=['GET', 'POST'])
def verVoces(urlConcurso):
    concurso = Concurso.query.filter_by(url_concurso=urlConcurso).first()
    if concurso:
        if (not current_user.is_authenticated):
            return render_template(URL_LIST_VOICE, datos=traerVoces(0,concurso.id),concursoActual=concurso,auth=0)
        elif (current_user.email!=concurso.email_admin):
            return render_template(URL_LIST_VOICE, datos=traerVoces(0,concurso.id),concursoActual=concurso,auth=0)
        return render_template(URL_LIST_VOICE, datos=traerVoces(1,concurso.id),concursoActual=concurso,auth=1)

def traerVoces(b,cId):
    if b:
        voces = Voz.query.filter_by(concurso_id=cId).order_by(desc(Voz.fecha_creacion)).all()
        objtemp = voces_schema.dump(voces)
        for s in objtemp:
            s['ID']=s.pop('id')
            s['Email']=s.pop('email')
            s['Nombre(s)']=s.pop('nombre')
            s['Apellido(s)']=s.pop('apellido')
            s['Estado']=s.pop('procesado')
            s[LABEL_CREATE_DATE]=s.pop('fecha_creacion')
            s['Voz Original']=s.pop('url_voz_original')
            s['Voz procesada']=s.pop('url_voz_convertida')
            s.pop("observaciones", None)
            s.pop("concurso_id", None)
    else:
        voces = Voz.query.filter_by(concurso_id=cId,procesado=1).order_by(desc(Voz.fecha_creacion)).all()
        objtemp = voces_schema.dump(voces)
        for s in objtemp:
            s['ID']=s.pop('id')
            s['Voz procesada']=s.pop('url_voz_convertida')
            s[LABEL_CREATE_DATE]=s.pop('fecha_creacion')
            s.pop("email", None)
            s.pop("nombre", None)
            s.pop("apellido", None)
            s.pop("procesado", None)
            s.pop("url_voz_original", None)
            s.pop("observaciones", None)
            s.pop("concurso_id", None)

    return objtemp

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('static', request.args['filename'])

@app.route('/RUDConcurso.html')
def RUDConcurso():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('home/RUDConcurso.html', )


# Form to load user voice
@app.route('/RUDConcurso.html/<urlConcurso>', methods=['GET', 'POST'])
def verConcurso(urlConcurso):

    form = updateConcursoForm(request.form)

    msg = None
    success = False

    if request.method == 'GET':
        concurso = Concurso.query.filter_by(url_concurso=urlConcurso).first()
        if concurso:
            if (not current_user.is_authenticated):
                return render_template('login')
        print(concurso.recomendaciones)
        return render_template('home/RUDConcurso.html', concursoActual=concurso, form=form, msg=msg)

    if request.method == 'POST':
        concurso = Concurso.query.filter_by(url_concurso=urlConcurso).first()
        format = '%Y/%m/%d'
        if 'name' in request.form:
            concurso.nombre = request.form.get('name', '', type=str)

        if 'url_concurso' in request.form:
            concurso.url_concurso = request.form.get('url_concurso', '', type=str)

        if 'fecha_inicio' in request.form:
            concurso.fecha_inicio =  request.form.get('fecha_inicio', '')

        if 'fecha_fin' in request.form:
            concurso.fecha_fin = request.form.get('fecha_fin', '')

        if 'valor_pago' in request.form:
            concurso.valor_pago = request.form.get('valor_pago', '')

        if 'guion_voz' in request.form:
            concurso.guion_voz = request.form.get('guion_voz', '')

        if 'recomendaciones' in request.form:
            concurso.recomendaciones = request.form.get('recomendaciones', '')

        db.session.commit()

        print('!!!!!!', concurso.nombre)

        msg = 'Concurso actualizado exitosamente'
        success = True


    return redirect(url_for('concAdm'))

@app.route('/deleteConcurso/<urlConcurso>')
def deleteConcurso(urlConcurso):
    concurso =  Concurso.query.filter_by(url_concurso=urlConcurso).first()
    db.session.delete(concurso)
    db.session.commit()
    return redirect(url_for('concAdm'))
