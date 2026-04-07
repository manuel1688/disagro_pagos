import json
import datetime 
from datetime import date
from typing import Optional
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
from werkzeug.security import check_password_hash

import sys
from disagro_i.clases import modelo
from disagro_i.clases.utils import Utils
from disagro_i.conexion_orm import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import and_, asc,desc, not_, or_,update,func
import requests
import datetime
import time
import base64
import json
import csv
from sqlalchemy.exc import SQLAlchemyError
import openpyxl
from PIL import Image
import io
from disagro_i.error_reporter import ErrorReporter
from sqlalchemy.inspection import inspect
from disagro_i.fecha_hora import get_user_date, parse_timezone_from_request

bp = Blueprint('inventario_bp', __name__, url_prefix='/inventario')

# 1. Captura de inventario
# 2. No se debe cargar nada si no hay una planificacion activa


def _parse_fecha_generica(valor: Optional[str]) -> Optional[date]:
    if not valor:
        return None

    texto = valor.strip()
    if texto == "":
        return None

    formatos = ["%d/%m/%Y", "%Y-%m-%d"]
    for formato in formatos:
        try:
            return datetime.datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def _obtener_estado_vencido(db: Session) -> Optional[str]:
    estado = (
        db.query(modelo.Estado)
        .filter(func.lower(modelo.Estado.ESTADO) == 'vencido')
        .first()
    )
    return estado.ESTADO if estado else None


def _aplicar_estado_vencido_si_corresponde(json_data: dict, db: Session) -> None:
    fecha_expiracion = _parse_fecha_generica(json_data.get("FECHA_EXPIRACION"))
    if not fecha_expiracion:
        return

    # Usar la fecha del usuario según su zona horaria
    timezone_str = parse_timezone_from_request(json_data)
    fecha_usuario = get_user_date(timezone_str)
    
    if fecha_expiracion >= fecha_usuario:
        return

    estado_vencido = _obtener_estado_vencido(db)
    if estado_vencido:
        json_data["ESTADO"] = estado_vencido


def _marcar_planificacion_en_inventario(db: Session, planificacion: Optional[modelo.Planificacion], contexto: str) -> None:
    """
    Asegura que la planificación quede en estado EN_INVENTARIO.
    Se usa un UPDATE explícito para evitar condiciones de carrera.
    """
    if not planificacion:
        print(f"[DEBUG]{contexto} planificacion no encontrada, no se puede actualizar estado")
        return

    if planificacion.ESTADO != 'EN_PLANIFICACION':
        print(f"[DEBUG]{contexto} planificacion {planificacion.ID} no está en EN_PLANIFICACION (estado actual: {planificacion.ESTADO})")
        return

    filas = (
        db.query(modelo.Planificacion)
        .filter(
            modelo.Planificacion.ID == planificacion.ID,
            modelo.Planificacion.ESTADO == 'EN_PLANIFICACION',
        )
        .update({modelo.Planificacion.ESTADO: 'EN_INVENTARIO'}, synchronize_session=False)
    )

    if filas:
        planificacion.ESTADO = 'EN_INVENTARIO'
        print(f"[DEBUG]{contexto} planificacion {planificacion.ID} actualizada a EN_INVENTARIO")
    else:
        print(f"[DEBUG]{contexto} no se actualizó planificacion {planificacion.ID}; estado cambió antes del update")


def compress_image_if_needed(file_data: bytes) -> bytes:
    """
    Comprime una imagen si su tamaño excede 2MB.
    - Redimensiona a máximo 1920x1920px manteniendo aspect ratio
    - Comprime a calidad 85% en formato JPEG
    - Retorna los bytes de la imagen (original o comprimida)
    """
    if not file_data or len(file_data) <= 2 * 1024 * 1024:  # 2MB
        return file_data
    
    try:
        # Abrir imagen desde bytes
        img = Image.open(io.BytesIO(file_data))
        
        # Convertir a RGB si es necesario (para guardar como JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar si excede 1920x1920
        max_size = 1920
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Comprimir a JPEG con calidad 85%
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        compressed_data = output.getvalue()
        
        original_size = len(file_data) / (1024 * 1024)  # MB
        compressed_size = len(compressed_data) / (1024 * 1024)  # MB
        print(f"[DEBUG] Imagen comprimida: {original_size:.2f}MB -> {compressed_size:.2f}MB")
        
        return compressed_data
    except Exception as e:
        print(f"[ERROR] Error al comprimir imagen: {str(e)}")
        # Si falla la compresión, retornar imagen original
        return file_data


@bp.route("/captura/<planificacion_id>",methods=['GET'])
@requiere_login 
def captura_por_id(planificacion_id):
    try:
        db: Session = request.db
        utils = Utils()
        captura = True
        re_conteo = False
        nuevo_articulo = False
        return obtener_pantalla_captura(db,g,utils,captura,re_conteo,nuevo_articulo,planificacion_id)
    finally:
        db.close()


def _construir_planificaciones_json(planificaciones):
    """Normaliza la data de planificaciones para el selector."""
    return [
        {
            "ID": p.ID,
            "ESTADO": p.ESTADO,
            "FECHA": p.FECHA.strftime('%d/%m/%Y') if p.FECHA else "",
            "REPORTE_ESTADO": p.REPORTE_ESTADO,
            "USUARIO": p.USUARIO,
            "DESCRIPCION": (
                (f"Número de planificación: {p.ID}, {p.NOMBRE}, creado el {p.FECHA.strftime('%d/%m/%Y')}")
                if (getattr(p, 'NOMBRE', None) and str(getattr(p, 'NOMBRE')).strip() != '' and p.FECHA)
                else (
                    f"Número de planificación: {p.ID} , {str(getattr(p, 'NOMBRE'))}"
                    if (getattr(p, 'NOMBRE', None) and str(getattr(p, 'NOMBRE')).strip() != '')
                    else (
                        f"Número de planificación: {p.ID} , creado el {p.FECHA.strftime('%d/%m/%Y')}"
                        if p.FECHA
                        else f"Número de planificación: {p.ID}"
                    )
                )
            ),
        }
        for p in planificaciones
    ]


def _resolver_selector_planificacion(db: Session, utils: Utils, redirect_endpoint: str):
    """Encapsula la lógica de selección y redirección de planificaciones activas."""
    pais = utils.obtener_pais(db, g)
    planificaciones = get_planificaciones_activas(db, pais, g.user.usuario)

    if not planificaciones:
        flash("No hay planificacion activa para este usuario", "error")
        return render_template('inicio.html', error="No hay planificacion activa para este usuario")

    if len(planificaciones) == 1:
        pid = planificaciones[0].ID
        return redirect(url_for(redirect_endpoint, planificacion_id=pid))

    planificaciones_activas_json = _construir_planificaciones_json(planificaciones)
    url_template = url_for(redirect_endpoint, planificacion_id='__PLAN_ID__')
    modo_config = {
        'inventario_bp.captura_por_id': {
            'etiqueta': 'Toma física',
            'descripcion': 'Selecciona la planificación para registrar capturas.',
            'badge_class': 'badge-planificacion-info',
            'boton_texto': 'Ir a captura',
        },
        'inventario_bp.reconteo_por_id': {
            'etiqueta': 'Reconteo',
            'descripcion': 'Selecciona la planificación para validar diferencias.',
            'badge_class': 'badge-planificacion-danger',
            'boton_texto': 'Ir a reconteo',
        },
        'inventario_bp.nuevo_por_id': {
            'etiqueta': 'Nuevo artículo',
            'descripcion': 'Selecciona la planificación donde agregarás artículos específicos.',
            'badge_class': 'badge-planificacion-warning',
            'boton_texto': 'Ir a nuevo artículo',
        },
    }
    modo = modo_config.get(redirect_endpoint, modo_config['inventario_bp.captura_por_id'])
    return render_template(
        'inventario/selector_planificacion.html',
        planificaciones_activas=planificaciones_activas_json,
        url_template=url_template,
        modo=modo,
    )


@bp.route('/captura', methods=['GET'])
@requiere_login
def selector_de_planificacion():
    """Ruta por defecto para captura: decide entre redirigir o mostrar selector."""
    try:
        db: Session = request.db
        utils = Utils()
        return _resolver_selector_planificacion(db, utils, 'inventario_bp.captura_por_id')
    finally:
        db.close()

@bp.route("/reconteo",methods=['GET'])
@requiere_login
@role_required(['nivel_3'])
def reconteo():
    try:
        db: Session = request.db
        utils = Utils()
        return _resolver_selector_planificacion(db, utils, 'inventario_bp.reconteo_por_id')
    finally:
        db.close()


@bp.route("/reconteo/<planificacion_id>", methods=['GET'])
@requiere_login
@role_required(['nivel_3'])
def reconteo_por_id(planificacion_id):
    try:
        db: Session = request.db
        utils = Utils()
        captura = False
        re_conteo = True
        nuevo_articulo = False
        return obtener_pantalla_captura(db, g, utils, captura, re_conteo, nuevo_articulo, planificacion_id)
    finally:
        db.close()

@bp.route("/nuevo", methods=['GET'])
@requiere_login
def nuevo():
    try:
        db: Session = request.db
        utils = Utils()
        return _resolver_selector_planificacion(db, utils, 'inventario_bp.nuevo_por_id')
    finally:
        db.close()


@bp.route("/nuevo/<planificacion_id>", methods=['GET'])
@requiere_login
def nuevo_por_id(planificacion_id):
    try:
        db: Session = request.db
        utils = Utils()
        captura = True
        re_conteo = False
        nuevo_articulo = True
        return obtener_pantalla_captura(db, g, utils, captura, re_conteo, nuevo_articulo, planificacion_id)
    finally:
        db.close()

def get_planificacion_id(session: Session, pais: str, usuario_asignado: str):
    result = session.query(modelo.Planificacion.ID).join(modelo.Usuario, modelo.Planificacion.USUARIO == modelo.Usuario.usuario).join(
        modelo.Planificacion_linea, modelo.Planificacion.ID == modelo.Planificacion_linea.PLANIFICACION_ID
    ).filter(
        and_(
            modelo.Usuario.pais == pais,
            or_(
                and_(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',
                    modelo.Planificacion_linea.VALOR_FILTRO == usuario_asignado
                ),
                
                and_(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',
                    modelo.Planificacion_linea.VALOR_FILTRO == 'TODAS'
                ),
            ),
            or_(
                modelo.Planificacion.ESTADO == 'EN_PLANIFICACION',
                modelo.Planificacion.ESTADO == 'EN_INVENTARIO'
            )
        )
    ).distinct().one_or_none()
    
    if result:
        return result[0]  # Return the ID of the planificacion
    return None

def get_planificaciones_activas(session: Session, pais: str, usuario_asignado: str):
    """
    Devuelve una lista de objetos Planificacion que estén activos (EN_PLANIFICACION o EN_INVENTARIO)
    y que apliquen al usuario dado (por valor de filtro 'USUARIO' igual al usuario o 'TODAS').
    """
    results = session.query(modelo.Planificacion).join(
        modelo.Planificacion_linea, modelo.Planificacion.ID == modelo.Planificacion_linea.PLANIFICACION_ID
    ).join(
        modelo.Usuario, modelo.Planificacion.USUARIO == modelo.Usuario.usuario
    ).filter(
        and_(
            modelo.Usuario.pais == pais,
            or_(
                and_(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',
                    modelo.Planificacion_linea.VALOR_FILTRO == usuario_asignado
                ),
                and_(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',
                    modelo.Planificacion_linea.VALOR_FILTRO == 'TODAS'
                ),
            ),
            modelo.Planificacion.ESTADO.in_(['EN_PLANIFICACION', 'EN_INVENTARIO'])
        )
    ).distinct().all()

    return results    

def _ruta_selector_por_modo(captura: bool, re_conteo: bool, nuevo_articulo: bool) -> str:
    if re_conteo:
        return url_for('inventario_bp.reconteo')
    if nuevo_articulo:
        return url_for('inventario_bp.nuevo')
    return url_for('inventario_bp.selector_de_planificacion')


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "si", "sí", "on", "yes"}
    return False


def obtener_pantalla_captura(db, g, utils, captura, re_conteo, nuevo_articulo, planificacion_id=None):
    """
    Evitar que un usuario que esta en INVENTARIO sea asignado a un Planificacion
    """
    try:
        planificacion_activa = None
        #Buscar la planifiacion configurada para este usuario
        #Solo debe haber una planificacion activa por usuario
        #El usuario puede estar en una configuracion de TODAS
        #Solo debe haber una planificacion TODAS 
        pais_del_usuario = utils.obtener_pais(db,g)

        if planificacion_id is None:
            planificacion_id = get_planificacion_id(db, pais_del_usuario, g.user.usuario)

        if planificacion_id is None:
            flash("No hay planificacion activa para este usuario", "error")
            return render_template('inicio.html', error="No hay planificacion activa para este usuario")
        else:
            planificacion_activa = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == planificacion_id).first()

        if not planificacion_activa:
            flash("La planificación solicitada no existe", "error")
            return redirect(_ruta_selector_por_modo(captura, re_conteo, nuevo_articulo))

        if planificacion_activa.ESTADO == "ARCHIVADO":
            flash("La planificación seleccionada está archivada. Seleccione una planificación activa.", "error")
            return redirect(_ruta_selector_por_modo(captura, re_conteo, nuevo_articulo))

        print("planificacion_activa")
        print(planificacion_activa.USUARIO)
        almacenes_planificados = utils.obtener_planificaciones(db,planificacion_activa.ID,pais_del_usuario,'ALMACEN',modelo.Almacen)
        ubicaciones_planificadas = utils.obtener_planificaciones(db,planificacion_activa.ID,pais_del_usuario,'UBICACION',modelo.Ubicacion)
        return render_template(
            "inventario/captura.html",
            usuario=g.user.usuario,
            ubicaciones=ubicaciones_planificadas,
            captura=captura,
            almacenes=almacenes_planificados,
            planificacion_activa=planificacion_activa,
            re_conteo=re_conteo,
            nuevo_articulo=nuevo_articulo,
        )
    finally:
        db.close()

@bp.route("/articulos/<id_planificacion>",methods=['GET'])
@requiere_login
def articulos(id_planificacion):
    try:
        db: Session = request.db

        planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
        if not planificacion:
            return make_response(jsonify({"mensaje": "La planificación solicitada no existe", "error": True, "redirect": _ruta_selector_por_modo(True, False, False)}), 404)
        if planificacion.ESTADO == "ARCHIVADO":
            return make_response(jsonify({"mensaje": "La planificación está archivada. Selecciona una planificación activa.", "error": True, "redirect": _ruta_selector_por_modo(True, False, False)}), 400)

        # Esto representa las categorias, ubicaciones y almacenes planificadas
        articulos_planificados = []
        filtros_de_planificacion  = []
        utils = Utils()
        pais = utils.obtener_pais(db,g)
        version = None
        if planificacion and planificacion.FECHA_ACTUALIZACION:
            version = planificacion.FECHA_ACTUALIZACION.isoformat()

        #obtener_planificacion(self, db, id_planificacion, pais, tabla_filtro, modelo,agrupacion = None)
        ubicaciones_planificadas = utils.obtener_planificaciones(db,id_planificacion,pais,'UBICACION',modelo.Ubicacion)
        almacenes_planificados = utils.obtener_planificaciones(db,id_planificacion,pais,'ALMACEN',modelo.Almacen)
        categorias_1_planificadas = utils.obtener_planificaciones(db,id_planificacion,pais,'CATEGORIA',modelo.Categoria,'1')
        categorias_2_planificadas = utils.obtener_planificaciones(db,id_planificacion,pais,'CATEGORIA',modelo.Categoria,'2')

        # En caso de tener articulos especificos planificados solo se deben mostrar esos articulos
        articulos_planificados = utils.obtener_planificaciones(db,id_planificacion,pais,'ARTICULO',modelo.Articulo)
        if len(articulos_planificados) > 0:
            articulos_planificados = db.query(
                modelo.Articulo.ARTICULO.label('CODIGO'),
                modelo.Articulo.DESCRIPCION.label("DESCRIPCION")
            ).filter(
                modelo.Articulo.ARTICULO.in_([art.ARTICULO for art in articulos_planificados])
            ).order_by(
                modelo.Articulo.ARTICULO.asc()
            ).all()
            articulos_planificados_json = [dict(row._asdict()) for row in articulos_planificados]
            return jsonify({'DATOS': articulos_planificados_json, "RESPUESTA": "OK", "version": version})

        if len(ubicaciones_planificadas) > 0:
            filtros_de_planificacion.append(modelo.Existencia.UBICACION.in_([ubicacion.UBICACION for ubicacion in ubicaciones_planificadas]))
        if len(almacenes_planificados) > 0:
            filtros_de_planificacion.append(modelo.Existencia.ALMACEN.in_([almacen.ALMACEN for almacen in almacenes_planificados]))
        if len(categorias_1_planificadas) > 0:
            filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_1.in_([categoria.CATEGORIA for categoria in categorias_1_planificadas]))
        if len(categorias_2_planificadas) > 0:
            filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_2.in_([categoria.CATEGORIA for categoria in categorias_2_planificadas]))

        # TODO: tecnicamente no deberia ser necesario preguntar por filtros_de_planificacion ya que si llegamos a este punto es porque hay filtros
        if len(filtros_de_planificacion) > 0:
            articulos_planificados = utils.obtener_articulos_planificados(db,filtros_de_planificacion,id_planificacion)
            articulos_planificados_json = [dict(row._asdict()) for row in articulos_planificados]
            return jsonify({'DATOS':articulos_planificados_json,"RESPUESTA":"OK", "version": version})
        else:
            # Si no hay filtros de planificacion, entonces no se deben mostrar articulos
            return jsonify({'DATOS':[],"RESPUESTA":"OK", "version": version})
    finally:
        db.close()

@bp.route("/captaciones/<id_planificacion>",methods=['GET'])
@requiere_login
def captaciones(id_planificacion):
    """
    Esta funcion se encarga de obtener las captaciones fisicas del usuario
    """
    try:
        db: Session = request.db
        planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
        if not planificacion or planificacion.ESTADO == "ARCHIVADO":
            flash("La planificación seleccionada no está disponible para captura.", "error")
            return redirect(_ruta_selector_por_modo(True, False, False))
        print("USUARIO")
        print(g.user.usuario)
        captaciones = db.query(modelo.CaptacionFisica).filter(
        modelo.CaptacionFisica.USUARIO == str(g.user.usuario),
            modelo.CaptacionFisica.ID_PLANIFICACION == id_planificacion,
            or_(
                modelo.CaptacionFisica.ETIQUETA.is_(None),  # Incluir valores NULL
                modelo.CaptacionFisica.ETIQUETA == '',     # Incluir valores en blanco
                not_(modelo.CaptacionFisica.ETIQUETA.like("RECONTEO%"))  # Excluir los que comienzan con "RECONTEO"
            )
        ).all()
        # print("query_captaciones")
        # print("Query string:", str(query_captaciones.statement))
        # captaciones = query_captaciones.all()

        print("captaciones")
        print(captaciones)

        # Reemplazar los valores None por ''
        captaciones = [
            {
                'ID': captacion.ID if captacion.ID is not None else '',
                'ARTICULO': captacion.ARTICULO if captacion.ARTICULO is not None else '',
                'DESCRIPCION': captacion.DESCRIPCION if captacion.DESCRIPCION is not None else '',
                'UBICACION': captacion.UBICACION if captacion.UBICACION is not None else '',
                'ALMACEN': captacion.ALMACEN if captacion.ALMACEN is not None else '',
                'LOTE': captacion.LOTE if captacion.LOTE is not None else '',
                'FECHA_EXPIRACION': captacion.FECHA_EXPIRACION.strftime('%d/%m/%Y') if captacion.FECHA_EXPIRACION else '',
                'FECHA': captacion.FECHA if captacion.FECHA is not None else '',
                'CANTIDAD': captacion.CANTIDAD if captacion.CANTIDAD is not None else '',
                'USUARIO': captacion.USUARIO if captacion.USUARIO is not None else '',
                'SERIE': captacion.SERIE if getattr(captacion, 'SERIE', None) is not None else '',
                'MODELO': captacion.MODELO if getattr(captacion, 'MODELO', None) is not None else '',
                'EN_TRANSITO': (getattr(captacion, 'ETIQUETA', '') or '').upper().startswith('EN_TRANSITO')
            }
            for captacion in captaciones
        ]

        return render_template(
            "inventario/capturas_usuario.html",
            captaciones=captaciones,
            planificacion_id=id_planificacion,
        )
    finally:
        db.close()

@bp.route("/captura/corregir", methods=["POST"])
@requiere_login
def corregir_captura():
    db: Session = request.db
    data = request.get_json()
    error = None
    a_usuario = data.get("usuario")
    a_contrasena = data.get("contrasena")

    # Validar que el usuario ingresado existe
    usuario = db.query(modelo.Usuario).filter(modelo.Usuario.usuario == a_usuario).first()
    if usuario is None:
        return jsonify({"mensaje": "Usuario o contraseña incorrectos.", "error": True}), 400
    
    # Validar contraseña
    contrasena = usuario.contrasena 
    if not check_password_hash(contrasena, a_contrasena):
        return jsonify({"mensaje": "Usuario o contraseña incorrectos.", "error": True}), 400
    
    # Validar que el usuario tiene permiso nivel_4
    if usuario.nivel_4 != 'SI':
        return jsonify({"mensaje": "El usuario no tiene permisos de supervisor para autorizar correcciones.", "error": True}), 403

    # Validación exitosa, proceder con la corrección

    captacion_id = data.get("captacion_id")
    articulo_codigo = data.get("articulo_id")
    print("captacion_id")
    print(captacion_id)
    print("articulo_codigo")
    print(articulo_codigo)
    filtered_captacion = db.query(modelo.CaptacionFisica).filter(
        modelo.CaptacionFisica.ID == captacion_id,
        modelo.CaptacionFisica.ARTICULO == articulo_codigo
    ).first()

    if not filtered_captacion:
        return jsonify({"mensaje": "No se encontró la captación con los parámetros proporcionados", "error": True}), 400

    try:
        filtered_captacion.CANTIDAD = data.get("nueva_cantidad")
        db.commit()
        flash("Captación corregida exitosamente", "success")
        return jsonify({"mensaje": "Captación corregida exitosamente", "error": False}), 200
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        db.rollback()
        return jsonify({"mensaje": str(err), "error": True}), 500
    finally:
        db.close()

# TODO: HAY QUE MOVER ESTA FUNCION A UN BLUEPRINT DE ESTADOS
@bp.route("/estados",methods=['GET'])
@requiere_login
def estados():
    """
    Esta funcion se encarga de obtener los estados para clasificar los articulos
    """
    try:
        db: Session = request.db
        estados = db.query(modelo.Estado).all()
        estados = [{"CODIGO":estado.ESTADO,"DESCRIPCION":estado.DESCRIPCION} for estado in estados]
        return jsonify({'DATOS':estados,"RESPUESTA":"OK"})
    finally:
        db.close()

@bp.route("/articulo/<id>",methods=['POST'])
@requiere_login
def articulo(id):
    """
    Esta funcion retorna la descripcion del articulo cuando el usuario ingresa un codigo
    """
    db: Session = request.db
    print(id)
    json_data = request.get_json()
    print(json_data)
    try:
        articulo = db.query(modelo.Articulo).filter(modelo.Articulo.ARTICULO == id).first()
        dato = {"CODIGO": articulo.ARTICULO, "DESCRIPCION": articulo.DESCRIPCION}
        return jsonify({'mensaje': dato, "error": False})
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()

@bp.route("/articulo/nuevo/<id>",methods=['POST'])
@requiere_login
def articulo_nuevo(id):
    """
    Esta funcion se encarga de crear un nuevo articulo
    """
    db: Session = request.db
    json_data = request.get_json()
    print(json_data)
    try:
        # Verificar si el articulo ya existe
        articulo_existente = db.query(modelo.Articulo).filter(modelo.Articulo.ARTICULO == id).first()
        if articulo_existente:
            return make_response(jsonify({"mensaje": "El artículo ya existe", "error": True}), 400)
        dato = {"CODIGO": id, "DESCRIPCION": ""}
        return jsonify({'mensaje': dato, "error": False})
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()
    
@bp.route("/ubicacion/<id>",methods=['POST'])
@requiere_login
def ubicacion(id):
    """
    Esta funcion en base al articulo y ubicacion que viene en el json
    obtiene los almacenes que tiene ese articulo en esa ubicacion,
    esto se hace cuando el usuario selecciona un articulo y una ubicacion en la vista
    """
    db: Session = request.db
    json_data = request.get_json()
    print(json_data)
    try:
        filtro = json_data.get('FILTRO', {})
        articulo = filtro.get('ARTICULO', '')
        ubicacion = filtro.get('UBICACION', '')
        almacenes = db.query(modelo.Existencia.ALMACEN).filter(
            modelo.Existencia.ARTICULO == articulo,
            modelo.Existencia.UBICACION == ubicacion
        ).group_by(modelo.Existencia.ALMACEN).all()
        almacenes_json = [{"CODIGO": almacen.ALMACEN, "DESCRIPCION": almacen.ALMACEN} for almacen in almacenes if almacen.ALMACEN is not None]
        dato = {"ALMACEN": almacenes_json}
        return jsonify({'mensaje': dato, "error": False})
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()
    
@bp.route("/almacen/<id>",methods=['POST'])
@requiere_login
def almacen(id):
    db: Session = request.db
    json_data = request.get_json()
    print(json_data)
    try:
        filtro = json_data.get('FILTRO', {})
        articulo = filtro.get('ARTICULO', '')
        ubicacion = filtro.get('UBICACION', '')
        lotes = db.query(
            modelo.Existencia.LOTE
        ).filter(
            modelo.Existencia.ARTICULO == articulo,
            modelo.Existencia.UBICACION == ubicacion,
            modelo.Existencia.ALMACEN == id
        ).group_by(
            modelo.Existencia.LOTE
        ).all()
        lotes_json = [{"CODIGO": lote.LOTE, "DESCRIPCION": lote.LOTE} for lote in lotes if lote.LOTE is not None]
        dato = {"LOTES": lotes_json}
        return jsonify({'mensaje': dato, "error": False})
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()
    
@bp.route("/lote/",methods=['POST'])
@requiere_login
def lote():
    db: Session = request.db
    json_data = request.get_json()
    print(json_data)
    try:
        filtro = json_data.get('FILTRO', {})
        articulo = filtro.get('ARTICULO', '')
        ubicacion = filtro.get('UBICACION', '')
        almacen = filtro.get('ALMACEN', '')
        lote = filtro.get('LOTE', '')
        fechas_de_expiracion = db.query(
            modelo.Existencia.FECHA_EXPIRACION
        ).filter(
            modelo.Existencia.ARTICULO == articulo,
            modelo.Existencia.UBICACION == ubicacion,
            modelo.Existencia.ALMACEN == almacen,
            modelo.Existencia.LOTE == lote
        ).group_by(
            modelo.Existencia.FECHA_EXPIRACION
        ).all()
        print("fechas_de_expiracion")
        print(fechas_de_expiracion)
        fechas_de_expiracion_json = [{"CODIGO": str(fecha.FECHA_EXPIRACION.date().strftime('%d/%m/%Y')), "DESCRIPCION": str(fecha.FECHA_EXPIRACION.date().strftime('%d/%m/%Y'))} for fecha in fechas_de_expiracion if fecha.FECHA_EXPIRACION is not None]
        dato = {"FECHAS_EXPIRACION": fechas_de_expiracion_json}
        return jsonify({'mensaje': dato, "error": False})
    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()

#__________________________ CAPTURA ____________________________________
@bp.route("/captura/<id_planificacion>",methods=['POST'])
@requiere_login
def guardar_captura(id_planificacion):
    """
    Esta funcion se encarga de guardar la captacion fisica
    """
    db: Session = request.db
    etiqueta = None

    """Cuando se envía un archivo, normalmente se utiliza un objeto FormData que codifica los 
    datos en formato multipart/form-data. Si se establece manualmente el header Content-Type como 
    "application/json", esto impide que el navegador configure correctamente el formato multipart, 
    ya que "application/json" es para datos en formato JSON."""

    planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
    redirect_url = _ruta_selector_por_modo(True, False, False)
    if planificacion is None:
        return make_response(jsonify({"mensaje": "Planificación no encontrada", "error": True, "redirect": redirect_url}), 404)
    if planificacion.ESTADO == "ARCHIVADO":
        return make_response(jsonify({"mensaje": "Error: La planificación se encuentra archivada", "error": True, "redirect": redirect_url}), 400)

    # Se obtiene el archivo de la solicitud
    file = request.files.get('file')
    file_data = None
    if file:
        file_data = file.read()
        # Comprimir imagen si es necesario (>2MB)
        file_data = compress_image_if_needed(file_data)

    # Se obtiene el JSON de la solicitud
    json_data = request.form.get('json')
    json_data = json.loads(json_data)
    print("JSON:",json_data)
    print("ARTICULO: ",json_data["ARTICULO"])
    print("UBICACION: ",json_data["UBICACION"])
    print("UBICACION: ",json_data["ALMACEN"])
    print("LOTE: ",json_data["LOTE"])
    print("FECHA_EXPIRACION: ",json_data["FECHA_EXPIRACION"])
    print("ESTADO: ",json_data["ESTADO"])
    print("SERIE: ", json_data.get("SERIE"))
    print("MODELO: ", json_data.get("MODELO"))

    en_transito = _to_bool(json_data.get("EN_TRANSITO"))
    json_data["EN_TRANSITO"] = en_transito
    observacion = (json_data.get("OBSERVACION") or "").strip()
    if len(observacion) > 50:
        observacion = observacion[:50]
    json_data["OBSERVACION"] = observacion

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    if file:
        filename = file.filename.lower()
        if '.' not in filename or filename.rsplit('.', 1)[1] not in allowed_extensions:
            return make_response(jsonify({"mensaje": "Error: Solo se permiten formatos de imagen.", "error": True}), 400)
        
    fecha_ingresada = (json_data.get("FECHA_EXPIRACION") or "").strip()
    fecha_normalizada = _parse_fecha_generica(fecha_ingresada)
    if fecha_ingresada and not fecha_normalizada:
        return make_response(jsonify({"mensaje": "Error: La fecha debe tener el formato DD/MM/AAAA", "error": True}), 400)

    if fecha_normalizada:
        json_data["FECHA_EXPIRACION"] = fecha_normalizada.strftime("%Y-%m-%d")

    _aplicar_estado_vencido_si_corresponde(json_data, db)

    if not json_data.get("ESTADO", "").strip() and file:
        return make_response(jsonify({"mensaje": "Error: El estado no puede estar en blanco.", "error": True}), 400)

    if json_data.get("ESTADO", "").strip():
        estados_validos = [estado.ESTADO for estado in db.query(modelo.Estado).all()]
        if json_data["ESTADO"] not in estados_validos:
            return make_response(jsonify({"mensaje": "Error: Estado inválido", "error": True}), 400)

    # Esto representa las categorias, ubicaciones y almacenes planificadas
    articulos_planificados = []
    filtros_de_planificacion  = []
    utils = Utils()
    pais = utils.obtener_pais(db,g)

    articulos_planificados = utils.obtener_planificaciones(db,id_planificacion,pais,'ARTICULO',modelo.Articulo)
    if len(articulos_planificados) > 0:
        articulos_planificados = db.query(
            modelo.Articulo.ARTICULO.label('CODIGO'),
            modelo.Articulo.DESCRIPCION.label("DESCRIPCION")
        ).filter(
            modelo.Articulo.ARTICULO.in_([art.ARTICULO for art in articulos_planificados])
        ).order_by(
            modelo.Articulo.ARTICULO.asc()
        ).all()
        if json_data["ARTICULO"] not in [art.CODIGO for art in articulos_planificados]:
            return make_response(jsonify({"mensaje": "Error: Artículo no planificado.", "error": True}), 400)

    #obtener_planificacion(self, db, id_planificacion, pais, tabla_filtro, modelo,agrupacion = None)
    ubicaciones_planificadas = utils.obtener_planificaciones(db,id_planificacion,pais,'UBICACION',modelo.Ubicacion)
    if( json_data["UBICACION"] not in [ubicacion.UBICACION for ubicacion in ubicaciones_planificadas]):
        return make_response(jsonify({"mensaje": "Error: Ubicacion no planificada","error": True}), 400)
    almacenes_planificados = utils.obtener_planificaciones(db,id_planificacion,pais,'ALMACEN',modelo.Almacen)
    if( json_data["ALMACEN"] not in [almacen.ALMACEN for almacen in almacenes_planificados]):
        return make_response(jsonify({"mensaje": "Error: Almacen no planificado","error": True}), 400)
    
    filtros_de_planificacion = utils.obtener_filtros(db,id_planificacion,pais)

    if len(filtros_de_planificacion) > 0:
        articulos_planificados = utils.obtener_articulos_planificados(db,filtros_de_planificacion,id_planificacion)
        if(json_data["ARTICULO"] not in [articulo.CODIGO for articulo in articulos_planificados]):
            return make_response(jsonify({"mensaje": "Error: Articulo no planificado","error": True}), 400)
    
    if json_data["FECHA_EXPIRACION"] and not json_data["LOTE"]:
        return make_response(jsonify({"mensaje": "Error: FECHA_EXPIRACION debe contener un LOTE", "error": True}), 400)
    print(json_data["CANTIDAD"])
  
    if not en_transito and json_data.get("LOTE", "").strip() != "":
        etiqueta = generar_etiqueta(json_data["LOTE"], json_data["FECHA_EXPIRACION"])

    print("etiqueta:")
    print(etiqueta)

    mensaje = {
        "ARTICULO": json_data["ARTICULO"],
        "DESCRIPCION": json_data["DESCRIPCION"],
        "CANTIDAD": json_data["CANTIDAD"],
        "UBICACION": json_data["UBICACION"],
        "ALMACEN": json_data.get("ALMACEN"),
        "LOTE": json_data.get("LOTE"),
        "SERIE": json_data.get("SERIE"),
        "MODELO": json_data.get("MODELO"),
        "FECHA": json_data["FECHA"],
        "EN_TRANSITO": en_transito,
        "OBSERVACION": observacion,
    }

    try:
        if json_data["LOTE"] == "":
            json_data["LOTE"] = None
        if json_data["FECHA_EXPIRACION"] == "":
            json_data["FECHA_EXPIRACION"] = None
        if json_data["ESTADO"] == "":
            json_data["ESTADO"] = None
        if json_data.get("SERIE", "") == "":
            json_data["SERIE"] = None
        if json_data.get("MODELO", "") == "":
            json_data["MODELO"] = None
        
        if en_transito:
            etiqueta = "EN_TRANSITO"

        # Obtener la fecha según la zona horaria del usuario
        timezone_str = parse_timezone_from_request(json_data)
        fecha_captura = get_user_date(timezone_str)

        captacion = modelo.CaptacionFisica(
            ID_PLANIFICACION=id_planificacion,
            ARTICULO=json_data["ARTICULO"],
            DESCRIPCION=json_data["DESCRIPCION"],
            UBICACION=json_data["UBICACION"],
            ALMACEN=json_data["ALMACEN"],
            LOTE=json_data["LOTE"],
            FECHA_EXPIRACION=json_data["FECHA_EXPIRACION"],
            ETIQUETA=etiqueta,
            FECHA=fecha_captura, 
            CANTIDAD=json_data["CANTIDAD"],
            USUARIO=g.user.usuario,
            ESTADO=json_data["ESTADO"],
            IMAGEN=file_data,
            SERIE=json_data.get("SERIE"),
            MODELO=json_data.get("MODELO"),
            OBSERVACION=observacion or None,
        )

        _marcar_planificacion_en_inventario(db, planificacion, "[captura] ")

        db.add(captacion)
        print("[DEBUG][captura] captacion agregada, realizando commit...")
        db.commit()
        print("[DEBUG][captura] commit completado correctamente")
        return jsonify({'mensaje': "Guardado",'OBJETO':mensaje, "error": False})

    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()
    
#_______________________________ RECONTEO ____________________________________
@bp.route("/reconteo/<id_planificacion>",methods=['POST'])
@requiere_login
@role_required(['nivel_3'])
def guardar_reconteo(id_planificacion):
    """
    Esta funcion se encarga de guardar la captacion fisica
    """
    db: Session = request.db
    etiqueta = None

    planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
    redirect_url = _ruta_selector_por_modo(False, True, False)
    if planificacion is None:
        return make_response(jsonify({"mensaje": "Planificación no encontrada", "error": True, "redirect": redirect_url}), 404)
    if planificacion.ESTADO == "ARCHIVADO":
        return make_response(jsonify({"mensaje": "Error: La planificación se encuentra archivada", "error": True, "redirect": redirect_url}), 400)

    """Cuando se envía un archivo, normalmente se utiliza un objeto FormData que codifica los 
    datos en formato multipart/form-data. Si se establece manualmente el header Content-Type como 
    "application/json", esto impide que el navegador configure correctamente el formato multipart, 
    ya que "application/json" es para datos en formato JSON."""

    # Se obtiene el archivo de la solicitud
    file = request.files.get('file')
    file_data = None
    if file:
        file_data = file.read()
        # Comprimir imagen si es necesario (>2MB)
        file_data = compress_image_if_needed(file_data)

    # Se obtiene el JSON de la solicitud
    json_data = request.form.get('json')
    json_data = json.loads(json_data)
    print("JSON:",json_data)
    print("ARTICULO: ",json_data["ARTICULO"])
    print("UBICACION: ",json_data["UBICACION"])
    print("UBICACION: ",json_data["ALMACEN"])
    print("LOTE: ",json_data["LOTE"])
    print("FECHA_EXPIRACION: ",json_data["FECHA_EXPIRACION"])
    print("DIFERENCIA: ",json_data["DIFERENCIA"])
    print("TIPO_DIFERENCIA: ",json_data["TIPO_DIFERENCIA"])
    print("SERIE: ", json_data.get("SERIE"))
    print("MODELO: ", json_data.get("MODELO"))
    print("ESTADO: ",json_data["ESTADO"])
    json_data = parsear_json_captura(json_data)

    print("DATOS EXTRAIDOS")
    print(json_data)

    en_transito = _to_bool(json_data.get("EN_TRANSITO"))
    json_data["EN_TRANSITO"] = en_transito

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    if file:
        filename = file.filename.lower()
        if '.' not in filename or filename.rsplit('.', 1)[1] not in allowed_extensions:
            return make_response(jsonify({"mensaje": "Error: Solo se permiten formatos de imagen.", "error": True}), 400)
        
    fecha_ingresada = (json_data.get("FECHA_EXPIRACION") or "").strip()
    fecha_normalizada = _parse_fecha_generica(fecha_ingresada)
    if fecha_ingresada and not fecha_normalizada:
        return make_response(jsonify({"mensaje": "Error: La fecha debe tener el formato DD/MM/AAAA", "error": True}), 400)

    if fecha_normalizada:
        json_data["FECHA_EXPIRACION"] = fecha_normalizada.strftime("%Y-%m-%d")

    _aplicar_estado_vencido_si_corresponde(json_data, db)

    if not json_data.get("ESTADO", "").strip() and file:
        return make_response(jsonify({"mensaje": "Error: El estado no puede estar en blanco si no se suministra un archivo con datos.", "error": True}), 400)

    if json_data.get("ESTADO", "").strip():
        estados_validos = [estado.ESTADO for estado in db.query(modelo.Estado).all()]
        if json_data["ESTADO"] not in estados_validos:
            return make_response(jsonify({"mensaje": "Error: Estado inválido", "error": True}), 400)

    # Esto representa las categorias, ubicaciones y almacenes planificadas
    articulos_planificados = []
    filtros_de_planificacion  = []
    utils = Utils()
    pais = utils.obtener_pais(db,g)

    usuarios_planificados = utils.usuarios_planificados(db,id_planificacion,pais)

    #obtener_planificacion(self, db, id_planificacion, pais, tabla_filtro, modelo,agrupacion = None)
    ubicaciones_planificadas = utils.obtener_planificaciones(db,id_planificacion,pais,'UBICACION',modelo.Ubicacion)
    if( json_data["UBICACION"] not in [ubicacion.UBICACION for ubicacion in ubicaciones_planificadas]):
        return make_response(jsonify({"mensaje": "Error: Ubicacion no planificada","error": True}), 400)
    almacenes_planificados = utils.obtener_planificaciones(db,id_planificacion,pais,'ALMACEN',modelo.Almacen)
    if( json_data["ALMACEN"] not in [almacen.ALMACEN for almacen in almacenes_planificados]):
        return make_response(jsonify({"mensaje": "Error: Almacen no planificado","error": True}), 400)
    
    filtros_de_planificacion = utils.obtener_filtros(db,id_planificacion,pais)

    if len(filtros_de_planificacion) > 0:
        articulos_planificados = utils.obtener_articulos_planificados(db,filtros_de_planificacion)
        if(json_data["ARTICULO"] not in [articulo.CODIGO for articulo in articulos_planificados]):
            return make_response(jsonify({"mensaje": "Error: Articulo no planificado","error": True}), 400)
    
    # Check if FECHA_EXPIRACION is present and LOTE is not
    if json_data["FECHA_EXPIRACION"] and not json_data["LOTE"]:
        return make_response(jsonify({"mensaje": "Error: FECHA_EXPIRACION debe contener un LOTE", "error": True}), 400)
    print(json_data["CANTIDAD"])

    if not en_transito and json_data.get("LOTE", "").strip() != "":
        etiqueta = generar_etiqueta(json_data["LOTE"], json_data["FECHA_EXPIRACION"])

    if en_transito:
        etiqueta = "EN_TRANSITO"
    elif etiqueta is None:
        etiqueta = "RECONTEO"
    else:
        etiqueta = f'RECONTEO_{etiqueta}'

    # print("etiqueta:")
    # print(etiqueta)

    mensaje = {
        "ARTICULO": json_data["ARTICULO"],
        "DESCRIPCION": json_data["DESCRIPCION"],
        "CANTIDAD": json_data["CANTIDAD"],
        "UBICACION": json_data["UBICACION"],
        "ALMACEN": json_data.get("ALMACEN"),
        "LOTE": json_data.get("LOTE"),
        "SERIE": json_data.get("SERIE"),
        "MODELO": json_data.get("MODELO"),
        "FECHA": json_data["FECHA"],
        "EN_TRANSITO": en_transito,
    }

    try:
        if json_data["LOTE"] == "":
            json_data["LOTE"] = None
        if json_data["FECHA_EXPIRACION"] == "":
            json_data["FECHA_EXPIRACION"] = None
        if json_data["ESTADO"] == "":
            json_data["ESTADO"] = None
        if json_data.get("SERIE", "") == "":
            json_data["SERIE"] = None
        if json_data.get("MODELO", "") == "":
            json_data["MODELO"] = None
        
        # Obtener la fecha según la zona horaria del usuario
        timezone_str = parse_timezone_from_request(json_data)
        fecha_reconteo = get_user_date(timezone_str)

        captacion = modelo.CaptacionFisica(
            ID_PLANIFICACION = id_planificacion,
            ARTICULO = json_data["ARTICULO"],
            DESCRIPCION = json_data["DESCRIPCION"],
            UBICACION = json_data["UBICACION"],
            ALMACEN = json_data["ALMACEN"],
            LOTE = json_data["LOTE"],
            FECHA_EXPIRACION = json_data["FECHA_EXPIRACION"],
            ETIQUETA = etiqueta,
            FECHA = fecha_reconteo, 
            CANTIDAD = json_data["CANTIDAD"],
            USUARIO = g.user.usuario,
            ESTADO = json_data["ESTADO"],
            IMAGEN=file_data,
            SERIE=json_data.get("SERIE"),
            MODELO=json_data.get("MODELO"),
        )

        planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
        _marcar_planificacion_en_inventario(db, planificacion, "[reconteo] ")

        db.add(captacion)
        print("[DEBUG][reconteo] captacion agregada, realizando commit...")
        db.commit()
        print("[DEBUG][reconteo] commit completado correctamente")
        return jsonify({'mensaje': "Guardado",'OBJETO':mensaje, "error": False})

    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()
    
#_______________________________ NUEVO ARTICULO ____________________________________
@bp.route("/nuevo/<id_planificacion>",methods=['POST'])
@requiere_login
def guardar_nuevo_articulo(id_planificacion):
    """
    Esta funcion se encarga crear un nuevo artículo
    """
    db: Session = request.db
    etiqueta = None

    planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
    redirect_url = _ruta_selector_por_modo(True, False, True)
    if planificacion is None:
        return make_response(jsonify({"mensaje": "Planificación no encontrada", "error": True, "redirect": redirect_url}), 404)
    if planificacion.ESTADO == "ARCHIVADO":
        return make_response(jsonify({"mensaje": "Error: La planificación se encuentra archivada", "error": True, "redirect": redirect_url}), 400)

    #TODO validar si ya existe

    # Se obtiene el archivo de la solicitud
    file = request.files.get('file')
    file_data = None
    if file:
        file_data = file.read()
        # Comprimir imagen si es necesario (>2MB)
        file_data = compress_image_if_needed(file_data)

    # Se obtiene el JSON de la solicitud
    json_data = request.form.get('json')
    json_data = json.loads(json_data)
    print("JSON:",json_data)
    print("ARTICULO: ",json_data["ARTICULO"])
    print("UBICACION: ",json_data["UBICACION"])
    print("UBICACION: ",json_data["ALMACEN"])
    print("LOTE: ",json_data["LOTE"])
    print("FECHA_EXPIRACION: ",json_data["FECHA_EXPIRACION"])
    print("DIFERENCIA: ",json_data["DIFERENCIA"])
    print("TIPO_DIFERENCIA: ",json_data["TIPO_DIFERENCIA"])
    json_data = parsear_json_captura(json_data)

    print("DATOS EXTRAIDOS")
    print(json_data)

    en_transito = _to_bool(json_data.get("EN_TRANSITO"))
    json_data["EN_TRANSITO"] = en_transito

    # Esto representa las categorias, ubicaciones y almacenes planificadas
    utils = Utils()
    pais = utils.obtener_pais(db,g)

    usuarios_planificados = utils.usuarios_planificados(db,id_planificacion,pais)


    #obtener_planificacion(self, db, id_planificacion, pais, tabla_filtro, modelo,agrupacion = None)
    ubicaciones_planificadas = utils.obtener_planificaciones(db,id_planificacion,pais,'UBICACION',modelo.Ubicacion)
    if( json_data["UBICACION"] not in [ubicacion.UBICACION for ubicacion in ubicaciones_planificadas]):
        return make_response(jsonify({"mensaje": "Error: Ubicacion no planificada","error": True}), 400)
    almacenes_planificados = utils.obtener_planificaciones(db,id_planificacion,pais,'ALMACEN',modelo.Almacen)
    if( json_data["ALMACEN"] not in [almacen.ALMACEN for almacen in almacenes_planificados]):
        return make_response(jsonify({"mensaje": "Error: Almacen no planificado","error": True}), 400)
    
    fecha_ingresada = (json_data.get("FECHA_EXPIRACION") or "")
    fecha_normalizada = _parse_fecha_generica(fecha_ingresada)
    if fecha_ingresada.strip() and not fecha_normalizada:
        return make_response(jsonify({"mensaje": "Error: La fecha debe tener el formato DD/MM/AAAA", "error": True}), 400)

    if fecha_normalizada:
        json_data["FECHA_EXPIRACION"] = fecha_normalizada.strftime("%Y-%m-%d")

    _aplicar_estado_vencido_si_corresponde(json_data, db)

    if json_data.get("ESTADO", "").strip():
        estados_validos = [estado.ESTADO for estado in db.query(modelo.Estado).all()]
        if json_data["ESTADO"] not in estados_validos:
            return make_response(jsonify({"mensaje": "Error: Estado inválido", "error": True}), 400)

    # Check if FECHA_EXPIRACION is present and LOTE is not
    if json_data["FECHA_EXPIRACION"] and not json_data["LOTE"]:
        return make_response(jsonify({"mensaje": "Error: FECHA_EXPIRACION debe contener un LOTE", "error": True}), 400)
    print(json_data["CANTIDAD"])

    if not en_transito and json_data.get("LOTE", "").strip() != "":
        etiqueta = generar_etiqueta(json_data["LOTE"], json_data["FECHA_EXPIRACION"])

    if en_transito:
        etiqueta = "EN_TRANSITO"
    elif etiqueta is None:
        etiqueta = "NUEVO"
    else:
        etiqueta = f'NUEVO_{etiqueta}'

    mensaje = {
        "ARTICULO": json_data["ARTICULO"],
        "DESCRIPCION": json_data["DESCRIPCION"],
        "CANTIDAD": json_data["CANTIDAD"],
        "UBICACION": json_data["UBICACION"],
        "ALMACEN": json_data.get("ALMACEN"),
        "LOTE": json_data.get("LOTE"),
        "SERIE": json_data.get("SERIE"),
        "MODELO": json_data.get("MODELO"),
        "FECHA": json_data["FECHA"],
        "EN_TRANSITO": en_transito,
    }

    try:

        existing_articulo = db.query(modelo.Articulo).filter(modelo.Articulo.ARTICULO == json_data["ARTICULO"]).first()
        if existing_articulo:
            return make_response(jsonify({"mensaje": "Error: El artículo ya existe.", "error": True}), 400)
        nuevo_articulo_obj = modelo.Articulo(
            ARTICULO=json_data["ARTICULO"],
            DESCRIPCION=json_data["DESCRIPCION"]
            # Puedes agregar otros campos necesarios aquí
        )
        db.add(nuevo_articulo_obj)
        db.commit()

        if json_data["LOTE"] == "":
            json_data["LOTE"] = None
        if json_data["FECHA_EXPIRACION"] == "":
            json_data["FECHA_EXPIRACION"] = None
        if json_data["ESTADO"] == "":
            json_data["ESTADO"] = None
        if json_data.get("SERIE", "") == "":
            json_data["SERIE"] = None
        if json_data.get("MODELO", "") == "":
            json_data["MODELO"] = None
        
        # Obtener la fecha según la zona horaria del usuario
        timezone_str = parse_timezone_from_request(json_data)
        fecha_nuevo = get_user_date(timezone_str)

        captacion = modelo.CaptacionFisica(
            ID_PLANIFICACION = id_planificacion,
            ARTICULO = json_data["ARTICULO"],
            DESCRIPCION = json_data["DESCRIPCION"],
            UBICACION = json_data["UBICACION"],
            ALMACEN = json_data["ALMACEN"],
            LOTE = json_data["LOTE"],
            FECHA_EXPIRACION = json_data["FECHA_EXPIRACION"],
            ETIQUETA = etiqueta,
            FECHA = fecha_nuevo, 
            CANTIDAD = json_data["CANTIDAD"],
            USUARIO = g.user.usuario,
            ESTADO = json_data["ESTADO"],
            IMAGEN=file_data,
            SERIE=json_data.get("SERIE"),
            MODELO=json_data.get("MODELO"),
        )

        planificacion = db.query(modelo.Planificacion).filter(modelo.Planificacion.ID == id_planificacion).first()
        _marcar_planificacion_en_inventario(db, planificacion, "[nuevo_articulo] ")

        db.add(captacion)
        print("[DEBUG][nuevo_articulo] captacion agregada, realizando commit...")
        db.commit()
        print("[DEBUG][nuevo_articulo] commit completado correctamente")
        return jsonify({'mensaje': "Guardado",'OBJETO':mensaje, "error": False})

    except Exception as err:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
        return make_response(jsonify({"mensaje":str(err),"error":True}), 200)
    finally:
        db.close()

def parsear_json_captura(json_data):
    print("JSON:",json_data)
    print("ARTICULO: ",json_data["ARTICULO"])
    print("UBICACION: ",json_data["UBICACION"])
    print("UBICACION: ",json_data["ALMACEN"])
    print("LOTE: ",json_data["LOTE"])
    print("FECHA_EXPIRACION: ",json_data["FECHA_EXPIRACION"])
    print("CANTIDAD: ",json_data["CANTIDAD"])
    print("DIFERENCIA: ",json_data["DIFERENCIA"])
    print("TIPO_DIFERENCIA: ",json_data["TIPO_DIFERENCIA"])
    if(json_data["DIFERENCIA"] != ''):
        print('if(json_data["DIFERENCIA"] != ''):')
        json_data = extraer_diferencia(json_data)
    return json_data

def extraer_diferencia(json_data):
    """
    Esta funcion se encarga de extraer la diferencia del json
    """
    if json_data["TIPO_DIFERENCIA"] == "POSITIVA":
        print('if json_data["TIPO_DIFERENCIA"] == "POSITIVA":')
        json_data["CANTIDAD"] = json_data["DIFERENCIA"]
    else:
        print('else')
        print(json_data["DIFERENCIA"])
        json_data["CANTIDAD"] = -1 * float(json_data["DIFERENCIA"])
        print("json_data")
        print(json_data)
    return json_data
    
def determine_estado(json_data, lote_fecha):
    new_lote = json_data.get("LOTE", "").strip()
    new_fecha = json_data.get("FECHA_EXPIRACION", "").strip()

    # Buscar registros que tengan el mismo lote
    registros_lote = [r for r in lote_fecha if r.LOTE == new_lote]
    if registros_lote:
        # Si ya existe ese lote, verificar si existe coincidencia de fecha
        for reg in registros_lote:
            print
            if reg.formatted_fecha == new_fecha:
                return "EXISTE"
        # El lote existe pero la fecha es distinta
        return "FECHA_NUEVA"
    else:
        # El lote es nuevo. No importa que new_fecha esté en blanco; esa combinación no existe.
        return "LOTE_FECHA_NUEVA"
    
def existe_lote(lote):
    """
    Esta funcion verifica si el lote existe en la base de datos
    """
    try:
        db: Session = request.db
        lote = db.query(modelo.Existencia).filter(modelo.Existencia.LOTE == lote).first()
        if lote:
            return True
        else:
            return False
    finally:
        db.close()
    
def existe_fecha_de_vencimiento(lote, fecha):
    """
    Esta función verifica si la fecha de vencimiento existe en la base de datos.
    Si 'fecha' es una cadena vacía, se reemplaza por None para evitar errores.
    """
    try:
        db: Session = request.db
        if fecha == "":
            fecha = None
        registro = db.query(modelo.Existencia).filter(
            modelo.Existencia.LOTE == lote,
            modelo.Existencia.FECHA_EXPIRACION == fecha
        ).first()
        return True if registro else False
    finally:
        db.close()

def generar_etiqueta(lote,fecha_vencimiento):
    """
    Este método genera una etiqueta para el lote y la fecha de vencimiento.
    """
    etiqueta = None
    if existe_lote(lote):
        if not existe_fecha_de_vencimiento(lote,fecha_vencimiento):
            etiqueta = "FECHA_NUEVA"
    elif not existe_lote(lote) and fecha_vencimiento == "":
        etiqueta = "LOTE_NUEVO"
    elif not existe_lote(lote) and not existe_fecha_de_vencimiento(lote,fecha_vencimiento):
        etiqueta = "LOTE_FECHA_NUEVA"
    else:
        etiqueta = None
    return etiqueta
