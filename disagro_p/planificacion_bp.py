import json
import datetime 
from datetime import date
import re
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
from sqlalchemy import asc,desc,update,func,text
import requests 
import datetime
import time
import base64
import json
import csv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import postgresql

from disagro_i.error_reporter import ErrorReporter
from disagro_i.fecha_hora import get_user_datetime, parse_timezone_from_request
from io import StringIO

bp = Blueprint('planificacion_bp', __name__, url_prefix='/planificacion')

@bp.route("/planificaciones",methods=['GET'])
@requiere_login
@role_required(['nivel_1'])  
def planificaciones():
    """
    Carga del template con una tabla que contiene todas las planificaciones con su correspondiente estado
    """
    try: 
        db: Session = request.db
        planificaciones = db.query(modelo.Planificacion).filter(
            modelo.Planificacion.USUARIO == g.user.usuario,
            modelo.Planificacion.ESTADO != 'ARCHIVADO'
        ).order_by(modelo.Planificacion.FECHA.desc()).all()
        # print(planificaciones)
        return render_template("planificacion/planificaciones.html", usuario=g.user.usuario,planificaciones = planificaciones)
    finally:
        db.close()

@bp.route("/cargar/existencias",methods=['GET'])
@requiere_login
@role_required(['nivel_1'])  
def cargar_existencias():
    """
    Carga del template para cargar el archivo de existencias
    """
    try:
        db: Session = request.db
        resultado =  db.query(modelo.Planificacion).filter(modelo.Planificacion.USUARIO == g.user.usuario).all()
        existencias = db.query(modelo.MaestroUpload).filter_by(MAESTRO="EXISTENCIAS").first()
        utils = Utils()
        pais = utils.obtener_pais(db, g)
        pais = (pais or '').upper()
        anio_actual = datetime.datetime.now().year
        return render_template(
            "planificacion/existencias.html",
            usuario=g.user.usuario,
            resultado=resultado,
            existencias=existencias,
            pais=pais,
            anio_actual=anio_actual,
        )
    finally:
        db.close()

#Ese id se debe generar en la carga de existencias
#TODO RESOLVER EL PROBLEMA DE USAR TODAS
@bp.route("/planificar/<id>",methods=['GET'])
@requiere_login
def planificacion(id):
    """
    Carga del template para configurar la planificacion de acuerdo a los filtros de categoria, ubicacion y almacen
    """
    try:
        db: Session = request.db
        # Esto representa las categorias, ubicaciones y almacenes planificadas
        articulos_planificados = []
        articulos_filtrados = []
        filtros_de_planificacion  = []
        utils = Utils()
        pais = utils.obtener_pais(db,g)
        pais = (pais or '').upper()

        planificacion = (
            db.query(modelo.Planificacion)
            .filter(
                modelo.Planificacion.ID == id,
                modelo.Planificacion.USUARIO == g.user.usuario,
            )
            .first()
        )

        if not planificacion:
            abort(403)

        ubicaciones_planificadas = utils.obtener_planificaciones(db,id,pais,'UBICACION',modelo.Ubicacion,None)
        estan_todas_ubicacion = utils.estan_todas_planificadas('UBICACION',None,id,pais)
        
        almacenes_planificados = utils.obtener_planificaciones(db,id,pais,'ALMACEN',modelo.Almacen,None)
        estan_todas_almacen = utils.estan_todas_planificadas('ALMACEN',None,id,pais)

        usuarios_planificados = utils.usuarios_planificados(db,id,pais)
        estan_todas_usuarios = utils.estan_todas_planificadas('USUARIO',None,id,None)

        categorias_1_planificadas = utils.obtener_planificaciones(db,id,pais,'CATEGORIA',modelo.Categoria,'1')
        estan_todas_categorias_1 = utils.estan_todas_planificadas('CATEGORIA','1',id,None)

        categorias_2_planificadas = utils.obtener_planificaciones(db,id,pais,'CATEGORIA',modelo.Categoria,'2')
        estan_todas_categorias_2 = utils.estan_todas_planificadas('CATEGORIA','2',id,None)

        articulos_planificados = utils.obtener_planificaciones(db,id,pais,'ARTICULO',modelo.Articulo,None)

        # Esto representa las categorias, ubicaciones y almacenes globales
        categorias_1 = db.query(modelo.Categoria).filter(modelo.Categoria.AGRUPACION == '1').all()
        categorias_2 = db.query(modelo.Categoria).filter(modelo.Categoria.AGRUPACION == '2').all()
        ubicaciones = db.query(modelo.Ubicacion).all()
        almacenes = db.query(modelo.Almacen).all()

        if len(ubicaciones_planificadas) > 0:
            filtros_de_planificacion.append(modelo.Existencia.UBICACION.in_([ubicacion.UBICACION for ubicacion in ubicaciones_planificadas]))
        if len(almacenes_planificados) > 0:
            filtros_de_planificacion.append(modelo.Existencia.ALMACEN.in_([almacen.ALMACEN for almacen in almacenes_planificados]))
        if len(categorias_1_planificadas) > 0:
            filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_1.in_([categoria.CATEGORIA for categoria in categorias_1_planificadas]))
        if len(categorias_2_planificadas) > 0:
            filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_2.in_([categoria.CATEGORIA for categoria in categorias_2_planificadas]))

        if len(filtros_de_planificacion) > 0:
            articulos_filtrados = utils.obtener_articulos_planificados(db,filtros_de_planificacion,id)

        # Detectar artículos incompletos en esta planificación
        articulos_incompletos = (
            db.query(modelo.Articulo)
            .join(modelo.Existencia, modelo.Articulo.ARTICULO == modelo.Existencia.ARTICULO)
            .filter(
                modelo.Existencia.ID_PLANIFICACION == id,
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

        usuarios = db.query(modelo.Usuario).filter(modelo.Usuario.pais == pais, modelo.Usuario.nivel_5 == 'SI').all()
        return render_template("planificacion/planificacion.html", usuario=g.user.usuario,
                            categorias_1=categorias_1,
                            categorias_2=categorias_2,
                            ubicaciones=ubicaciones, almacenes=almacenes,
                            ubicaciones_planificadas=ubicaciones_planificadas,
                            almacenes_planificados=almacenes_planificados,
                            categorias_1_planificadas=categorias_1_planificadas,
                            categorias_2_planificadas=categorias_2_planificadas,
                            articulos_filtrados=articulos_filtrados,
                            ubicacion_tiene_opcion_todas=estan_todas_ubicacion,
                            almacen_tiene_opcion_todas=estan_todas_almacen,
                            categorias_1_tiene_opcion_todas=estan_todas_categorias_1,
                            categorias_2_tiene_opcion_todas=estan_todas_categorias_2,
                            usuarios=usuarios,
                            usuarios_planificados=usuarios_planificados,
                            usuario_tiene_opcion_todas=estan_todas_usuarios,
                            cantidad_articulos_incompletos=cantidad_articulos_incompletos,
                            lista_articulos_incompletos=lista_articulos_incompletos,
                            id=id,planificacion=planificacion,articulos_planificados=articulos_planificados,pais=pais)
    finally:
        db.close()

# --------------------------------------------------------- POST ----------------------------------------------------------------------------
@bp.route("/upload/existencias", methods=['POST'])
@requiere_login
@role_required(['nivel_1'])  
def subir_existencias():
    """
    Esta funcion se encarga de subir el archivo de existencias a la base de datos
    """
    if 'archivo' not in request.files:
        # print("No se ha subido ningun archivo")
        respuesta = {"mensaje":"No se ha subido ningun archivo"}
        return make_response(jsonify(respuesta), 400)

    file = request.files['archivo']

    if not file.filename.endswith('.csv'):
        # print("Formato de archivo invalido. Solo se permiten archivos CSV")
        respuesta = {"mensaje":"Formato de archivo invalido. Solo se permiten archivos CSV"}
        return make_response(jsonify(respuesta), 400)

    try:
        file = TextIOWrapper(file, encoding='utf-8')
        csv_reader = csv.reader(file,delimiter=';')
        next(csv_reader)
        # Convertir a lista para poder iterar múltiples veces
        csv_data = list(csv_reader)
        db = SessionLocal()
        # Limpiar la tabla antes de agregar nuevos registros
        utils = Utils()
        pais = utils.obtener_pais(db,g)
        articulos = db.query(modelo.Articulo).all()
        ubicaciones = db.query(modelo.Ubicacion).all()
        almacenes = db.query(modelo.Almacen).all()
        
        # Extraer todos los códigos de artículos únicos del CSV
        articulos_csv = set(row[0].strip() for row in csv_data if row and len(row) > 0 and row[0].strip() != "")
        
        # Obtener artículos existentes en BD
        articulos_bd = set(art.ARTICULO for art in articulos)
        
        # Identificar artículos faltantes
        articulos_faltantes = articulos_csv - articulos_bd
        
        # Auto-crear artículos faltantes si existen
        articulos_creados = []
        if articulos_faltantes:
            # Verificar que las categorías ND_1 y ND_2 existan, crearlas si no
            nd_1 = db.query(modelo.Categoria).filter_by(CATEGORIA='ND_1').first()
            if not nd_1:
                nd_1 = modelo.Categoria(CATEGORIA='ND_1', DESCRIPCION='No Definido', AGRUPACION='1')
                db.add(nd_1)
            
            nd_2 = db.query(modelo.Categoria).filter_by(CATEGORIA='ND_2').first()
            if not nd_2:
                nd_2 = modelo.Categoria(CATEGORIA='ND_2', DESCRIPCION='No Definido', AGRUPACION='2')
                db.add(nd_2)
            
            db.flush()  # Asegurar que las categorías estén disponibles
            
            # Crear artículos faltantes
            for codigo_articulo in sorted(articulos_faltantes):
                nuevo_articulo = modelo.Articulo(
                    ARTICULO=codigo_articulo,
                    DESCRIPCION='Sin descripción',
                    CATEGORIA_1='ND_1',
                    CATEGORIA_2='ND_2'
                )
                db.add(nuevo_articulo)
                articulos_creados.append(codigo_articulo)
            
            db.flush()
            
            # Registrar en bitácora la creación automática de artículos
            detalles = f"Artículos creados automáticamente durante carga de existencias: {', '.join(articulos_creados)}"
            bitacora = modelo.Bitacora(
                ID_USUARIO=g.user.usuario,
                ACCION='INSERCION_AUTOMATICA',
                TABLA='ARTICULO',
                DETALLES=detalles
            )
            db.add(bitacora)
            
            # Actualizar lista de artículos en memoria
            articulos = db.query(modelo.Articulo).all()
        
        # Read and validate the plan name: we now require a non-empty name when creating a plan
        nombre_planificacion = None
        try:
            nombre_planificacion = request.form.get('nombre') if request.form else None
        except Exception:
            nombre_planificacion = None

        if not nombre_planificacion or not nombre_planificacion.strip():
            return make_response(jsonify({"mensaje": "El nombre de la planificación es requerido.", "error": True}), 400)

        correlativo_base = None
        try:
            correlativo_base = request.form.get('correlativo_base') if request.form else None
        except Exception:
            correlativo_base = None

        correlativo_base = (correlativo_base or '').strip().upper().replace(' ', '-')
        if not correlativo_base:
            return make_response(jsonify({"mensaje": "El identificador del correlativo es requerido.", "error": True}), 400)
        if not re.fullmatch(r'[A-Z0-9-]+', correlativo_base):
            return make_response(jsonify({"mensaje": "El identificador del correlativo solo puede contener letras, números o guiones.", "error": True}), 400)
        if not re.search(r'[A-Z]', correlativo_base):
            return make_response(jsonify({"mensaje": "El identificador del correlativo debe contener al menos una letra.", "error": True}), 400)

        tipo_correlativo = None
        if request.form:
            tipo_correlativo = request.form.get('tipo_correlativo', None)

        prefijo = 'CI'
        pais_codigo = pais
        if pais_codigo == 'GT' and (tipo_correlativo or '').upper() == 'PLANTA':
            prefijo = 'CIP'

        # Usar zona horaria del usuario para determinar el año
        # El timezone viene del form data enviado por el cliente
        timezone_str = request.form.get('timezone', 'America/Guatemala')
        fecha_usuario = get_user_datetime(timezone_str)
        anio_actual = fecha_usuario.year
        
        consecutivo = db.execute(
            text('SELECT "TOMA_FISICA".siguiente_correlativo(:pais, :base, :anio) AS correlativo'),
            {"pais": pais_codigo, "base": correlativo_base, "anio": anio_actual}
        ).scalar()

        if consecutivo is None:
            consecutivo = 1

        correlativo = f"{prefijo}-{pais_codigo}-{correlativo_base}-{anio_actual}-{int(consecutivo):03d}"

        planificacion = modelo.Planificacion(
            ESTADO='INCOMPLETO',
            FECHA=fecha_usuario.replace(tzinfo=None),  # Remover timezone info para compatibilidad con DB
            REPORTE_ESTADO=None,
            USUARIO=g.user.usuario,
            NOMBRE=nombre_planificacion.strip(),
            CORRELATIVO=correlativo,
            CORRELATIVO_BASE=correlativo_base,
            FECHA_ACTUALIZACION=fecha_usuario.replace(tzinfo=None),
        )
        db.add(planificacion)
        db.flush()#esta linea es para obtener el id de la planificacion
        planificacion_id = planificacion.ID

        #db.query(modelo.Existencia).delete()
        for row in csv_data:
            if row[0] != "" and row[1] != "" and row[3] != "" and row[4] != "":
                articulo = row[0]
                ubicacion = row[1]
                almacen = row[2]
                cantidad = float(row[3])
                costo = float(row[4])
                lote = row[5]
                # print(f"Lote: {lote}")
                fecha_expiracion = row[6].strip()
                # print(f"Articulo: {articulo}, Ubicacion: {ubicacion}, Almacen: {almacen}, Cantidad: {cantidad}, Costo: {costo}, Lote: {lote}, Fecha Expiracion: {fecha_expiracion}")
                if articulo not in [art.ARTICULO for art in articulos]:
                    return make_response(jsonify({"mensaje":f"El articulo {articulo} no existe en la base de datos","error":True}), 400)
                if ubicacion not in [ubi.UBICACION for ubi in ubicaciones]:
                    return make_response(jsonify({"mensaje":f"La ubicacion {ubicacion} no existe en la base de datos","error":True}), 400)
                if almacen not in [alm.ALMACEN for alm in almacenes]:
                    return make_response(jsonify({"mensaje":f"El almacen {almacen} no existe en la base de datos","error":True}), 400)
                if fecha_expiracion != '' and fecha_expiracion != None:
                    # print(f"Fecha Expiracion: {fecha_expiracion}")
                    fecha_expiracion = datetime.datetime.strptime(fecha_expiracion, '%m/%d/%Y')
                else:
                    # print("Fecha Expiracion: None")
                    fecha_expiracion = None
                if lote == "":
                    lote = None

                nueva_existencia = modelo.Existencia(
                    ARTICULO=articulo,
                    ID_PLANIFICACION = planificacion_id,
                    UBICACION=ubicacion,
                    ALMACEN=almacen,
                    LOTE=lote,
                    FECHA_EXPIRACION=fecha_expiracion,
                    CANTIDAD=cantidad,
                    COSTO=costo
                )
                db.add(nueva_existencia)
        planificacion.ESTADO = "EXISTENCIAS_CARGADAS"
        
        # Usar zona horaria del usuario para fecha de actualización
        timezone_str = request.form.get('timezone', 'America/Guatemala')
        fecha_actualizacion = get_user_datetime(timezone_str)
        planificacion.FECHA_ACTUALIZACION = fecha_actualizacion.replace(tzinfo=None)
        db.commit()
        
        # Preparar respuesta con información de artículos creados
        mensaje = "Archivo subido exitosamente"
        if articulos_creados:
            mensaje += f". Se crearon automáticamente {len(articulos_creados)} artículo(s) nuevo(s)"
        
        respuesta = {
            "mensaje": mensaje,
            "id": planificacion_id,
            "correlativo": correlativo,
            "error": False,
            "articulos_creados": articulos_creados if articulos_creados else []
        }
        return make_response(jsonify(respuesta), 200)
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()
    
#para el query de articulos planificacion si se usan todos los ID en caso de TODOS
#pero para agregar en la tabla de planificaicon linea solo se una la palabra TODAS
@bp.route("/filtrar/<id_planificacion>",methods=['POST'])
@requiere_login
def filtrar(id_planificacion):
    """
    Esta funcion carga el template para la planificacion del inventario y para editar la planificacion
    """
    db: Session = request.db 
    json_data = request.get_json()
    print("json_data")
    print(json_data)
    utils = Utils()

    pais = utils.obtener_pais(db,g)
    pais = (pais or '').upper()

    categorias_1 = extrar_filtro_de_categorias(json_data, tabla='CATEGORIA', agrupacion='1', suffix='_CATEGORIA_1')
    if "TODAS_1" in categorias_1 or len(categorias_1) == 0:
        # Si se encuentra el filtro "TODAS" en las categorías 1, se reemplaza por todas las categorías 1 disponibles en la base de datos.
        categorias_db = db.query(modelo.Categoria.CATEGORIA).filter(modelo.Categoria.AGRUPACION == '1', modelo.Categoria.CATEGORIA != 'TODAS_1').all()
        categorias_1 = [categoria for (categoria,) in categorias_db]

    categorias_2 = extrar_filtro_de_categorias(json_data, tabla='CATEGORIA', agrupacion='2', suffix='_CATEGORIA_2')
    if "TODAS_2" in categorias_2 or len(categorias_2) == 0:
        # Si se encuentra el filtro "TODAS" en las categorías 2, se reemplaza por todas las categorías 2 disponibles en la base de datos.
        categorias_db = db.query(modelo.Categoria.CATEGORIA).filter(modelo.Categoria.AGRUPACION == '2', modelo.Categoria.CATEGORIA != 'TODAS_2').all()
        categorias_2 = [categoria for (categoria,) in categorias_db]

    ubicaciones = [filtro.removesuffix('_UBICACION') for item in json_data if item['TABLA'] == 'UBICACION' for filtro in item['FILTRO']]
    ubicaciones_normalizadas = [valor.strip().upper() for valor in ubicaciones]
    if (
        len(ubicaciones) == 0
        or any(valor == 'TODAS' or valor.startswith('TODAS_') or valor == f'TODAS_{pais}' for valor in ubicaciones_normalizadas)
    ):
        # Si se encuentra el filtro "TODAS" en las ubicaciones, se reemplaza por todas las ubicaciones disponibles en la base de datos.
        ubicaciones_db = db.query(modelo.Ubicacion.UBICACION).all()
        ubicaciones = [ubicacion for (ubicacion,) in ubicaciones_db]
    else:
        ubicaciones = [valor for valor, normalizado in zip(ubicaciones, ubicaciones_normalizadas) if not normalizado.startswith('TODAS')]

    almacenes = [filtro.removesuffix('_ALMACEN') for item in json_data if item['TABLA'] == 'ALMACEN' for filtro in item['FILTRO']]
    almacenes_normalizados = [valor.strip().upper() for valor in almacenes]
    if (
        len(almacenes) == 0
        or any(valor == 'TODAS' or valor.startswith('TODAS_') or valor == f'TODAS_{pais}' for valor in almacenes_normalizados)
    ):
        # Si se encuentra el filtro "TODAS" en los almacenes, se reemplaza por todos los almacenes disponibles en la base de datos.
        almacenes_db = db.query(modelo.Almacen.ALMACEN).all()
        almacenes = [almacen for (almacen,) in almacenes_db]
    else:
        almacenes = [valor for valor, normalizado in zip(almacenes, almacenes_normalizados) if not normalizado.startswith('TODAS')]

    try:
        filtros_de_planificacion  = []
        if len(categorias_1) > 0:
            filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_1.in_(categorias_1))

        if len(categorias_2) > 0:
            filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_2.in_(categorias_2))
        
        if len(ubicaciones) > 0:
            filtros_de_planificacion.append(modelo.Existencia.UBICACION.in_(ubicaciones))
        
        if len(almacenes) > 0:
            filtros_de_planificacion.append(modelo.Existencia.ALMACEN.in_(almacenes))
        
        # Este es el query más importante del sistema, ya que es el que filtra los artículos según los filtros seleccionados por el usuario.
        articulos_planificados = utils.obtener_articulos_planificados(db,filtros_de_planificacion,id_planificacion)
        # print(query_articulos_planificados.statement.compile(compile_kwargs={"literal_binds": True}))
        articulos_filtrados = [
            [articulo.CODIGO, articulo.DESCRIPCION]
            for articulo in articulos_planificados
        ]
        return make_response(jsonify({"mensaje": "El filtro se realizó con exito.", "error": False,"articulos_filtrados":articulos_filtrados}), 200)
    
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":err,"error":True}), 200)
    finally:
        db.close()
    
@bp.route("/planificar/<id>",methods=['POST'])
@requiere_login
def planificar(id):
    """
    Esta funcion se encarga de planificar el inventario, es decir, asignar los articulos a los usuarios,
    en base a los filtros seleccionados por el usuario en la vista de planificacion
    """
    #TODO: obtener usuario de la planificacion
    #TODO: obtener articulos de la planificacion
    db: Session = request.db 
    json_data = request.get_json()
    
    # Extraer timezone y filtros del payload
    timezone_str = json_data.get('timezone', 'America/Guatemala') if isinstance(json_data, dict) else 'America/Guatemala'
    
    # Si el payload tiene estructura {filtros: [...], timezone: "..."}, extraer filtros
    if isinstance(json_data, dict) and 'filtros' in json_data:
        filtros_data = json_data['filtros']
    else:
        # Retrocompatibilidad: si json_data es directamente el array de filtros
        filtros_data = json_data
        
    categorias_1, categorias_2, ubicaciones, almacenes, usuarios = [], [], [], [], []
    utils = Utils()
    pais = utils.obtener_pais(db,g)

    planificacion_actual = (
        db.query(modelo.Planificacion)
        .filter(
            modelo.Planificacion.ID == id,
            modelo.Planificacion.USUARIO == g.user.usuario,
        )
        .first()
    )
    if not planificacion_actual:
        abort(403)

    #TODO EVALUAR QUE LOS USUARIOS NO ESTEN EN MAS DE UNA PLANIFICACION
    try:
        """
        Primero se extraen los usuarios de la planificacion. Se permite asignar captadores a
        múltiples planificaciones, incluyendo aquellas configuradas con "TODAS".
        """
        usuarios_para_planificacion = extrar_usuairos(filtros_data)
        # print("len(usuarios_para_planificacion)")
        # print(len(usuarios_para_planificacion))
        if(len(usuarios_para_planificacion) > 0):
            # Allow users to be assigned to multiple planificaciones.
            # Previous behaviour returned an error when any of the users
            # were already assigned to another planificación. That check
            # was removed so a captador can belong to several planificaciones.
            pass
        else:
            pass

        #TODO: validar si viene articulos especificos, si es asi la plafinicacion solo se realiza para esos articulos

        categorias_1 = extrar_filtro_de_categorias(filtros_data, tabla='CATEGORIA', agrupacion='1', suffix='_CATEGORIA_1')
        if len(categorias_1) == 0:
            categorias_1 = ["TODAS_1"]
        categorias_2 = extrar_filtro_de_categorias(filtros_data, tabla='CATEGORIA', agrupacion='2', suffix='_CATEGORIA_2')
        if len(categorias_2) == 0:
            categorias_2 = ["TODAS_2"]
        ubicaciones = [filtro.removesuffix('_UBICACION') for item in filtros_data if item['TABLA'] == 'UBICACION' for filtro in item['FILTRO']]
        if len(ubicaciones) == 0:
            ubicaciones = [f'TODAS']
        almacenes = [filtro.removesuffix('_ALMACEN') for item in filtros_data if item['TABLA'] == 'ALMACEN' for filtro in item['FILTRO']]
        if len(almacenes) == 0:
            almacenes = [f'TODAS']
        usuarios = [filtro.rstrip('_USUARIO') for item in filtros_data if item['TABLA'] == 'USUARIO' for filtro in item['FILTRO']]
        if len(usuarios) == 0:
            usuarios = ["TODAS"]
        articulos = [filtro.rstrip('_ARTICULO') for item in filtros_data if item['TABLA'] == 'ARTICULO' for filtro in item['FILTRO']]
        # print("articulos: ...")
        # print(articulos)
       
        # print("usuarios_para_planificacion")
        # print(usuarios_para_planificacion)
        if len(usuarios_para_planificacion) == 0:
            usuarios_para_planificacion = ["TODAS"]

        # print("usuarios_para_planificacion")
        # print(usuarios_para_planificacion)

        add_planificacion(id,'CATEGORIA_1',categorias_1,db)
        add_planificacion(id,'CATEGORIA_2',categorias_2,db)
        add_planificacion(id,'UBICACION',ubicaciones,db)
        add_planificacion(id,'ALMACEN',almacenes,db)
        add_planificacion(id,'USUARIO',usuarios_para_planificacion,db)
        add_planificacion(id,'ARTICULO',articulos,db)

        # Se elimina la planificacion anterior para el mismo id para no duplicar
        db.query(modelo.Planificacion_linea).filter(modelo.Planificacion_linea.PLANIFICACION_ID == id).delete(synchronize_session=False) 
        # for item in json_data:
        #     add_planificacion(id, item['TABLA'], item['FILTRO'], db)
        planificacion_actual.ESTADO = "EN_PLANIFICACION"
        
        # Usar zona horaria del usuario para fecha de actualización
        fecha_actualizacion = get_user_datetime(timezone_str)
        planificacion_actual.FECHA_ACTUALIZACION = fecha_actualizacion.replace(tzinfo=None)
        db.commit()
        return make_response(jsonify({"mensaje": "La planificación se realizó con exito.", "error": False}), 200)
            
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":err,"error":True}), 200)
    finally:
        db.close()

def add_planificacion(planificacion_id,tabla,filtros,db):
    for filtro in filtros:
        db.add(modelo.Planificacion_linea(
            PLANIFICACION_ID=planificacion_id,
            NOMBRE_TABLA_FILTRO=tabla,
            VALOR_FILTRO=filtro
        ))   

@bp.route("/articulos/incompletos", methods=['GET'])
@bp.route("/articulos/incompletos/<int:id_planificacion>", methods=['GET'])
@requiere_login
@role_required(['nivel_1', 'super_usuario'])
def obtener_articulos_incompletos(id_planificacion=None):
    """
    Obtiene la lista de artículos incompletos.
    - super_usuario sin id_planificacion: Obtiene todos los artículos incompletos del sistema
    - nivel_1 con id_planificacion: Obtiene artículos incompletos de una planificación específica
    """
    db: Session = request.db
    try:
        # Determinar si es super_usuario desde g.user directamente
        es_super_usuario = g.user and g.user.super_usuario == 'SI'
        
        print(f"[DEBUG] obtener_articulos_incompletos - es_super_usuario: {es_super_usuario}, id_planificacion: {id_planificacion}")
        
        # Si es nivel_1, debe proporcionar id_planificacion
        if not es_super_usuario and id_planificacion is None:
            return make_response(jsonify({"mensaje": "ID de planificación requerido", "error": True}), 400)
        
        # Si es nivel_1, verificar que la planificación le pertenece
        if not es_super_usuario and id_planificacion:
            planificacion = (
                db.query(modelo.Planificacion)
                .filter(
                    modelo.Planificacion.ID == id_planificacion,
                    modelo.Planificacion.USUARIO == g.user.usuario,
                )
                .first()
            )
            if not planificacion:
                abort(403)
        
        # Construir query base de artículos incompletos
        query = db.query(modelo.Articulo).filter(
            modelo.Articulo.DESCRIPCION == 'Sin descripción',
            (
                modelo.Articulo.CATEGORIA_1.in_(['ND_1', 'ND']) |
                modelo.Articulo.CATEGORIA_2.in_(['ND_2', 'ND'])
            )
        )
        
        print(f"[DEBUG] Query base construido")
        
        # Si se proporciona id_planificacion, filtrar por esa planificación
        if id_planificacion:
            print(f"[DEBUG] Filtrando por id_planificacion: {id_planificacion}")
            query = query.join(
                modelo.Existencia, 
                modelo.Articulo.ARTICULO == modelo.Existencia.ARTICULO
            ).filter(
                modelo.Existencia.ID_PLANIFICACION == id_planificacion
            )
        
        articulos_incompletos = query.distinct().all()
        print(f"[DEBUG] Artículos encontrados: {len(articulos_incompletos)}")
        
        # Obtener todas las categorías para los selects
        categorias_1 = db.query(modelo.Categoria).filter(modelo.Categoria.AGRUPACION == '1').all()
        categorias_2 = db.query(modelo.Categoria).filter(modelo.Categoria.AGRUPACION == '2').all()
        
        print(f"[DEBUG] Categorías 1: {len(categorias_1)}, Categorías 2: {len(categorias_2)}")
        
        articulos_data = [
            {
                "articulo": art.ARTICULO,
                "descripcion": art.DESCRIPCION,
                "categoria_1": art.CATEGORIA_1,
                "categoria_2": art.CATEGORIA_2
            }
            for art in articulos_incompletos
        ]
        
        categorias_1_data = [{"codigo": cat.CATEGORIA, "descripcion": cat.DESCRIPCION} for cat in categorias_1]
        categorias_2_data = [{"codigo": cat.CATEGORIA, "descripcion": cat.DESCRIPCION} for cat in categorias_2]
        
        print(f"[DEBUG] Retornando {len(articulos_data)} artículos")
        
        return make_response(jsonify({
            "articulos": articulos_data,
            "categorias_1": categorias_1_data,
            "categorias_2": categorias_2_data,
            "error": False
        }), 200)
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje": str(err), "error": True}), 500)
    finally:
        db.close()

@bp.route("/articulos/actualizar", methods=['PUT'])
@requiere_login
@role_required(['nivel_1', 'super_usuario'])
def actualizar_articulo():
    """
    Actualiza la descripción y categorías de un artículo
    """
    db: Session = request.db
    try:
        json_data = request.get_json()
        codigo_articulo = json_data.get('articulo')
        nueva_descripcion = json_data.get('descripcion', '').strip()
        nueva_categoria_1 = json_data.get('categoria_1')
        nueva_categoria_2 = json_data.get('categoria_2')
        
        # Validaciones
        if not codigo_articulo:
            return make_response(jsonify({"mensaje": "Código de artículo requerido", "error": True}), 400)
        
        if not nueva_descripcion or nueva_descripcion == 'Sin descripción':
            return make_response(jsonify({"mensaje": "La descripción no puede estar vacía o ser 'Sin descripción'", "error": True}), 400)
        
        if not nueva_categoria_1 or not nueva_categoria_2:
            return make_response(jsonify({"mensaje": "Ambas categorías son requeridas", "error": True}), 400)
        
        # Verificar que las categorías existen
        cat_1 = db.query(modelo.Categoria).filter_by(CATEGORIA=nueva_categoria_1, AGRUPACION='1').first()
        cat_2 = db.query(modelo.Categoria).filter_by(CATEGORIA=nueva_categoria_2, AGRUPACION='2').first()
        
        if not cat_1:
            return make_response(jsonify({"mensaje": f"Categoría 1 '{nueva_categoria_1}' no existe", "error": True}), 400)
        if not cat_2:
            return make_response(jsonify({"mensaje": f"Categoría 2 '{nueva_categoria_2}' no existe", "error": True}), 400)
        
        # Obtener artículo
        articulo = db.query(modelo.Articulo).filter_by(ARTICULO=codigo_articulo).first()
        if not articulo:
            return make_response(jsonify({"mensaje": "Artículo no encontrado", "error": True}), 404)
        
        # Guardar valores anteriores para bitácora
        valores_anteriores = {
            "descripcion": articulo.DESCRIPCION,
            "categoria_1": articulo.CATEGORIA_1,
            "categoria_2": articulo.CATEGORIA_2
        }
        
        # Actualizar artículo
        articulo.DESCRIPCION = nueva_descripcion
        articulo.CATEGORIA_1 = nueva_categoria_1
        articulo.CATEGORIA_2 = nueva_categoria_2
        
        # Registrar en bitácora
        detalles = f"Artículo {codigo_articulo} actualizado. Cambios: DESC: '{valores_anteriores['descripcion']}' → '{nueva_descripcion}', CAT1: '{valores_anteriores['categoria_1']}' → '{nueva_categoria_1}', CAT2: '{valores_anteriores['categoria_2']}' → '{nueva_categoria_2}'"
        bitacora = modelo.Bitacora(
            ID_USUARIO=g.user.usuario,
            ACCION='ACTUALIZAR_ARTICULO',
            TABLA='ARTICULO',
            DETALLES=detalles
        )
        db.add(bitacora)
        
        db.commit()
        return make_response(jsonify({"mensaje": "Artículo actualizado exitosamente", "error": False}), 200)
    except Exception as err:
        db.rollback()
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje": str(err), "error": True}), 500)
    finally:
        db.close()

@bp.route("/eliminar/<int:id_planificacion>", methods=['DELETE'])
@requiere_login
@role_required(['nivel_1'])
def eliminar_planificacion(id_planificacion):
    db: Session = request.db
    try:
        planificacion = (
            db.query(modelo.Planificacion)
            .filter(
                modelo.Planificacion.ID == id_planificacion,
                modelo.Planificacion.USUARIO == g.user.usuario,
            )
            .first()
        )
        if not planificacion:
            abort(403)
        if planificacion.ESTADO == "ARCHIVADO":
            return make_response(jsonify({"mensaje": "No se puede eliminar una planificación archivada", "error": True}), 400)
        db.query(modelo.CaptacionFisica).filter(modelo.CaptacionFisica.ID_PLANIFICACION == id_planificacion).delete(synchronize_session=False)
        db.query(modelo.Existencia).filter_by(ID_PLANIFICACION=id_planificacion).delete()
        db.query(modelo.Planificacion_linea).filter(modelo.Planificacion_linea.PLANIFICACION_ID == id_planificacion).delete(synchronize_session=False)
        db.delete(planificacion)
        db.commit()
        return make_response(jsonify({"mensaje": "Planificación eliminada exitosamente", "error": False}), 200)
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()

def extrar_filtro_de_categorias(json_data, tabla='CATEGORIA', agrupacion='1', suffix='_CATEGORIA_1'):
    """
    Extrae y transforma los filtros de los items que cumplen con los criterios, 
    sin usar sintaxis de comprensiones de lista.
    """
    resultado = []
    for item in json_data:
        if item['TABLA'] == tabla and item['AGRUPACION'] == agrupacion:
            for filtro in item['FILTRO']:
                if filtro.endswith(suffix):
                    procesado = filtro[:-len(suffix)]
                else:
                    procesado = filtro
                resultado.append(procesado)
    return resultado

def extrar_usuairos(json_data):
    """
    Extrae y transforma los filtros de los items que cumplen con los criterios, 
    sin usar sintaxis de comprensiones de lista.
    """
    resultado = []
    for item in json_data:
        if item['TABLA'] == 'USUARIO':
            for filtro in item['FILTRO']:
                if filtro.endswith('_USUARIO'):
                    procesado = filtro[:-len('_USUARIO')]
                else:
                    procesado = filtro
                resultado.append(procesado)
    return resultado

@bp.route("/descargar/existencias/<int:id_planificacion>", methods=['GET'])
@requiere_login
@role_required(['nivel_1','nivel_2','nivel_3'])
def descargar_existencias(id_planificacion):
    """
    Descarga un archivo Excel con las existencias de una planificación específica
    """
    db: Session = request.db
    try:
        # Verificar que la planificación existe y pertenece al usuario
        planificacion = (
            db.query(modelo.Planificacion)
            .filter(
                modelo.Planificacion.ID == id_planificacion,
                modelo.Planificacion.USUARIO == g.user.usuario,
            )
            .first()
        )
        
        if not planificacion:
            abort(403)
        
        # Obtener las existencias de la planificación
        existencias = (
            db.query(modelo.Existencia)
            .filter(modelo.Existencia.ID_PLANIFICACION == id_planificacion)
            .order_by(modelo.Existencia.ARTICULO, modelo.Existencia.UBICACION, modelo.Existencia.ALMACEN)
            .all()
        )
        
        if not existencias:
            return make_response(jsonify({"mensaje": "No hay existencias para esta planificación", "error": True}), 404)
        
        # Crear el archivo CSV en memoria
        output = StringIO()
        csv_writer = csv.writer(output, delimiter=';')
        
        # Escribir encabezados
        csv_writer.writerow(['ARTICULO', 'UBICACION', 'ALMACEN', 'CANTIDAD', 'COSTO', 'LOTE', 'FECHA_EXPIRACION'])
        
        # Escribir datos
        for existencia in existencias:
            fecha_exp = ''
            if existencia.FECHA_EXPIRACION:
                fecha_exp = existencia.FECHA_EXPIRACION.strftime('%m/%d/%Y')
            
            csv_writer.writerow([
                existencia.ARTICULO,
                existencia.UBICACION,
                existencia.ALMACEN,
                existencia.CANTIDAD,
                existencia.COSTO,
                existencia.LOTE or '',
                fecha_exp
            ])
        
        # Preparar respuesta
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=existencias_planificacion_{id_planificacion}.csv"
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje": str(err), "error": True}), 500)
    finally:
        db.close()
