import os
from flask import Flask, g, render_template, request, session, redirect, url_for
from flask.helpers import send_from_directory
import base64
from sqlalchemy.orm import Session
# from flask_cors import CORS
from flask_cors import CORS

from disagro_i.clases import modelo
from disagro_i.conexion_orm import SessionLocal

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    # cors = CORS(app, resources={r"/inventario/*": {"origins": "*"}})
    app.config.from_mapping(SECRET_KEY='dev')
    CORS(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static/img'),'disagro.png',mimetype='image/png')

    @app.route('/')
    def index():
        # Si el usuario está autenticado, redirigir a inicio
        if g.user is not None:
            return redirect(url_for('inicio'))
        # Si no hay sesión, mostrar landing page
        return render_template('landing.html')

    @app.route('/inicio')
    def inicio():
        # Verificar que el usuario esté autenticado
        if g.user is None:
            return redirect(url_for('auth.iniciar_sesion'))
        
        # Variables para artículos incompletos (solo para super_usuario)
        cantidad_articulos_incompletos = 0
        lista_articulos_incompletos = []
        es_super_usuario = False
        
        # Verificar si es super_usuario
        if g.user and g.user.super_usuario == 'SI':
            es_super_usuario = True
            db = SessionLocal()
            try:
                # Obtener artículos incompletos del sistema
                articulos_incompletos = (
                    db.query(modelo.Articulo)
                    .filter(
                        modelo.Articulo.DESCRIPCION == 'Sin descripción',
                        (
                            modelo.Articulo.CATEGORIA_1.in_(['ND_1', 'ND']) |
                            modelo.Articulo.CATEGORIA_2.in_(['ND_2', 'ND'])
                        )
                    )
                    .distinct()
                    .all()
                )
                cantidad_articulos_incompletos = len(articulos_incompletos)
                lista_articulos_incompletos = [art.ARTICULO for art in articulos_incompletos]
            except Exception:
                pass
            finally:
                db.close()
        
        return render_template(
            'inicio.html',
            es_super_usuario=es_super_usuario,
            cantidad_articulos_incompletos=cantidad_articulos_incompletos,
            lista_articulos_incompletos=lista_articulos_incompletos
        )
    
    # Centralizamos la creación de un sesión de base de datos para todas las rutas
    @app.before_request
    def create_session():
        request.db = SessionLocal()

    # Al momento de terminar la petición, cerramos la sesión de base de datos.
    @app.teardown_request
    def remove_session(exception=None):
        db: Session = getattr(request, 'db', None)
        if db is not None:
            try:
                if exception:
                    db.rollback()
                else:
                    db.commit()
            finally:
                db.close()

    from . import auth
    app.register_blueprint(auth.bp)

    from . import administracion_bp
    app.register_blueprint(administracion_bp.bp)

    from . import usuario_bp
    app.register_blueprint(usuario_bp.bp)

    from . import categoria_bp
    app.register_blueprint(categoria_bp.bp)

    from . import articulo_bp
    app.register_blueprint(articulo_bp.bp)

    from . import estado_bp
    app.register_blueprint(estado_bp.bp)

    from . import ubicacion_bp
    app.register_blueprint(ubicacion_bp.bp)

    from . import almacen_bp
    app.register_blueprint(almacen_bp.bp)

    from . import existencia_bp
    app.register_blueprint(existencia_bp.bp)

    from . import planificacion_bp
    app.register_blueprint(planificacion_bp.bp)

    from . import inventario_bp
    app.register_blueprint(inventario_bp.bp)

    from . import historial_bp
    app.register_blueprint(historial_bp.bp)

    from . import reporte_bp
    app.register_blueprint(reporte_bp.bp)

    @app.template_filter()
    def redondear(value):
        return round(float(value),3)

    @app.template_filter()
    def b64encode(value):
        return base64.b64encode(value).decode('utf-8')
        
    @app.template_filter()
    def formatoMonto(valor):
        return ("$"+str(round(float(valor),3)))

    @app.template_filter()
    def formatoMonto(valor):
        return ("$"+str(round(float(valor),3)))

    @app.template_filter()
    def dos_decimales(value):
        value = '{:.3f}'.format(float(value))
        return (value)

    @app.template_filter()
    def ajusta_largo(value):
        if(len(value)> 30):
            return value[0: 27: 1] + "..."
        return value
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Error 500: {error}')
        return render_template('500.html'), 500
    
    @app.teardown_appcontext
    def close_db_session(exception=None):
        db = getattr(g, 'db_session', None)
        if db is not None:
            db.close()

    @app.context_processor
    def area():
        def validar_area(rol_valido, usuario):
            """
            Verifica si el usuario tiene el rol válido proporcionado.
            :param rol_valido: Rol válido (por ejemplo, 'nivel_1').
            :param usuario: Nombre del usuario.
            :return: True si el usuario tiene el rol válido, False en caso contrario.
            """
            # Convertir el rol válido a minúsculas para evitar problemas de mayúsculas/minúsculas
            rol_valido = rol_valido.lower()

            # Verificar si los roles ya están en la sesión
            if 'roles' in session:
                print("validar_area ::: obteniendo roles de la sesión")
                user_roles = session['roles']
            elif hasattr(g, 'roles'):
                # Si los roles están en g, reutilizarlos
                print("validar_area ::: obteniendo roles de cache en g")
                user_roles = g.roles
            else:
                # Si no están en la sesión ni en g, consultar la base de datos
                print(f"validar_area ::: consultando roles en la base de datos para el usuario '{usuario}'")
                db = SessionLocal()
                try:
                    # Consultar todos los roles del usuario desde la base de datos
                    query = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == usuario)
                    print("SQL validar_area: ")
                    print(query.statement.compile(compile_kwargs={"literal_binds": True}))
                    usuario_db = query.first()
                    if not usuario_db:
                        return False

                    # Cargar los roles del usuario en un diccionario
                    user_roles = {
                        "super_usuario": usuario_db.super_usuario,
                        "nivel_1": usuario_db.nivel_1,
                        "nivel_2": usuario_db.nivel_2,
                        "nivel_3": usuario_db.nivel_3,
                        "nivel_4": usuario_db.nivel_4,
                        "nivel_5": usuario_db.nivel_5,
                    }
                    print("Roles for user", usuario, ":", user_roles)
                    # Almacenar los roles en la sesión y en g para futuras solicitudes
                    session['roles'] = user_roles
                    g.roles = user_roles
                finally:
                    db.commit()
                    db.close()  # Asegurarse de cerrar la conexión a la base de datos

            # Verificar si el usuario tiene el rol válido
            return user_roles.get(rol_valido) == 'SI'

        return dict(validar_area=validar_area)
    
    return app

