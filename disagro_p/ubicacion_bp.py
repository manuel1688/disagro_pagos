import json
import datetime 
from datetime import date
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
from flask.helpers import make_response
from werkzeug.exceptions import abort
from disagro_i.auth import requiere_login
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
import openpyxl

bp = Blueprint('ubicacion_bp', __name__, url_prefix='/ubicacion')

@bp.route("/ubicaciones",methods=['GET'])
@requiere_login
def ubicaciones():
    try:
        db: Session = request.db
        util = Utils()
        pais = util.obtener_pais(db,g)
        ubicaciones = db.query(modelo.Ubicacion).order_by(modelo.Ubicacion.UBICACION).all()
        ultima_subida = db.query(modelo.MaestroUpload).filter_by(MAESTRO='UBICACION').first()
        return render_template("ubicacion/ubicacion.html",usuario = g.user.usuario,ubicaciones = ubicaciones,ultima_subida = ultima_subida)
    finally:
        db.close()

@bp.route("/excel", methods=['GET'])
@requiere_login
def excel_ubicacion():
    try:
        db: Session = request.db
        ubicaciones = db.query(modelo.Ubicacion).all()

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        sheet['A1'] = "UBICACION"
        sheet['B1'] = "DESCRIPCION"

        for i, ubicacion in enumerate(ubicaciones):
            sheet[f'A{i+2}'] = ubicacion.UBICACION
            sheet[f'B{i+2}'] = ubicacion.DESCRIPCION
            
        # Guardar el libro de Excel
        filepath = f'ubicaciones.xlsx'
        workbook.save(filepath)

        # Descargar el archivo Excel
        response = make_response()
        response.headers['Content-Disposition'] = f'attachment; filename=ubicaciones.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        with open(filepath, 'rb') as file:
            response.data = file.read()

        return response
    finally:
        db.close()

@bp.route("/eliminar/<ubicacion_id>", methods=['POST'])
@requiere_login
def eliminar_ubicacion(ubicacion_id):
    try:
        db: Session = request.db
        relacion_captacion = db.query(modelo.CaptacionFisica).filter(modelo.CaptacionFisica.UBICACION == ubicacion_id).first()
        relacion_existencia = db.query(modelo.Existencia).filter(modelo.Existencia.UBICACION == ubicacion_id).first()
        if relacion_captacion or relacion_existencia:
            flash("No se puede eliminar la ubicación porque tiene registros relacionados.", "error")
            return redirect(url_for('ubicacion_bp.ubicaciones'))
        
        ubicacion = db.query(modelo.Ubicacion).filter(modelo.Ubicacion.UBICACION == ubicacion_id).first()
        if ubicacion:
            db.delete(ubicacion)
            db.commit()
            flash("Ubicacion eliminada exitosamente.", "success")
        else:
            flash("Ubicacion no encontrada.", "error")
    except SQLAlchemyError as e:
        db.rollback()
        flash(f"Error al eliminar la ubicaci��n: {str(e)}", "error")
    finally:
        db.close()
    return redirect(url_for('ubicacion_bp.ubicaciones'))
