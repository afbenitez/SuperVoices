# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging 
import json


# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory,jsonify
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2              import TemplateNotFound

# App modules
from app        import app, lm, db, bc
from app.models import Concurso, Users,UsuarioAdmin
from app.forms  import LoginForm, RegisterForm

# App schemas

from app.schemas import concurso_schema,concursos_schema,voces_schema,voz_schema,usuario_schema,usuarios_schema

# provide login manager with load_user callback
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

    msg     = None
    success = False

    if request.method == 'GET': 

        return render_template( 'accounts/register.html', form=form, msg=msg )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        name = request.form.get('name', '', type=str)
        lastname = request.form.get('lastname','',type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 



        # filter User out of database through username
        user_by_email = UsuarioAdmin.query.filter_by(email=email).first()

        if user_by_email:
            msg = 'Error: Ya existe un usuario con este correo!'
        
        else:
 
            pw_hash = bc.generate_password_hash(password)

            user = UsuarioAdmin(email, pw_hash,name,lastname)

            user.save()

            msg     = 'Usuario creado exitosamente'     
            success = True

    else:
        msg=''
 
    return render_template( 'accounts/register.html', form=form, msg=msg, success=success )

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

    return render_template( 'accounts/login.html', form=form, msg=msg )

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    try:

        if not path.endswith( '.html' ):
            path += '.html'

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( 'home/' + path )
    
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
        s['ID']=s.pop('id')
        s['Nombre']=s.pop('nombre')
        s['Fecha de Inicio']=s.pop('fecha_inicio')
        s['Fecha de Finalización']=s.pop('fecha_fin')
        s['Fecha de Creación']=s.pop('fecha_creacion')
        s['Valor pagado al ganador']=s.pop('valor_pago')
        s.pop("url_imagen", None)
        s.pop("url_concurso", None)
        s.pop("guion_voz", None)
        s.pop("recomendaciones", None)
        s.pop("email_admin", None)

    return objtemp

@app.route('/concAdm.html')
def concAdm():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('home/concAdm.html', datos=traerConcursos())




