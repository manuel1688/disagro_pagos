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

bp = Blueprint('estado_bp', __name__, url_prefix='/estado')

@bp.route("/estados",methods=['GET'])
@requiere_login
def estados():
    try:
        db: Session = request.db
        estados = db.query(modelo.Estado).all()
        ultima_subida = db.query(modelo.MaestroUpload).filter_by(MAESTRO='ESTADO').first()
        return render_template("estado/estado.html",usuario = g.user.usuario,estados = estados,ultima_subida = ultima_subida)
    finally:
        db.close()

@bp.route("/excel", methods=['GET'])
@requiere_login
def excel_estado():
    try:
        db: Session = request.db
        estados = db.query(modelo.Estado).all()

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        sheet["A1"] = "ESTADO"
        sheet["B1"] = "DESCRIPCION"
        
        for i, estado in enumerate(estados):
            sheet[f"A{i+2}"] = estado.ESTADO
            sheet[f"B{i+2}"] = estado.DESCRIPCION

        filepath = f'estados.xlsx'
        workbook.save(filepath)

        response = make_response()
        response.headers['Content-Disposition'] = f'attachment; filename=estados.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        with open(filepath, 'rb') as file:
            response.data = file.read()
        return response
    finally:
        db.close()

