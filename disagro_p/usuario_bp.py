import json
import datetime 
from datetime import date
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
from flask.helpers import make_response
from werkzeug.exceptions import abort
from disagro_i.auth import requiere_login, role_required
# from disagro_i.clases import ( caja as class_caja, pedido as class_pedido, tienda as class_tienda)
import os
import csv
from io import TextIOWrapper

import sys
from disagro_i.clases import modelo
from disagro_i.error_reporter import ErrorReporter
from disagro_i.conexion_orm import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import asc,desc,update,func,and_
import requests 
import datetime
import time
import base64
import json
import csv
from sqlalchemy.exc import SQLAlchemyError
import random
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import g, abort

bp = Blueprint('usuario', __name__, url_prefix='/usuario')

@bp.route("/configuracion",methods=['GET'])
@requiere_login
@role_required(['super_usuario'])  
def configurar_tienda():
    try:
        db: Session = request.db
        
        """La diferencia es que db.query(modelo.Usuario) forma parte de la interfaz del ORM, la cual utiliza la información del mapeo (registrada con mapper_registry.map_imperatively) para construir consultas SQL.
        Cuando haces db.query(modelo.Usuario), la sesión conoce cómo transformar la clase Usuario mapeada en una consulta, aunque Usuario en sí no tenga un método select(). Por otro lado, el método select() pertenece al objeto Table (modelo.usuario), que es parte del SQL Expression Language de SQLAlchemy.
        En resumen, el ORM proporciona una abstracción (db.query) que funciona a partir del mapeo de clases, mientras que select() es una función a nivel de tabla en el SQL Expression Language."""
        usuarios = db.execute(modelo.usuario.select().order_by(asc(modelo.usuario.c.nombre))).fetchall()
        
        bitacora = db.query(modelo.Bitacora).filter(
        modelo.Bitacora.TABLA == 'usuario',
        modelo.Bitacora.ACCION == 'ACTUALZIAR_MAESTRO'
        ).order_by(modelo.Bitacora.FECHA_REGISTRO.desc()).first()

        print(bitacora)
        return render_template("usuario/config_usuarios.html",usuario = g.user.usuario,usuarios=usuarios, bitacora=bitacora)
    finally:
        db.close()

@bp.route('/upload/usuarios', methods=['POST'])
@requiere_login
@role_required(['super_usuario']) 
def crear_usuarios():
    if 'archivo' not in request.files:
        print('No file part')
        respuesta = {"mensaje":"No hay archivo","error":True}
        return make_response(jsonify(respuesta), 400)

    archivo = request.files['archivo']

    if not archivo.filename.endswith('.csv'):
        print('Archivo no permitido')
        respuesta = {"mensaje":"Archivo no permitido, solo se permiten archivos .csv","error":True}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(archivo, encoding='utf-8')
        csv_data = csv.reader(file,delimiter=';')
        
        # Debug: mostrar contenido del CSV
        print("\n[DEBUG CSV UPLOAD] Iniciando carga de CSV")
        csv_data_list = list(csv_data)
        print(f"[DEBUG CSV UPLOAD] Total de líneas: {len(csv_data_list)}")
        if csv_data_list:
            print(f"[DEBUG CSV UPLOAD] Header: {csv_data_list[0]}")
            for idx, line in enumerate(csv_data_list[1:], 1):
                print(f"[DEBUG CSV UPLOAD] Fila {idx}: {line}")
        
        # Saltar el header
        if csv_data_list:
            csv_data_list = csv_data_list[1:]
        
        db: Session = request.db

        csv_data = procesar_csv_data(csv_data_list)
        print(csv_data)

        for row in csv_data:
            count_value = db.query(func.count(modelo.Usuario.id_usuario)).filter(modelo.Usuario.usuario == row[0]).scalar()
            if count_value and count_value > 0:
                row[0] = f"{row[0]}_{count_value+1}"
                
            contrasena_hash = generate_password_hash(row[0])
            nuevo_usuario = modelo.Usuario(
                usuario=row[0],
                contrasena=contrasena_hash,
                nombre=row[1],
                super_usuario=row[2],
                nivel_1=row[3],
                nivel_2=row[4],
                nivel_3=row[5],
                nivel_4=row[6],
                nivel_5=row[7],
                pais=row[8]
            )
            db.add(nuevo_usuario)
        bitacora = modelo.Bitacora(ID_USUARIO = g.user.usuario, ACCION = 'ACTUALZIAR_MAESTRO',TABLA = 'usuario',DETALLES = 'Actualziación de maestro de usuario.')
        db.add(bitacora)
        db.commit()
        respuesta = {"mensaje":"Usuarios creados correctamente","error":False}
        return make_response(jsonify(respuesta), 200)
    except Exception as err:
        db.rollback()
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()

def procesar_csv_data(csv_data):
    print(f"\n[DEBUG PROCESAR_CSV] Iniciando procesamiento de {len(csv_data)} filas")
    new_csv_data = []
    username_tracker = {}  
    for idx, row in enumerate(csv_data, 1):
        print(f"\n[DEBUG PROCESAR_CSV] Procesando fila {idx}:")
        print(f"[DEBUG PROCESAR_CSV]   - Datos completos: {row}")
        print(f"[DEBUG PROCESAR_CSV]   - Cantidad de columnas: {len(row)}")
        if len(row) > 1:
            print(f"[DEBUG PROCESAR_CSV]   - NOMBRES (columna 1): '{row[1]}'")
        base_username = generate_user_name(row[1])
        if base_username in username_tracker:
            username_tracker[base_username] += 1
            username_uni = f"{base_username}_{username_tracker[base_username]}"
        else:
            username_tracker[base_username] = 0
            username_uni = base_username
        
        row[0] = username_uni
        new_csv_data.append(row)
    
    return new_csv_data

@bp.route("/detalle/<id>",methods=['GET'])
@requiere_login
def configurar_usuario(id):
    try:
        db: Session = request.db
        usuario_detalle = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == id).first()
        if g.user.usuario != id:
            flash("No puedes modificar la contraseña de otro usuario.")
            return redirect(url_for('inicio',usuario=id))
        return render_template("usuario/detalle_usuario.html",usuario_detalle=usuario_detalle)
    finally:
        db.close()


@bp.route("/actualizar_contrasena", methods=['POST'])
@requiere_login
def actualizar_contrasena():
    db: Session = request.db
    # Obtener el username y la nueva contraseña enviados desde el formulario
    username = request.form.get("usuario")
    nueva_contrasena = request.form.get("contrasena")
    print(username)
    print(nueva_contrasena)
    # Si se requiere validar que el usuario exista, se puede hacer aquí
    if not username or not nueva_contrasena:
        flash("Faltan datos para actualizar la contraseña.")
        return redirect(url_for('usuario.configurar_usuario',id=g.user[1]))
    
    if g.user.usuario != username:
        flash("No puedes modificar la contraseña de otro usuario.")
        return redirect(url_for('usuario.configurar_usuario',id=g.user[1]))
    
    try:
        # Generar el hash de la nueva contraseña
        contrasena_hash = generate_password_hash(nueva_contrasena)
        # Actualizar la contraseña del usuario
        db.query(modelo.Usuario).filter(modelo.Usuario.usuario == username).update({modelo.Usuario.contrasena: contrasena_hash})
        db.commit()
        flash("Contraseña actualizada exitosamente.")
        return redirect(url_for('usuario.configurar_usuario',id=g.user.usuario))
    except Exception as err:
        db.rollback()
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        flash("Error al actualizar la contraseña.")
        return redirect(url_for('usuario.configurar_usuario',id=g.user.usuario))
    finally:
        db.close()

@bp.route("/eliminar/<id>",methods=['POST'])
@requiere_login
@role_required(['super_usuario']) 
def eliminar_descuento(id):
    db: Session = request.db
    print(id)
    try:
        user_to_delete = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == id).first()
        if user_to_delete and user_to_delete.super_usuario == 'SI':
            flash("No se puede eliminar el super usuario.")
            return redirect(url_for('usuario.configurar_tienda'))
        db.query(modelo.Usuario).filter(modelo.Usuario.usuario == id).delete()
        db.commit()
        flash("Usuario eliminado exitosamente.")
        return redirect(url_for('usuario.configurar_tienda'))
    except Exception as err:
        db.rollback()
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return redirect(url_for('usuario.configurar_tienda'))
    finally:
        db.close()
    
@bp.route("/restablecer_contrasena/<id>",methods=['POST'])
@requiere_login
@role_required(['super_usuario'])
def restablecer_contrasena(id):
    db: Session = request.db
    print(id)
    try:
        contrasena_hash = generate_password_hash(id)
        db.query(modelo.Usuario).filter(modelo.Usuario.usuario == id).update({modelo.Usuario.contrasena: contrasena_hash})
        db.commit()
        flash("Contraseña restablecida exitosamente.")
        return redirect(url_for('usuario.configurar_tienda'))
    except Exception as err:
        db.rollback()
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return redirect(url_for('usuario.configurar_tienda'))
    finally:
        db.close()

def validar_si_existe_todas(tabla,agrupacion):
    db: Session = request.db
    print(tabla,agrupacion)
    if tabla == 'CATEGORIA' and agrupacion == '1':
        existe_todas = db.query(modelo.Planificacion).filter(modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == tabla,modelo.Planificacion_linea.VALOR_FILTRO == 'TODAS_1').first()
    elif tabla == 'CATEGORIA' and agrupacion == '2':
        existe_todas = db.query(modelo.Planificacion).filter(modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == tabla,modelo.Planificacion_linea.VALOR_FILTRO == 'TODAS_2').first()
    else:
        existe_todas = db.query(modelo.Planificacion).filter(modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == tabla,modelo.Planificacion_linea.VALOR_FILTRO == 'TODAS').first()

    print(existe_todas)
    if existe_todas:
        return True
    return False 

@bp.route('/<usuario>', methods=['GET'])
@requiere_login
@role_required(['super_usuario']) 
def obtener_usuario(usuario):
    try:
        db: Session = request.db
        usuario_detalle = db.execute(modelo.usuario.select().where(modelo.usuario.c.usuario == usuario)).fetchone()
        print(usuario_detalle)
        return render_template("usuario/usuario.html",usuario = g.user.usuario,usuario_detalle=usuario_detalle)
    finally:
        db.close()

@bp.route('/<usuario>', methods=['POST'])
@requiere_login
@role_required(['super_usuario']) 
def actualizar_usuario(usuario):
    try:
        json_data = request.get_json()
        super_usuario = json_data.get('super_usuario')
        nivel_1 = json_data.get('nivel_1')
        nivel_2 = json_data.get('nivel_2')
        nivel_3 = json_data.get('nivel_3')
        nivel_4 = json_data.get('nivel_4')
        nivel_5 = json_data.get('nivel_5')

        db: Session = request.db
        usuario_db = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == usuario).first()

        if usuario_db:
            if nivel_1:
                usuario_db.nivel_1 = 'SI'
            else:
                usuario_db.nivel_1 = 'NO'

            if nivel_2:
                usuario_db.nivel_2 = 'SI'
            else:
                usuario_db.nivel_2 = 'NO'

            if nivel_3:
                usuario_db.nivel_3 = 'SI'
            else:
                usuario_db.nivel_3 = 'NO'
            if nivel_4:
                usuario_db.nivel_4 = 'SI'
            else:
                usuario_db.nivel_4 = 'NO'
            if nivel_5:
                usuario_db.nivel_5 = 'SI'
            else:
                usuario_db.nivel_5 = 'NO'
            if super_usuario:
                usuario_db.super_usuario = 'SI'
            else:
                usuario_db.super_usuario = 'NO'
        db.commit()
    except Exception as err:
        db.rollback()
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()

    return make_response(jsonify({"mensaje": "La operación se realizó con exito.", "error": False}), 200)

def generate_user_name(full_name):
    print(f"\n[DEBUG GENERATE_USER] Input recibido: '{full_name}'")
    print(f"[DEBUG GENERATE_USER] Tipo: {type(full_name)}, Longitud: {len(full_name) if full_name else 0}")
    
    words = full_name.split()
    print(f"[DEBUG GENERATE_USER] Palabras después de split: {words}")
    print(f"[DEBUG GENERATE_USER] Cantidad de palabras: {len(words)}")
    
    if len(words) < 2:
        error_msg = f"El nombre completo debe contener al menos dos palabras. Recibido: '{full_name}' (palabras: {words})"
        print(f"[DEBUG GENERATE_USER] ERROR: {error_msg}")
        raise ValueError(error_msg)
    if len(words) >= 3:
        user_name = words[0][0] + words[1] + words[2][0]
    else:
        user_name = words[0][0] + words[1]
    return user_name.lower()