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

bp = Blueprint('categoria_bp', __name__, url_prefix='/categoria')

@bp.route("/categorias/<agrupacion>",methods=['GET'])
@requiere_login
def categorias(agrupacion):
    try:
        db: Session = request.db
        categorias = db.query(modelo.Categoria).filter(modelo.Categoria.AGRUPACION == agrupacion).all()
        ultima_subida = db.query(modelo.MaestroUpload).filter_by(MAESTRO='CATEGORIA_1').first()
        return render_template("categoria/categoria.html",usuario = g.user.usuario,categorias = categorias,agrupacion=agrupacion,ultima_subida = ultima_subida)
    finally:
        db.close()

@bp.route("/excel/categoria/<agrupacion>", methods=['GET'])
@requiere_login
def excel_categoria(agrupacion):
    try:
        db: Session = request.db
        categorias = db.query(modelo.Categoria).filter(modelo.Categoria.AGRUPACION == agrupacion).all()

        # Crear un nuevo libro de Excel
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Agregar encabezados de columna
        sheet['A1'] = 'CATEGORIA'
        sheet['B1'] = 'DESCRIPCION'
        sheet['C1'] = 'AGRUPACION'

        # Agregar datos de las categorías
        for i, categoria in enumerate(categorias, start=2):
            sheet[f'A{i}'] = categoria.CATEGORIA
            sheet[f'B{i}'] = categoria.DESCRIPCION
            sheet[f'C{i}'] = f"CATEGORIA - {categoria.AGRUPACION}"

        # Guardar el libro de Excel
        filepath = f'categorias_{agrupacion}.xlsx'
        workbook.save(filepath)

        # Descargar el archivo Excel
        response = make_response()
        response.headers['Content-Disposition'] = f'attachment; filename=categorias_{agrupacion}.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        with open(filepath, 'rb') as file:
            response.data = file.read()
        return response
    finally:
        db.close()
