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

bp = Blueprint('existencia_bp', __name__, url_prefix='/existencia')

@bp.route("/existencias",methods=['GET'])
@requiere_login
def existencias():
    try:
        db: Session = request.db
        existencias = db.query(modelo.Existencia).all()
        ultima_subida = db.query(modelo.MaestroUpload).filter_by(MAESTRO='EXISTENCIAS').first()
        return render_template("existencia/existencia.html",usuario = g.user[1],existencias = existencias,ultima_subida = ultima_subida)
    finally:
        db.close()

@bp.route("/excel", methods=['GET'])
@requiere_login
def excel_existencia():
    try:
        db: Session = request.db
        existencias = db.query(modelo.Existencia).all()

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Existencias"

        # Encabezados
        sheet['A1'] = 'ID'
        sheet['B1'] = 'ID_ARTICULO'
        sheet['C1'] = 'ID_UBICACION'
        sheet['D1'] = 'ID_ESTADO'
        sheet['E1'] = 'CANTIDAD'
        sheet['F1'] = 'FECHA_CREACION'
        sheet['G1'] = 'FECHA_MODIFICACION'
        sheet['H1'] = 'USUARIO_CREACION'
        sheet['I1'] = 'USUARIO_MODIFICACION'

        # Datos
        for i, existencia in enumerate(existencias, start=2):
            sheet[f'A{i}'] = existencia.ID
            sheet[f'B{i}'] = existencia.ID_ARTICULO
            sheet[f'C{i}'] = existencia.ID_UBICACION
            sheet[f'D{i}'] = existencia.ID_ESTADO
            sheet[f'E{i}'] = existencia.CANTIDAD
            sheet[f'F{i}'] = existencia.FECHA_CREACION
            sheet[f'G{i}'] = existencia.FECHA_MODIFICACION
            sheet[f'H{i}'] = existencia.USUARIO_CREACION
            sheet[f'I{i}'] = existencia.USUARIO_MODIFICACION

        response = make_response(openpyxl.writer.excel.save_virtual_workbook(workbook))
        response.headers['Content-Disposition'] = 'attachment; filename=existencias.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response
    finally:
        db.close()