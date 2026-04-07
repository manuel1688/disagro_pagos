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
import openpyxl

bp = Blueprint('almacen_bp', __name__, url_prefix='/almacen')

@bp.route("/almacenes",methods=['GET'])
@requiere_login
@role_required(['nivel_1','super_usuario'])
def almacenes():
    try:
        db: Session = request.db
        util = Utils()
        almacenes = db.query(modelo.Almacen).order_by(modelo.Almacen.ALMACEN).all()
        ultima_subida = db.query(modelo.MaestroUpload).filter_by(MAESTRO = 'ALMACEN').first()
        return render_template("almacen/almacen.html",usuario = g.user.usuario,almacenes = almacenes, ultima_subida = ultima_subida)
    finally:
        db.close()

@bp.route("/excel", methods=['GET'])
@requiere_login
@role_required(['nivel_1','super_usuario'])
def excel_almacen():
    try:
        db: Session = request.db
        almacenes = db.query(modelo.Almacen).all()

        # Crear un nuevo libro de Excel
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Agregar encabezados de columna
        sheet['A1'] = 'ALMACEN'
        sheet['B1'] = 'DESCRIPCION'

        # Agregar datos de las categorías
        for i, almacen in enumerate(almacenes, start=2):
            sheet[f'A{i}'] = almacen.ALMACEN
            sheet[f'B{i}'] = almacen.DESCRIPCION

        # Guardar el libro de Excel
        filepath = f'almacenes.xlsx'
        workbook.save(filepath)

        # Descargar el archivo Excel
        response = make_response()
        response.headers['Content-Disposition'] = f'attachment; filename=almacenes.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        with open(filepath, 'rb') as file:
            response.data = file.read()

        return response
    finally:
        db.close()

@bp.route("/eliminar/<almacen_id>", methods=['POST'])
@requiere_login
@role_required(['super_usuario'])
def eliminar_almacen(almacen_id):
    try:
        db: Session = request.db
        relacion_captacion = db.query(modelo.CaptacionFisica).filter(modelo.CaptacionFisica.ALMACEN == almacen_id).first()
        relacion_existencia = db.query(modelo.Existencia).filter(modelo.Existencia.ALMACEN == almacen_id).first()
        if relacion_captacion or relacion_existencia:
            flash('No se puede eliminar el almacén porque está relacionado con captaciones o existencias.', 'error')
            return redirect(url_for('almacen_bp.almacenes'))
        almacen = db.query(modelo.Almacen).filter(modelo.Almacen.ALMACEN == almacen_id).first()
        if almacen:
            db.delete(almacen)
            db.commit()
            flash('Almacén eliminado correctamente.', 'success')
        else:
            flash('Almacén no encontrado.', 'error')
    except SQLAlchemyError as e:
        db.rollback()
        flash(f'Error al eliminar el almacén: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('almacen_bp.almacenes'))
