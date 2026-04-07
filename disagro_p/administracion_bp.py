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
from disagro_i.clases.utils import Utils
from disagro_i.conexion_orm import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import asc,desc,update,func
import requests 
import datetime
import time
import base64
import json
import csv
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('adminitracion', __name__, url_prefix='/admin')

def obtener_paises_filtrados(db):
    util = Utils()
    pais = util.obtener_pais(db, g)
    try:
        if pais == "TODOS":
            # Obtener todos los países únicos de los usuarios, excluyendo "TODOS"
            paises = [p[0] for p in db.query(modelo.Usuario.pais).distinct().all() if p[0] != "TODOS"]
        else:
            # Crear una lista con el país específico
            paises = [pais]  # Convierte el pais en una lista para uniformidad.
        return paises
    finally:
        db.close()

@bp.route("/maestros",methods=['GET'])
@requiere_login
@role_required(['nivel_1','super_usuario'])
def configurar_tienda():
    try:
        db: Session = request.db
        categoria_1 = db.query(modelo.MaestroUpload).filter_by(MAESTRO="CATEGORIA_1").first()
        categoria_2 = db.query(modelo.MaestroUpload).filter_by(MAESTRO="CATEGORIA_2").first()
        articulos = db.query(modelo.MaestroUpload).filter_by(MAESTRO="ARTICULOS").first()
        estado = db.query(modelo.MaestroUpload).filter_by(MAESTRO="ESTADO").first()

        util = Utils()
        pais = util.obtener_pais(db, g)
        ubicacion = db.query(modelo.MaestroUpload).filter_by(MAESTRO="UBICACION").first()
        almacen = db.query(modelo.MaestroUpload).filter_by(MAESTRO="ALMACEN").first()
        print("almacen")
        print(almacen)
        paises = obtener_paises_filtrados(db)
        print(paises)
        return render_template("administracion/config_maestros.html",usuario = g.user.usuario,categoria_1=categoria_1
        ,categoria_2=categoria_2,articulos=articulos,estado=estado,ubicacion=ubicacion,almacen=almacen,paises=paises,pais=pais)
    finally:
        db.close()

@bp.route("/upload/categoria/<agrupacion>", methods=['POST'])
@requiere_login
@role_required(['super_usuario']) 
def subir_categoria_1(agrupacion):

    """
    Este endpoint permite subir un archivo CSV con las categorias y sus descripciones.
    pero primero valida las categorias que ya fueron enlazadas a un articulo
    y muestra un mensaje de error si alguna categoria ya fue enlazada a un articulo,
    luego elimina todas las categorias de la tabla y agrega las nuevas categorias.
    BUG 001 Hay un bug que no permite actualizar las categorias despues de haberlas enlazado a un articulo.
    """

    # Check if a file was uploaded
    if 'archivo' not in request.files:
        print("No se ha subido ningun archivo")
        respuesta = {"mensaje":"No se ha subido ningun archivo"}
        return make_response(jsonify(respuesta), 400)

    file = request.files['archivo']

    # Check if the file has a CSV extension
    if not file.filename.endswith('.csv'):
        print("Formato de archivo invalido. Solo se permiten archivos CSV")
        respuesta = {"mensaje":"Formato de archivo invalido. Solo se permiten archivos CSV"}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(file, encoding='utf-8')
        csv_data = list(csv.reader(file, delimiter=';'))
        header = csv_data.pop(0) 
        db: Session = request.db
        # Limpiar la tabla antes de agregar nuevos registros

        #esto busca si la categoria ya fue enlazada a un articulo
        if agrupacion == "1":
            categorias_relacionadas = db.query(modelo.Articulo.CATEGORIA_1) \
        .join(modelo.Categoria,modelo.Articulo.CATEGORIA_1 == modelo.Categoria.CATEGORIA) \
        .filter(modelo.Categoria.AGRUPACION == agrupacion).distinct().all()
        else:
            categorias_relacionadas = db.query(modelo.Articulo.CATEGORIA_2) \
        .join(modelo.Categoria,modelo.Articulo.CATEGORIA_2 == modelo.Categoria.CATEGORIA) \
        .filter(modelo.Categoria.AGRUPACION == agrupacion).distinct().all()

        #categorias_relacionadas es una lista de las categorias que ya fueron enlazadas a un articulo
        #csv_data es el archivo subido con las categorias
        #este metodo retorna una lista de las categorias que no estan en el archivo subido
        categorias_faltantes = validar_categorias(categorias_relacionadas,csv_data)

        if categorias_faltantes.__len__() > 0:
            string_de_categorias = ", ".join([f"{cat[0]}" for cat in categorias_faltantes])
            respuesta = {"mensaje": f"La siguiente(s) categoría(s) fueron enlazadas con artículo(s) previamente y no estan en este archivo: [{string_de_categorias}]. \n\nDEBES LIMPIAR el maestro de ARTÍCULOS antes de actualizar la categorias {agrupacion}.","error":True}
            return make_response(jsonify(respuesta), 400)

        db.query(modelo.Categoria).filter_by(AGRUPACION=agrupacion).delete()
        print("csv_data")
        print(csv_data)
        # query_pais = db.query(modelo.Usuario.pais).filter(modelo.Usuario.usuario == g.user[1]).first()
        # print("PAIS")
        # pais = query_pais.pais
        # print(pais)
        
        for row in csv_data:
            print(row)
            if row[0] != "" and row[1] != "":
                print(row)
                nueva_categoria = modelo.Categoria(
                    CATEGORIA= f"{row[0]}",
                    DESCRIPCION=row[1],
                    AGRUPACION=agrupacion
                )
                db.add(nueva_categoria)

        categoria_todas = modelo.Categoria(
            CATEGORIA= f"TODAS_{agrupacion}",
            DESCRIPCION="TODAS",
            AGRUPACION=agrupacion
        )
        db.add(categoria_todas)  

        db.query(modelo.MaestroUpload).filter_by(MAESTRO=f"CATEGORIA_{agrupacion}").delete()
        nueva_subida = modelo.MaestroUpload(
                MAESTRO=f"CATEGORIA_{agrupacion}",
                ULTIMA_SUBIDA=datetime.datetime.now(),
                PAIS = "TODOS"
            )
        db.add(nueva_subida)
        db.commit()
    
    except SQLAlchemyError as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err),"error":True}), 500)
    except Exception as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 500)
    finally:
        db.close()

    respuesta = {"mensaje":"Archivo subido exitosamente"}
    return make_response(jsonify(respuesta), 200)

#categorias_relacionadas es una lista de las categorias que ya fueron enlazadas a un articulo
#csv_data es el archivo subido con las categorias
def validar_categorias(categorias_relacionadas, csv_data):

    #aqui se obtiene la lista de categorias del archivo subido
    categorias_csv = set(row[0] for row in csv_data)
    categorias_faltantes = []

    for categoria in categorias_relacionadas:
        print(categoria)
        if categoria[0] not in categorias_csv:
            categorias_faltantes.append(categoria)
    return categorias_faltantes

@bp.route("/upload/articulos", methods=['POST'])
@requiere_login
@role_required(['super_usuario'])
def subir_articulos():

    if 'archivo' not in request.files:
        print("No se ha subido ningun archivo")
        respuesta = {"mensaje":"No se ha subido ningun archivo"}
        return make_response(jsonify(respuesta), 400)

    file = request.files['archivo']

    if not file.filename.endswith('.csv'):
        print("Formato de archivo invalido. Solo se permiten archivos CSV")
        respuesta = {"mensaje":"Formato de archivo invalido. Solo se permiten archivos CSV"}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(file, encoding='utf-8')
        csv_data = csv.reader(file,delimiter=';')
        next(csv_data)
        db: Session = request.db

        #BUG hay que validar si hay articulos relacionados
        #TODO: validar si es necesario limpiar la tabla antes de agregar nuevos registros
        # db.query(modelo.Existencia).delete()
        db.query(modelo.Articulo).delete()
        for row in csv_data:
            if row[0] != "" and row[1] != "":
                nuevo_articulo = modelo.Articulo(
                    ARTICULO=row[0],
                    DESCRIPCION=row[1],
                    CATEGORIA_1=row[2],
                    CATEGORIA_2=row[3]
                )
                db.add(nuevo_articulo)

        db.query(modelo.MaestroUpload).filter_by(MAESTRO="ARTICULOS").delete()
        # db.query(modelo.MaestroUpload).filter_by(MAESTRO="EXISTENCIAS").delete()
        nueva_subida = modelo.MaestroUpload(
                MAESTRO="ARTICULOS",
                ULTIMA_SUBIDA=datetime.datetime.now(),
                PAIS = "TODOS"
            )
        db.add(nueva_subida)
        db.commit()

    except SQLAlchemyError as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err),"error":True}), 500)
        
    except Exception as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje":"Error en la base de datos"}), 500)
    finally:
        db.close()

    respuesta = {"mensaje":"Archivo subido exitosamente"}
    return make_response(jsonify(respuesta), 200)

def print_error_info(err, exception_type, filename, line_number):
    print("ERROR: ", err)
    print("Exception type: ", exception_type)
    print(f"File {filename}, line {line_number}")

@bp.route("/upload/estado", methods=['POST'])
@requiere_login
@role_required(['super_usuario'])
def subir_estado():
    # Check if a file was uploaded
    if 'archivo' not in request.files:
        print("No se ha subido ningun archivo")
        respuesta = {"mensaje":"No se ha subido ningun archivo"}
        return make_response(jsonify(respuesta), 400)

    file = request.files['archivo']

    # Check if the file has a CSV extension
    if not file.filename.endswith('.csv'):
        print("Formato de archivo invalido. Solo se permiten archivos CSV")
        respuesta = {"mensaje":"Formato de archivo invalido. Solo se permiten archivos CSV"}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(file, encoding='utf-8')
        csv_data = csv.reader(file,delimiter=';')
        next(csv_data)
        db = SessionLocal()

        #BUG hay que validar si hay estados relacionados a articulos y solo eliminar los que no esten relacionados y agregar los nuevos
        # Limpiar la tabla antes de agregar nuevos registros
        db.query(modelo.Estado).delete()
        for row in csv_data:
            if row[0] != "" and row[1] != "":
                nuevo_estado = modelo.Estado(
                    ESTADO=row[0],
                    DESCRIPCION=row[1]
                )
                db.add(nuevo_estado)

        db.query(modelo.MaestroUpload).filter_by(MAESTRO="ESTADO").delete()
        nueva_subida = modelo.MaestroUpload(
                MAESTRO="ESTADO",
                ULTIMA_SUBIDA=datetime.datetime.now(),
                PAIS = "TODOS"
            )
        db.add(nueva_subida)
        db.commit()
        
    except SQLAlchemyError as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err),"error":True}), 500)

    except Exception as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje":err}), 200)
    finally:
        db.close()

    respuesta = {"mensaje":"Archivo subido exitosamente","error":False}
    return make_response(jsonify(respuesta), 200)

@bp.route("/upload/ubicacion", methods=['POST'])
@requiere_login
@role_required(['super_usuario'])
def subir_ubicacion():
    # Check if a file was uploaded
    if 'archivo' not in request.files:
        print("No se ha subido ningun archivo")
        respuesta = {"mensaje":"No se ha subido ningun archivo"}
        return make_response(jsonify(respuesta), 400)

    file = request.files['archivo']

    # Check if the file has a CSV extension
    if not file.filename.endswith('.csv'):
        print("Formato de archivo invalido. Solo se permiten archivos CSV")
        respuesta = {"mensaje":"Formato de archivo invalido. Solo se permiten archivos CSV"}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(file, encoding='utf-8')
        csv_data = csv.reader(file,delimiter=';')
        next(csv_data)
        db = SessionLocal()
        # Limpiar la tabla antes de agregar nuevos registros
        util = Utils()
        pais = util.obtener_pais(db, g)

        #BUG hay que validar si hay ubicaciones relacionadas a articulos y solo eliminar los que no esten relacionados y agregar los nuevos
        for row in csv_data:
            if row[0] != "" and row[1] != "":
                # Verificar si la ubicación ya existe
                ubicacion_existente = db.query(modelo.Ubicacion).filter(
                    modelo.Ubicacion.UBICACION == row[0]
                ).first()

                # Si no existe, agregarla
                if not ubicacion_existente:
                    nueva_ubicacion = modelo.Ubicacion(
                        UBICACION=row[0],
                        DESCRIPCION=row[1],
                        PAIS="TODOS"
                    )
                    db.add(nueva_ubicacion)

        # Verificar si la ubicación "TODAS_{pais}" ya existe
        ubicacion_todas_existente = db.query(modelo.Ubicacion).filter(
            modelo.Ubicacion.UBICACION == "TODAS",
            modelo.Ubicacion.DESCRIPCION == "TODAS",
            modelo.Ubicacion.PAIS == pais
        ).first()

        # Si no existe, agregarla
        if not ubicacion_todas_existente:
            ubicacion_todas = modelo.Ubicacion(
                UBICACION="TODAS",
                DESCRIPCION="TODAS",
                PAIS=pais
            )
            db.add(ubicacion_todas)

        db.query(modelo.MaestroUpload).filter(
            modelo.MaestroUpload.MAESTRO == "UBICACION",
            modelo.MaestroUpload.PAIS == pais  # Agregar la condición del país
        ).delete()
        nueva_subida = modelo.MaestroUpload(
                MAESTRO="UBICACION",
                ULTIMA_SUBIDA=datetime.datetime.now(),
                PAIS = pais
            )
        db.add(nueva_subida)
        db.commit()
        
    except SQLAlchemyError as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err),"error":True}), 500)

    except Exception as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje":err}), 200)
    finally:
        db.close()

    respuesta = {"mensaje":"Archivo subido exitosamente"}
    return make_response(jsonify(respuesta), 200)

@bp.route("/upload/almacen", methods=['POST'])
@requiere_login
@role_required(['super_usuario'])
def subir_almacen():
    # Check if a file was uploaded
    if 'archivo' not in request.files:
        print("No se ha subido ningun archivo")
        respuesta = {"mensaje":"No se ha subido ningun archivo"}
        return make_response(jsonify(respuesta), 400)

    file = request.files['archivo']

    # Check if the file has a CSV extension
    if not file.filename.endswith('.csv'):
        print("Formato de archivo invalido. Solo se permiten archivos CSV")
        respuesta = {"mensaje":"Formato de archivo invalido. Solo se permiten archivos CSV"}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(file, encoding='utf-8')
        csv_data = csv.reader(file,delimiter=';')
        next(csv_data)
        db = SessionLocal()
        # Limpiar la tabla antes de agregar nuevos registros
        util = Utils()
        pais = util.obtener_pais(db, g)
        #BUG hay que validar si hay almacenes relacionados a articulos y solo eliminar los que no esten relacionados y agregar los nuevos
        for row in csv_data:
            if row[0] != "" and row[1] != "":
                # Verificar si el almacen ya existe
                almacen_existente = db.query(modelo.Almacen).filter(
                    modelo.Almacen.ALMACEN == row[0]
                ).first()

                # Si no existe, agregarlo
                if not almacen_existente:
                    nuevo_almacen = modelo.Almacen(
                        ALMACEN=row[0],
                        DESCRIPCION=row[1],
                        PAIS="TODOS"
                    )
                    db.add(nuevo_almacen)

        # Verificar si el almacen "TODOS_{pais}" ya existe
        almacen_todas_existente = db.query(modelo.Almacen).filter(
            modelo.Almacen.ALMACEN == "TODAS",
            modelo.Almacen.DESCRIPCION == "TODAS"
        ).first()

        # Si no existe, agregarlo
        if not almacen_todas_existente:
            almacen_todas = modelo.Almacen(
                ALMACEN="TODAS",
                DESCRIPCION="TODAS",
                PAIS=pais  # Asignar el país específico
            )
            db.add(almacen_todas)

        db.query(modelo.MaestroUpload).filter(
            modelo.MaestroUpload.MAESTRO == "ALMACEN",
            modelo.MaestroUpload.PAIS == pais  # Agregar la condición del país
        ).delete()
        nueva_subida = modelo.MaestroUpload(
                MAESTRO="ALMACEN",
                ULTIMA_SUBIDA=datetime.datetime.now(),
                PAIS = pais
            )
        db.add(nueva_subida)
        db.commit()
        
    except SQLAlchemyError as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err),"error":True}), 500)

    except Exception as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje":err}), 200)
    finally:
        db.close()

    respuesta = {"mensaje":"Archivo subido exitosamente"}
    return make_response(jsonify(respuesta), 200)

@bp.route("/upload/limpiar", methods=['DELETE'])
@requiere_login
def limpiar_maestro():
    db = SessionLocal()
    try:
        json_data = request.get_json()
        
        # Verificar si json_data es un diccionario
        if not isinstance(json_data, dict):
            raise TypeError("El JSON recibido no es un diccionario")
        
        print(json_data)
        tabla = json_data.get('TABLA')
        
        if not tabla:
            raise ValueError("La clave 'TABLA' no está presente en el JSON")
        
        if tabla == "ARTICULOS":
            db.query(modelo.Existencia).delete()
            db.query(modelo.Articulo).delete()
            db.query(modelo.MaestroUpload).filter_by(MAESTRO="ARTICULOS").delete()
            db.query(modelo.MaestroUpload).filter_by(MAESTRO="EXISTENCIAS").delete()
            db.commit()
        elif tabla == "EXISTENCIAS":
            db.query(modelo.Existencia).delete()
            db.query(modelo.MaestroUpload).filter_by(MAESTRO="EXISTENCIAS").delete()
            db.query(modelo.Planificacion).delete()
            db.commit()
        else:
            raise ValueError(f"Valor de 'TABLA' no válido: {tabla}")
    
    except SQLAlchemyError as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err), "error": True}), 500)
    
    except (TypeError, ValueError) as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        return make_response(jsonify({"mensaje": str(err), "error": True}), 400)
    
    except Exception as err:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print_error_info(err, exception_type, filename, line_number)
        db.rollback()
        return make_response(jsonify({"mensaje": str(err), "error": True}), 500)
    finally:
        db.close()
    
    respuesta = {"mensaje": "Maestro limpiado exitosamente", "error": False}
    return make_response(jsonify(respuesta), 200)

def print_error_info(err, exception_type, filename, line_number):
    print("ERROR: ", err)
    print("Exception type: ", exception_type)
    print(f"File {filename}, line {line_number}")
