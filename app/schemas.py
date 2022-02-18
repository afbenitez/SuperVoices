from app import ma
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