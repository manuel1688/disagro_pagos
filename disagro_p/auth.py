import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from flask.helpers import make_response
from flask.json import jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from disagro_i.clases import modelo
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from disagro_i.conexion_orm import SessionLocal

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def iniciar_sesion():
    if request.method == 'POST':
        print("LOGIN ...")
        a_usuario = request.form['usuario']
        a_contrasena = request.form['contrasena']
        error = None
        db: Session = request.db
        try:
            query = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == a_usuario)
            print("SQL: ")
            print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            usuario = query.first()
            if usuario is None:
                flash('Usuario o contraseña incorrectos.')
                return redirect(url_for('auth.iniciar_sesion')) 
            contrasena = usuario.contrasena 
            if usuario is None:
                error = 'Usuario incorrecto.'
            elif not check_password_hash(contrasena, a_contrasena):
                error = 'Contraseña incorrecta.'

            if error is None:
                # Preparar la lista de roles del usuario
                print("iniciar_sesion ::: definicion de roles en la sesion")
                roles = {
                    "super_usuario": usuario.super_usuario,
                    "nivel_1": usuario.nivel_1,
                    "nivel_2": usuario.nivel_2,
                    "nivel_3": usuario.nivel_3,
                    "nivel_4": usuario.nivel_4,
                    "nivel_5": usuario.nivel_5,
                }
                # Almacenar los roles en la sesión
                session.clear()
                session['id_usuario'] = usuario.id_usuario
                session['roles'] = roles  # Guardar los roles en la sesión
                return redirect(url_for('inicio', usuario=usuario))

            flash(error)
        finally:
            db.close()  # Cierra la conexión a la base de datos
    return render_template('auth/login.html')

#Este metodo se ejecuta antes de cada request
@bp.before_app_request
def cargar_usuario_logged():
    ID_USUARIO = session.get('id_usuario')
    if ID_USUARIO is None:
        g.user = None
    else:
        db: Session = request.db
        try:
            usuario = db.query(modelo.Usuario).filter(modelo.Usuario.id_usuario == ID_USUARIO).first()
            g.user = usuario
        finally:
            db.close()  # Cierra la conexión a la base de datos
        
@bp.route('/logout')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('index'))

def requiere_login(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.iniciar_sesion'))
        return view(**kwargs)
    return wrapped_view
 
def role_required(roles):
    def decorator(f): 
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si los roles ya están en la sesión
            if 'roles' not in session:
                # Si no están en la sesión, buscarlos en la base de datos
                db: Session = request.db
                try:
                    query = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == g.user.usuario)
                    print("role_required::: SQL role_required: ")
                    print(query.statement.compile(compile_kwargs={"literal_binds": True}))
                    usuario = query.first()
                    if usuario is None:
                        abort(403)
                    # Cargar los roles del usuario desde la base de datos
                    roles_db = {
                        "super_usuario": usuario.super_usuario,
                        "nivel_1": usuario.nivel_1,
                        "nivel_2": usuario.nivel_2,
                        "nivel_3": usuario.nivel_3,
                        "nivel_4": usuario.nivel_4,
                        "nivel_5": usuario.nivel_5,
                    }
                    # Almacenar los roles en la sesión
                    session['roles'] = roles_db
                finally:
                    db.close()  # Cierra la conexión a la base de datos
            else:
                # Si ya están en la sesión, no es necesario volver a consultarlos
                print("role_required ::: obteniendo roles de la sesión")

            # Obtener los roles desde la sesión
            user_roles = session['roles']

            # Verificar si el usuario tiene al menos uno de los roles requeridos
            condiciones_roles = [user_roles.get(rol) == 'SI' for rol in roles]
            if not any(condiciones_roles):
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator