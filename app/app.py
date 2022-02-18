from flask import Flask, request, jsonify, render_template
from models import db, UsuarioAdmin, Concurso, Voz
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import ffmpeg
import re
import os
from celery import Celery
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required, current_user, logout_user
from werkzeug import secure_filename

app = Flask(__name__)

app.config.from_object('config')

db.app = app
db.init_app(app)
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


ma = Marshmallow(app)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_Usuario(usuario_id):
    return UsuarioAdmin.query.get(int(usuario_id))

# Schema Usuario


class Usuario_Schema(ma.Schema):

    class Meta:

        fields = ("id", "email", "password", "nombre", "apellido")


usuario_schema = Usuario_Schema()
usuarios_schema = Usuario_Schema(many=True)

# Schema Concurso


class Concurso_Schema(ma.Schema):

    class Meta:

        fields = ("id", "nombre", "url_imagen", "url_concurso", "fecha_inicio", "fecha_fin",
                  "fecha_creacion", "valor_pago", "guion_voz", "recomendaciones", "email_admin")


concurso_schema = Concurso_Schema()
concursos_schema = Concurso_Schema(many=True)

# Schema Voz


class Voz_Schema(ma.Schema):

    class Meta:

        fields = ("id", "email", "nombre", "apellido", "fecha_creacion", "procesado",
                  "url_voz_original", "url_voz_convertida", "observaciones", "concurso_id")


voz_schema = Voz_Schema()
voces_schema = Voz_Schema(many=True)


class ResourceLogin(Resource):
    def post(self):
        email_login = request.form.get("email")
        password = request.form.get("password")

        usuario = UsuarioAdmin.query.filter_by(email=email_login).first()

        if not usuario or not check_password_hash(UsuarioAdmin.password, password):
            responseDict = {
                "message": "Email o password incorrecta"
            }
            response = jsonify(responseDict)
            response.headers.add(
                'Access-Control-Allow-Origin', 'http://localhost:3000')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        login_user(usuario)
        result = usuario_schema.dump(usuario)
        response = usuario_schema.jsonify(result)
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


class ResourceLogOut(Resource):
    @login_required
    def get(self):
        logout_user()
        responseDict = {
            "message": "El usuario se ha desconectado exitosamente"
        }
        response = jsonify(responseDict)
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


class ResourceSignUp(Resource):
    def post(self):
        email_login = request.form.get("email")
        password = request.form.get("password")
        password_encrypt = generate_password_hash(
            request.json["password"].encode("utf-8"))

        usuario = UsuarioAdmin.query.filter_by(email=email_login).first()
        if usuario:
            responseDict = {
                "message": "YA existe un usuario registrado con el email"
            }
            return json.dumps(responseDict)

        nuevo_Usuario = UsuarioAdmin(
            email=email_login,
            password=password_encrypt.decode("utf-8"),
            nombre=request.form.get("nombre"),
            apellido=request.form.get("apellido"))
        db.session.add(nuevo_Usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_Usuario)


# Recurso Concursos
class ResourceListarConcursos(Resource):

    def get(self):
        concursos = Concurso.query.all()
        return concurso_schema.dump(concursos)

    def post(self):
        nuevo_concurso = Concurso(
            nombre=request.json['nombre'],
            url_imagen=request.json['url_imagen'],
            url_concurso=request.json['url_concurso'],
            fecha_inicio=datetime.strptime(
                request.form.get("fecha_inicio"), '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(
                request.form.get("fecha_fin"), '%Y-%m-%d').date(),
            fecha_creacion=datetime.strptime(
                request.form.get("fecha_creacion"), '%Y-%m-%d').date(),
            valor_pago=request.json['valor_pago'],
            guion_voz=request.json['guion_voz'],
            recomendaciones=request.json['recomendaciones'],
            email_admin=request.json['email_admin'],
        )
        db.session.add(nuevo_concurso)
        db.session.commit()
        return concursos_schema.dump(nuevo_concurso)


# Recurso un concurso
class ResourceUnConcurso(Resource):

    def get(self, id_concurso):
        concurso = Concurso.query.get_or_404(id_concurso)
        return concursos_schema.dump(concurso)

    def put(self, id_concurso):
        concurso = Concurso.query.get_or_404(id_concurso)

        if 'nombre' in request.json:
            concurso.nombre = request.json['nombre']

        if 'url_imagen' in request.json:
            concurso.url_imagen = request.json['url_imagen']

        if 'url_concurso' in request.json:
            concurso.url_concurso = request.json['url_concurso']\

        if 'fecha_inicio' in request.json:
            concurso.fecha_inicio = datetime.strptime(
                request.form.get("fecha_inicio"), '%Y-%m-%d').date(),

        if 'fecha_fin' in request.json:
            concurso.fecha_fin = datetime.strptime(
                request.form.get("fecha_fin"), '%Y-%m-%d').date(),

        if 'fecha_creacion' in request.json:
            concurso.fecha_creacion = datetime.strptime(
                request.form.get("fecha_creacion"), '%Y-%m-%d').date(),

        if 'valor_pago' in request.json:
            concurso.valor_pago = request.json['valor_pago']

        if 'guion_voz' in request.json:
            concurso.guion_voz = request.json['guion_voz']

        if 'recomendaciones' in request.json:
            concurso.recomendaciones = request.json['recomendaciones']

        if 'email_admin' in request.json:
            concurso.email_admin = request.json['email_admin']

        db.session.commit()
        return concurso_schema.dump(concurso)

    def delete(self, id_concurso):
        concurso = Concurso.query.get_or_404(id_concurso)
        db.session.delete(concurso)
        db.session.commit()
        return '', 204


# Retornar concursos creado por usuario
class ResourceConcursosPorUsuario(Resource):
    @login_required
    def get(self):
        email = current_user.email
        concursos_usuario = Concurso.query.filter_by(email_admin=email)
        result = concursos_schema.dump(concursos_usuario)
        response = concursos_schema.jsonify(result)
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


# Recurso Voz
class ResourceListarVoces(Resource):

    def get(self):
        voces = Voz.query.all()
        return voces_schema.dump(voces)

    def post(self):
        nueva_voz = Voz(
            email=request.json['email'],
            nombre=request.json['nombre'],
            apellido=request.json['apellido'],
            fecha_creacion=datetime.strptime(
                request.form.get("fecha_creacion"), '%Y-%m-%d').date(),
            procesado=request.json['procesado'],
            url_voz_original=request.json['url_voz_original'],
            url_voz_convertida=request.json['url_voz_convertida'],
            observaciones=request.json['observaciones'],
            concurso_id=request.json['concurso_id'],
        )

        db.session.add(nueva_voz)
        db.session.commit()
        return voz_schema.dump(nueva_voz)


# Retornar voces subidas por concurso
class ResourceVocesPorConcurso(Resource):
    def get(self, id_concurso):
        voces_concurso = Voz.query.filter_by(concurso_id=id_concurso)
        result = voces_schema.dump(voces_concurso)
        response = voces_schema.jsonify(result)
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# Retornar detalle por voz


class ResourceDetallePorVoz(Resource):
    def get(self, id_voz):

        voz = Voz.query.get_or_404(id_voz)

        return voz_schema.dump(voz)


@app.route('/uploader', methods=['GET', 'POST'])
def agregarVoz(voz, id_concurso):
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        concurso = Concurso.query.get_or_404(id_concurso)

    voz.url_voz_original = ''
    concurso.voces.append(voz)

    db.session.add(concurso)
    db.session.commit()
    return voz_schema.dump(voz)


# Initialize Celery
celery = Celery(
    app.name, broker=app.config['CELERY_BROKER_URL'], include=['app'])
celery.conf.update(app.config)


@celery.task
def enviarCorreo(nombre, email, nombreConcurso):
    subject = "{}, tu voz ha sido procesada".format(nombre)
    print("Inicio envio mail a {}".format(email))
    msg = Message(subject, sender='supervoicesinfo@gmail.com',
                  recipients=[email])
    msg.body = 'Tu voz ha sido publicada en la página del concurso {}. ¡Mucha suerte!'.format(
        nombreConcurso)
    with app.app_context():
        mail.send(msg)
        print("Mail enviado!")


def convertir_archivo(urlEntrada):
    print("Convirtiendo archivo {}".format(urlEntrada))
    stream = ffmpeg.input(urlEntrada)
    ruta, ext = os.path.splitext(urlEntrada)
    urlSalida = ruta + ".mp3"
    urlSalida = urlSalida.replace(
        "Archivos_Originales", "Archivos_Convertidos")
    stream = ffmpeg.output(stream, urlSalida)
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)
    print("Archivo convertido. Ruta {}".format(urlSalida))
    return urlSalida


@celery.task
def convertir_voces():
    with app.app_context():
        vocesAProcesar = Voz.query.filter_by(procesado=False).all()
        for voz in vocesAProcesar:
            print("Inicio conversion de voz de {}".format(voz.email))
            urlSalida = convertir_archivo(voz.url_voz_original)
            voz.procesado = True
            voz.url_voz_convertida = urlSalida
            db.session.commit()
            enviarCorreo.delay(voz.nombre, voz.email, voz.concurso.nombre)


@scheduler.task('interval', id='job_process', seconds=60, misfire_grace_time=120)
def cronTask():
    with scheduler.app.app_context():
        convertir_voces.delay()


# Endpoints

api.add_resource(ResourceLogin, '/login')
api.add_resource(ResourceLogOut, '/logout')
api.add_resource(ResourceSignUp, '/signup')
api.add_resource(ResourceListarConcursos, '/concursos')
api.add_resource(ResourceUnConcurso, '/concursos/<int:id_concurso>')
api.add_resource(ResourceConcursosPorUsuario, '/concursosUsuario')
api.add_resource(ResourceListarVoces, '/voces')
api.add_resource(ResourceVocesPorConcurso, '/vocesConcurso')
api.add_resource(ResourceDetallePorVoz, '/voces/<int:id_voz>')


if __name__ == '__main__':
    # app.run(debug=True,host='0.0.0.0', port=5001)
    app.run(debug=True)
