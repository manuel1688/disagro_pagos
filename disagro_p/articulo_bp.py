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

bp = Blueprint('articulo_bp', __name__, url_prefix='/articulo')

@bp.route("/articulos",methods=['GET'])
@requiere_login
def articulos():
    try:
        db: Session = request.db
        articulos = db.query(modelo.Articulo).all()
        ultima_subida = db.query(modelo.MaestroUpload).filter_by(MAESTRO='ARTICULOS').first()
        return render_template("articulo/articulo.html",usuario = g.user.usuario,articulos = articulos,ultima_subida = ultima_subida)
    finally:
        db.close()

@bp.route("/excel", methods=['GET'])
@requiere_login
def excel():
    try:
        db: Session = request.db
        articulos = db.query(modelo.Articulo).all()
        
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        sheet["A1"] = "ARTICULO"
        sheet["B1"] = "DESCRIPCION"
        sheet["C1"] = "CATEGORIA_1"
        sheet["D1"] = "CATEGORIA_2"

        for i,articulo in enumerate(articulos):
            sheet[f"A{i+2}"] = articulo.ARTICULO
            sheet[f"B{i+2}"] = articulo.DESCRIPCION
            sheet[f"C{i+2}"] = articulo.CATEGORIA_1
            sheet[f"D{i+2}"] = articulo.CATEGORIA_2

        filepath = f'articulos_{date.today()}.xlsx'
        workbook.save(filepath)

        response = make_response()
        response.headers['Content-Disposition'] = f'attachment; filename=categorias_{agrupacion}.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        with open(filepath, 'rb') as file:
            response.data = file.read()
        return response
    finally:
        db.close()
