import json
import datetime 
from datetime import date
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
from flask.helpers import make_response
from werkzeug.exceptions import abort
from disagro_i.auth import requiere_login,role_required
# from disagro_i.clases import ( caja as class_caja, pedido as class_pedido, tienda as class_tienda)
import os
import csv
from io import TextIOWrapper

import sys
from disagro_i.clases import modelo
from disagro_i.conexion_orm import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import asc,desc,update,func
from werkzeug.security import check_password_hash
import requests
import datetime
import time
import base64
import json
import csv
from sqlalchemy.exc import SQLAlchemyError
import openpyxl
from collections import defaultdict
from disagro_i.fecha_hora import get_user_datetime, parse_timezone_from_request

bp = Blueprint('historial_bp', __name__, url_prefix='/historial')

@bp.route("/historiales/filtro",methods=['GET'])
@requiere_login
@role_required(['nivel_1','nivel_2','nivel_3'])
def filtro():
    try:
        db: Session = request.db
        fecha_archivo_expr = func.coalesce(modelo.Planificacion.FECHA_APROBACION, modelo.Planificacion.FECHA)
        historiales = (
            db.query(modelo.Planificacion)
            .filter(modelo.Planificacion.ESTADO == 'ARCHIVADO')
            .order_by(fecha_archivo_expr.desc())
            .limit(10)
            .all()
        )
        start_prefill = request.args.get('start_date', '')
        end_prefill = request.args.get('end_date', '')
        correlativo_prefill = request.args.get('correlativo', '')
        nombre_prefill = request.args.get('nombre_planificacion', '')
        return render_template(
            "historial/filtro_fecha.html",
            usuario=g.user.usuario,
            historiales=historiales,
            start_prefill=start_prefill,
            end_prefill=end_prefill,
            correlativo_prefill=correlativo_prefill,
            nombre_prefill=nombre_prefill,
        )
    finally:
        db.close()

@bp.route("/historiales/archivado", methods=['POST'])
@requiere_login
@role_required(['nivel_1','nivel_2','nivel_3'])
def obtener_archivoados():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    correlativo = request.form.get('correlativo', '').strip()
    nombre_planificacion = request.form.get('nombre_planificacion', '').strip()
    
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        start_date = datetime.datetime.combine(start_date.date(), datetime.time.min)
        end_date = datetime.datetime.combine(end_date.date(), datetime.time.max)
    except (ValueError, TypeError):
        start_date = None
        end_date = None

    try:
        db: Session = request.db
        fecha_archivo_expr = func.coalesce(modelo.Planificacion.FECHA_APROBACION, modelo.Planificacion.FECHA)
        query = db.query(modelo.Planificacion).filter(modelo.Planificacion.ESTADO == 'ARCHIVADO')
        if correlativo:
            query = query.filter(func.upper(modelo.Planificacion.CORRELATIVO) == correlativo.upper())
        if nombre_planificacion:
            query = query.filter(modelo.Planificacion.NOMBRE.ilike(f"%{nombre_planificacion}%"))
        if start_date and end_date:
            query = query.filter(fecha_archivo_expr.between(start_date, end_date))
        elif start_date:
            query = query.filter(fecha_archivo_expr >= start_date)
        elif end_date:
            query = query.filter(fecha_archivo_expr <= end_date)

        historiales = query.order_by(fecha_archivo_expr.desc()).all()
        start_prefill_str = start_date.strftime('%Y-%m-%d') if start_date else (start_date_str or '')
        end_prefill_str = end_date.strftime('%Y-%m-%d') if end_date else (end_date_str or '')
        return render_template(
            "historial/historiales.html",
            usuario=g.user.usuario,
            historiales=historiales,
            filtro_inicio=start_prefill_str,
            filtro_fin=end_prefill_str,
            filtro_correlativo=correlativo,
            filtro_nombre=nombre_planificacion,
        )
    finally:
        db.close()

@bp.route("/estados/complemento",methods=['GET'])
@requiere_login
@role_required(['nivel_1','nivel_2','nivel_3'])
def mostrar_captaciones():
    try:
        db: Session = request.db
        captaciones = obtener_captaciones_con_estado(db)
        return render_template('historial/complemento_estado.html', captaciones=captaciones)
    finally:
        db.close()

def obtener_captaciones_con_estado(db):
    try:
        query = db.query(
            modelo.CaptacionFisica.ARTICULO,
            modelo.CaptacionFisica.DESCRIPCION,
            modelo.CaptacionFisica.UBICACION,
            modelo.CaptacionFisica.ALMACEN,
            modelo.CaptacionFisica.LOTE,
            modelo.CaptacionFisica.FECHA_EXPIRACION,
            modelo.CaptacionFisica.CANTIDAD,
            modelo.Estado.DESCRIPCION.label('ESTADO'),
            modelo.CaptacionFisica.IMAGEN
        ).join(
            modelo.Estado,
            modelo.CaptacionFisica.ESTADO == modelo.Estado.ESTADO
        ).filter(
            modelo.CaptacionFisica.ESTADO.isnot(None),
            modelo.CaptacionFisica.ESTADO != ''
        )
        return query.all()
    finally:
        db.close()

@bp.route("/estados",methods=['GET'])
@requiere_login
@role_required(['nivel_1'])
def estados():
    try:
        db: Session = request.db
        date = datetime.datetime.now()
        resultados = obtener_capturas_por_estado(db)
        data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

        for result in resultados:
            ubicacion = result.UBICACION
            almacen = result.ALMACEN
            lote = result.LOTE
            fecha_expiracion = result.FECHA_EXPIRACION
            estado = result.ESTADO
            total_cantidad = result.total_cantidad
            articulo = result.ARTICULO
            descripcion = result.DESCRIPCION

            data[ubicacion][almacen][lote][estado].append({
                "UBICACION": ubicacion,
                "ALMACEN": almacen,
                "LOTE": lote,
                "FECHA_DE_EXPIRACION": fecha_expiracion,
                "FISICO": total_cantidad,
                "ESTADO": estado,
                "ARTICULO": articulo,
                "DESCRIPCION": descripcion
            })

        datos_estados = {
            "captaciones_por_ubicacion": []
        }

        total_global = 0

        for ubicacion, almacenes in data.items():
            for almacen, lotes in almacenes.items():
                total_ubicacion = 0
                articulos = []
                for lote, estados in lotes.items():
                    for estado, captaciones in estados.items():
                        total_fisico = sum(captacion["FISICO"] for captacion in captaciones)
                        total_ubicacion += total_fisico
                        articulos.append({
                            "ARTICULO": captaciones[0]["ARTICULO"],
                            "DESCRIPCION": captaciones[0]["DESCRIPCION"],
                            "CAPTACIONES": captaciones,
                            "TOTAL_FISICO": total_fisico
                        })
                datos_estados["captaciones_por_ubicacion"].append({
                    "UBICACION": ubicacion,
                    "ALMACEN": almacen,
                    "ARTICULOS": articulos,
                    "TOTAL_UBICACION": total_ubicacion
                })
                total_global += total_ubicacion

        datos_estados["TOTAL_GLOBAL"] = total_global
        return render_template("historial/reporte_reporte_estado.html",usuario = g.user[1],date = date,datos_estados=datos_estados)
    finally:
        db.close()

def obtener_capturas_por_estado(db):
    try:
        query = db.query(
            modelo.CaptacionFisica.UBICACION,
            modelo.CaptacionFisica.ALMACEN,
            modelo.CaptacionFisica.LOTE,
            modelo.CaptacionFisica.FECHA_EXPIRACION,
            modelo.Estado.DESCRIPCION.label('ESTADO'),
            modelo.CaptacionFisica.ARTICULO,
            modelo.CaptacionFisica.DESCRIPCION,
            func.sum(modelo.CaptacionFisica.CANTIDAD).label('total_cantidad')
        ).join(
            modelo.Estado,
            modelo.CaptacionFisica.ESTADO == modelo.Estado.ESTADO
        ).filter(
            modelo.CaptacionFisica.ESTADO.isnot(None),
            modelo.CaptacionFisica.ESTADO != ''
        ).group_by(
            modelo.CaptacionFisica.UBICACION,
            modelo.CaptacionFisica.ALMACEN,
            modelo.CaptacionFisica.LOTE,
            modelo.CaptacionFisica.FECHA_EXPIRACION,
            modelo.Estado.DESCRIPCION,
            modelo.CaptacionFisica.ARTICULO,
            modelo.CaptacionFisica.DESCRIPCION
        )

        resultados = query.all()
        return resultados
    finally:
        db.close()

@bp.route("/agregar/<id_planificacion>", methods=['POST'])
@requiere_login
@role_required(['nivel_1'])
def agregar_historial(id_planificacion):
    db: Session = request.db
    try:
        payload = request.get_json(silent=True) or {}
        firma_digital = (payload.get('firma_digital') or "").strip()
        observaciones = (payload.get('observaciones') or "").strip()

        if not firma_digital:
            return jsonify({
                "mensaje": "Debes ingresar tu firma digital para aprobar el cierre.",
                "error": True
            }), 400

        if g.user is None or not check_password_hash(g.user.contrasena, firma_digital):
            return jsonify({
                "mensaje": "La firma digital no coincide con tus credenciales.",
                "error": True
            }), 400

        id_planificacion = int(id_planificacion)
        planificacion = db.query(modelo.Planificacion).filter_by(ID=id_planificacion).first()
        if not planificacion:
            return jsonify({"mensaje": "Planificación no encontrada.", "error": True}), 404

        planificacion.ESTADO = 'ARCHIVADO'
        planificacion.REPORTE_ESTADO = 'APROBADO'
        planificacion.OBSERVACION_CIERRE = observaciones or None
        planificacion.USUARIO_APROBACION = g.user.usuario
        
        # Usar zona horaria del cliente para la fecha de aprobación
        data = request.get_json() or {}
        timezone_str = parse_timezone_from_request(data)
        fecha_aprobacion = get_user_datetime(timezone_str)
        planificacion.FECHA_APROBACION = fecha_aprobacion.replace(tzinfo=None)

        db.commit()

        mensaje = "Planificación archivada con éxito"
        return jsonify({'mensaje': mensaje, "error": False})
    except SQLAlchemyError as exc:
        db.rollback()
        return jsonify({
            "mensaje": "Ocurrió un error al registrar la aprobación.",
            "error": True
        }), 500
    finally:
        db.close()


@bp.route("/observaciones/<id_planificacion>", methods=['GET'])
@requiere_login
@role_required(['nivel_1','nivel_2','nivel_3','nivel_4'])
def obtener_observacion_planificacion(id_planificacion):
    db: Session = request.db
    try:
        planificacion = db.query(modelo.Planificacion).filter_by(ID=int(id_planificacion)).first()
        if not planificacion:
            return jsonify({"mensaje": "Planificación no encontrada.", "error": True}), 404

        data = {
            "observacion": planificacion.OBSERVACION_CIERRE or "",
            "usuario": planificacion.USUARIO_APROBACION,
            "fecha": planificacion.FECHA_APROBACION.isoformat() if planificacion.FECHA_APROBACION else None,
            "nombre_planificacion": planificacion.NOMBRE,
            "reporte_estado": planificacion.REPORTE_ESTADO,
            "estado_planificacion": planificacion.ESTADO,
            "correlativo": planificacion.CORRELATIVO,
        }
        return jsonify({"error": False, "data": data})
    finally:
        db.close()
