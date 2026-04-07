from disagro_i.conexion_orm import SessionLocal
from sqlalchemy.orm import Session
from flask import request
from disagro_i.clases import modelo
from sqlalchemy import func, or_

class Utils:
    def __init__(self):
        pass
    
    def estan_todas_planificadas(self,tabla,agrupacion,id,pais):
        db: Session = request.db
        try:
            filtro_valor = modelo.Planificacion_linea.VALOR_FILTRO.like('TODAS%')
            if tabla == 'CATEGORIA' and agrupacion == '1':
                existe_todas = db.query(modelo.Planificacion_linea).filter(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == "CATEGORIA_1",
                    filtro_valor,
                    modelo.Planificacion_linea.PLANIFICACION_ID == id
                ).first()
            elif tabla == 'CATEGORIA' and agrupacion == '2':
                existe_todas = db.query(modelo.Planificacion_linea).filter(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == "CATEGORIA_2",
                    filtro_valor,
                    modelo.Planificacion_linea.PLANIFICACION_ID == id
                ).first()
            else:
                existe_todas = db.query(modelo.Planificacion_linea).filter(
                    modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == tabla,
                    filtro_valor,
                    modelo.Planificacion_linea.PLANIFICACION_ID == id
                ).first()

            if existe_todas:
                return True
            return False
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def obtener_planificaciones(self, db, id_planificacion, pais, tabla_filtro, clase,agrupacion = None):
        planificaciones = []
        try:
            if self.estan_todas_planificadas(tabla_filtro, agrupacion, id_planificacion,pais):
                # Si es UBICACION o ALMACEN, obtener desde EXISTENCIA_UBICACION
                if tabla_filtro == 'UBICACION':
                    # Obtener ubicaciones únicas desde EXISTENCIA_UBICACION para esta planificación
                    ubicaciones_ids = db.query(modelo.Existencia.UBICACION).filter(
                        modelo.Existencia.ID_PLANIFICACION == id_planificacion
                    ).distinct().all()
                    ubicaciones_ids = [u.UBICACION for u in ubicaciones_ids]
                    
                    # Obtener los objetos completos de UBICACION con descripción
                    planificaciones = db.query(clase).filter(
                        clase.UBICACION.in_(ubicaciones_ids)
                    ).all()
                    
                elif tabla_filtro == 'ALMACEN':
                    # Obtener almacenes únicos desde EXISTENCIA_UBICACION para esta planificación
                    almacenes_ids = db.query(modelo.Existencia.ALMACEN).filter(
                        modelo.Existencia.ID_PLANIFICACION == id_planificacion
                    ).distinct().all()
                    almacenes_ids = [a.ALMACEN for a in almacenes_ids]
                    
                    # Obtener los objetos completos de ALMACEN con descripción
                    planificaciones = db.query(clase).filter(
                        clase.ALMACEN.in_(almacenes_ids)
                    ).all()
                    
                else:
                    # Para otros casos (CATEGORIA, ARTICULO, etc.) mantener la lógica original
                    planificaciones = db.query(clase).filter(getattr(clase, tabla_filtro) != 'TODAS').all()
            else:
                print("ENTRE 3")
                filtro_ids = self.obtener_filtros_id(db, id_planificacion, tabla_filtro, agrupacion)
                planificaciones = db.query(clase).filter(getattr(clase, tabla_filtro).in_(filtro_ids)).all()
            return planificaciones
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def obtener_filtros_id(self, db, id_planificacion, tabla_filtro, agrupacion):
        try:
            if tabla_filtro == 'CATEGORIA':
                tabla_filtro = f'CATEGORIA_{agrupacion}'
            filtro_ids = [linea.VALOR_FILTRO for linea in db.query(modelo.Planificacion_linea)
                            .filter(modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == tabla_filtro,
                                    modelo.Planificacion_linea.PLANIFICACION_ID == id_planificacion).all()]
            return filtro_ids
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass

    def usuarios_planificados(self, db, id_planificacion,pais):
        usuarios_planificados = []
        try:
            if self.estan_todas_planificadas('USUARIO',None,id_planificacion,pais):
                usuarios_planificados = db.query(modelo.Usuario).filter(modelo.Usuario.nivel_5 == 'SI',modelo.Usuario.pais == pais).all()
            else:
                usuarios_planificados = [planificacion.VALOR_FILTRO for planificacion in db.query(modelo.Planificacion_linea).filter(modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',modelo.Planificacion_linea.PLANIFICACION_ID == id_planificacion).all()]
                usuarios_planificados = db.query(modelo.Usuario).filter(modelo.Usuario.usuario.in_(usuarios_planificados)).all()  
            return usuarios_planificados
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def obtener_pais(self,db,g):
        try:
            query_pais = db.query(modelo.Usuario.pais).filter(modelo.Usuario.usuario == g.user.usuario).first()
            return query_pais.pais
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def planificacion_con_todas(self, db, pais, id_excluido):
        try:
            planificacion_con_todas = db.query(modelo.Planificacion).join(
                modelo.Planificacion_linea,
                modelo.Planificacion_linea.PLANIFICACION_ID == modelo.Planificacion.ID
            ).join(
                modelo.Usuario,
                modelo.Planificacion.USUARIO == modelo.Usuario.usuario
            ).filter(
                modelo.Usuario.pais == pais,
                modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',
                modelo.Planificacion_linea.VALOR_FILTRO == 'TODAS',
                or_(
                    modelo.Planificacion.ESTADO == 'EN_PLANIFICACION',
                    modelo.Planificacion.ESTADO == 'EN_INVENTARIO'
                ),
                modelo.Planificacion.ID != id_excluido
            ).first()
            return True if planificacion_con_todas else False
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def obtener_usuarios_por_valor_filtro(self, db, pais, id_excluido):
        try:
            usuarios_planificacion = db.query(modelo.Planificacion_linea).join(
                modelo.Planificacion,
                modelo.Planificacion_linea.PLANIFICACION_ID == modelo.Planificacion.ID
            ).join(
                modelo.Usuario,
                modelo.Planificacion.USUARIO == modelo.Usuario.usuario
            ).filter(
                modelo.Usuario.pais == pais,
                modelo.Planificacion_linea.NOMBRE_TABLA_FILTRO == 'USUARIO',
                or_(
                    modelo.Planificacion.ESTADO == 'EN_PLANIFICACION',
                    modelo.Planificacion.ESTADO == 'EN_INVENTARIO'
                ),
                modelo.Planificacion.ID != id_excluido
            ).all()
            return [u.VALOR_FILTRO for u in usuarios_planificacion]
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def existe_planificacion_activa(self, db, pais, id_excluido):
        try:
            planificacion_activa = db.query(modelo.Planificacion).join(
                modelo.Usuario,
                modelo.Planificacion.USUARIO == modelo.Usuario.usuario
            ).filter(
                modelo.Usuario.pais == pais,
                or_(
                    modelo.Planificacion.ESTADO == 'EN_PLANIFICACION',
                    modelo.Planificacion.ESTADO == 'EN_INVENTARIO'
                ),
                modelo.Planificacion.ID != id_excluido
            ).first()
            return True if planificacion_activa else False
        finally:
            # La sesión request.db se cierra en teardown_request
            pass
    
    def obtener_articulos_planificados(self, db, filtros_de_planificacion, id_planificacion):
        try:
            filtros_de_planificacion = [modelo.Existencia.ID_PLANIFICACION == id_planificacion] + filtros_de_planificacion
            query = db.query(
                modelo.Articulo.ARTICULO.label('CODIGO'),
                modelo.Articulo.DESCRIPCION.label("DESCRIPCION")
            ).join(
                modelo.Existencia,
                modelo.Articulo.ARTICULO == modelo.Existencia.ARTICULO
            ).filter(
                *filtros_de_planificacion
            ).group_by(
                modelo.Articulo.ARTICULO,
                modelo.Articulo.DESCRIPCION
            ).order_by(
                modelo.Articulo.ARTICULO.asc()
            )
            print("Consulta de artículos planificados SQL:", str(db.query(
                modelo.Articulo.ARTICULO.label('CODIGO'),
                modelo.Articulo.DESCRIPCION.label("DESCRIPCION")
            ).join(
                modelo.Existencia,
                modelo.Articulo.ARTICULO == modelo.Existencia.ARTICULO
            ).filter(
                *filtros_de_planificacion
            ).group_by(
                modelo.Articulo.ARTICULO,
                modelo.Articulo.DESCRIPCION,
                modelo.Existencia.ARTICULO
            ).order_by(
                modelo.Existencia.ARTICULO.asc()
            ).statement.compile(compile_kwargs={"literal_binds": True})))
            return query.all()
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass

    def obtener_costos_por_ubicacion_y_almacen(self, db, filtros_de_planificacion, id_planificacion):
        try:
            costos = db.query(
                modelo.Existencia.UBICACION,
                modelo.Existencia.ALMACEN,
                modelo.Existencia.ARTICULO,
                func.avg(modelo.Existencia.COSTO).label("costo_promedio")
            ).filter(
                modelo.Existencia.ID_PLANIFICACION == id_planificacion,
                *filtros_de_planificacion
            ).group_by(
                modelo.Existencia.UBICACION,
                modelo.Existencia.ALMACEN,
                modelo.Existencia.ARTICULO
            ).order_by(
                modelo.Existencia.UBICACION.asc(),
                modelo.Existencia.ALMACEN.asc(),
                modelo.Existencia.ARTICULO.asc()
            ).all()
            return costos
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass

    def obtener_existencias_planificadas(self, db, filtros_de_planificacion,id_planificacion):
        try:
            query_existencias = db.query(
                modelo.Existencia.ARTICULO,
                modelo.Articulo.DESCRIPCION,
                modelo.Existencia.UBICACION,
                modelo.Existencia.ALMACEN,
                modelo.Existencia.LOTE,
                modelo.Existencia.FECHA_EXPIRACION,
                func.sum(modelo.Existencia.CANTIDAD).label("cantidad_existencia"),
                func.avg(modelo.Existencia.COSTO).label("costo_existencia")
            ).join(
                modelo.Articulo, modelo.Articulo.ARTICULO == modelo.Existencia.ARTICULO
            ).filter(
                modelo.Existencia.ID_PLANIFICACION == id_planificacion,
                *filtros_de_planificacion
            ).group_by(
                modelo.Existencia.ARTICULO,
                modelo.Articulo.DESCRIPCION,
                modelo.Existencia.UBICACION,
                modelo.Existencia.ALMACEN,
                modelo.Existencia.LOTE,
                modelo.Existencia.FECHA_EXPIRACION
            ).order_by(
                modelo.Existencia.ARTICULO.asc()
            )
            existencias = query_existencias.all()
            print("Consulta de existencias:")
            print("Consulta de existencias SQL:", str(query_existencias.statement.compile(compile_kwargs={"literal_binds": True})))
            
            return existencias
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
    
    def obtener_filtros(self, db, id_planificacion, pais):
        filtros_de_planificacion = []
        try:
            ubicaciones_planificadas = self.obtener_planificaciones(db,id_planificacion,pais,'UBICACION',modelo.Ubicacion)
            # print("ubicaciones_planificadas")
            # print(ubicaciones_planificadas)
            almacenes_planificados = self.obtener_planificaciones(db,id_planificacion,pais,'ALMACEN',modelo.Almacen)
            # print("almacenes_planificados")
            # print(almacenes_planificados)
            categorias_1_planificadas = self.obtener_planificaciones(db,id_planificacion,pais,'CATEGORIA',modelo.Categoria,'1')
            categorias_2_planificadas = self.obtener_planificaciones(db,id_planificacion,pais,'CATEGORIA',modelo.Categoria,'2')
            articulos_planificados = self.obtener_planificaciones(db,id_planificacion,pais,'ARTICULO',modelo.Articulo)

            if len(ubicaciones_planificadas) > 0:
                filtros_de_planificacion.append(modelo.Existencia.UBICACION.in_([ubicacion.UBICACION for ubicacion in ubicaciones_planificadas]))
            if len(almacenes_planificados) > 0:
                filtros_de_planificacion.append(modelo.Existencia.ALMACEN.in_([almacen.ALMACEN for almacen in almacenes_planificados]))
            if len(categorias_1_planificadas) > 0:
                filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_1.in_([categoria.CATEGORIA for categoria in categorias_1_planificadas]))
            if len(categorias_2_planificadas) > 0:
                filtros_de_planificacion.append(modelo.Articulo.CATEGORIA_2.in_([categoria.CATEGORIA for categoria in categorias_2_planificadas]))
            if len(articulos_planificados) > 0:
                filtros_de_planificacion.append(modelo.Existencia.ARTICULO.in_([articulo.ARTICULO for articulo in articulos_planificados]))

            # print("Filtros de planificacion:")
            # for idx, filtro in enumerate(filtros_de_planificacion, start=1):
            #     print(f"Filtro {idx}: {filtro}")

            return filtros_de_planificacion
        finally:
            # No cerrar request.db aquí; teardown_request gestiona el ciclo de vida
            pass
