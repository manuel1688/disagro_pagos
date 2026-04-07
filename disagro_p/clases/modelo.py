from sqlalchemy import Float, Numeric, ForeignKeyConstraint, MetaData, Table, String, Column, Text, DateTime, Boolean, Integer, LargeBinary
from sqlalchemy.orm import mapper
from sqlalchemy.orm import registry
from sqlalchemy import func, ForeignKey

metadata = MetaData()

mapper_registry = registry()
 
categoria = Table( 
    "CATEGORIA",
    metadata,
    Column("CATEGORIA", String(20), primary_key=True),
    Column("DESCRIPCION", String(254), nullable=False),
    Column("AGRUPACION", String(12), nullable=False),
    schema="TOMA_FISICA"
)

class Categoria:
    pass

mapper_registry.map_imperatively(Categoria, categoria)

articulo = Table(
    "ARTICULO",
    metadata,
    Column("ARTICULO", String(20), primary_key=True),
    Column("DESCRIPCION", String(254), nullable=False),
    Column("CATEGORIA_1", String(12), nullable=True),
    Column("CATEGORIA_2", String(12), nullable=True),
    schema="TOMA_FISICA"
)

class Articulo:
    pass

mapper_registry.map_imperatively(Articulo, articulo)

estado = Table(
    "ESTADO",
    metadata,
    Column("ESTADO", String(20), primary_key=True),
    Column("DESCRIPCION", String(254), nullable=False),
    schema="TOMA_FISICA"
)

class Estado:
    pass

mapper_registry.map_imperatively(Estado, estado)

ubicacion = Table(
    "UBICACION",
    metadata,
    Column("UBICACION", String(20), primary_key=True),
    Column("DESCRIPCION", String(254), nullable=False),
    Column("PAIS", String(10), nullable=False),
    schema="TOMA_FISICA"
)

class Ubicacion:
    pass

mapper_registry.map_imperatively(Ubicacion, ubicacion)

almacen = Table(
    "ALMACEN",
    metadata,
    Column("ALMACEN", String(20), primary_key=True),
    Column("DESCRIPCION", String(254), nullable=False),
    Column("PAIS", String(10), nullable=False),
    schema="TOMA_FISICA"
)

class Almacen:
    pass

mapper_registry.map_imperatively(Almacen, almacen)

existencia = Table(
    "EXISTENCIA_UBICACION",
    metadata,
    Column("ID", Integer, primary_key=True),
    Column("ARTICULO", String(20), nullable=False),
    Column("ID_PLANIFICACION", Integer, nullable=False),
    Column("UBICACION", String(20), nullable=False),
    Column("ALMACEN", String(20), nullable=False),
    Column("CANTIDAD", Numeric(15, 3), nullable=False),
    Column("COSTO", Numeric(15, 3), nullable=False),
    Column("LOTE", String(20), nullable=False),
    Column("FECHA_EXPIRACION", DateTime, nullable=False),
    schema="TOMA_FISICA"
)

class Existencia:
    pass

mapper_registry.map_imperatively(Existencia, existencia)

captacion_fisica = Table(
    "CAPTACION_FISICA",
    metadata,
    Column("ID", Integer, primary_key=True),
    Column("ID_PLANIFICACION", Integer, nullable=False),
    Column("ARTICULO", String(20)),
    Column("DESCRIPCION", String(254)),
    Column("UBICACION", String(50)),
    Column("ALMACEN", String(50)),
    Column("LOTE", String(50)),
    Column("FECHA_EXPIRACION", DateTime, nullable=True),
    Column("ETIQUETA", String(50)),
    Column("FECHA", DateTime, nullable=True),
    Column("CANTIDAD", Numeric(15, 3), nullable=False),
    Column("USUARIO", String(50)),
    Column("ESTADO", String(50)),
    Column("IMAGEN", LargeBinary),
    Column("SERIE", String(100)),
    Column("MODELO", String(100)),
    Column("OBSERVACION", String(50)),
    schema="TOMA_FISICA"
)

class CaptacionFisica:
    pass

mapper_registry.map_imperatively(CaptacionFisica, captacion_fisica)

maestro_upload = Table(
    "MAESTRO_UPLOAD",
    metadata,
    Column("MAESTRO", String(20), primary_key=True),
    Column("ULTIMA_SUBIDA", DateTime, nullable=False),
    Column("PAIS", String(10)),
    schema="TOMA_FISICA" 
)

class MaestroUpload:
    pass

mapper_registry.map_imperatively(MaestroUpload, maestro_upload)

planificacion_linea = Table(
    "PLANIFICACION_LINEA",
    metadata,
    Column("ID", Integer, primary_key=True),
    Column("PLANIFICACION_ID", Integer,nullable=False),
    Column("NOMBRE_TABLA_FILTRO", String(50), nullable=False),
    Column("VALOR_FILTRO", String(50), nullable=False),
    schema="TOMA_FISICA"
)

class Planificacion_linea:
    pass

mapper_registry.map_imperatively(Planificacion_linea, planificacion_linea)

planificacion = Table(
    "PLANIFICACION",
    metadata,
    Column("ID", Integer, primary_key=True),
    Column("ESTADO", String(50), nullable=False),
    Column("FECHA", DateTime, nullable=False),
    Column("REPORTE_ESTADO", String(50), nullable=False),
    Column("CORRELATIVO", String(120), nullable=True),
    Column("CORRELATIVO_BASE", String(60), nullable=True),
    Column("FECHA_ACTUALIZACION", DateTime, nullable=True),
    Column("USUARIO", String(100), nullable=False),
    Column("NOMBRE", String(255), nullable=True),
    Column("OBSERVACION_CIERRE", Text, nullable=True),
    Column("USUARIO_APROBACION", String(100), nullable=True),
    Column("FECHA_APROBACION", DateTime, nullable=True),
    schema="TOMA_FISICA"
)

class Planificacion:
    pass

mapper_registry.map_imperatively(Planificacion, planificacion)

usuario = Table(
    "usuario",
    metadata,
    Column("id_usuario", Integer, primary_key=True),
    Column("usuario", String(100), nullable=False, unique=True),
    Column("contrasena", String(255), nullable=False),
    Column("nombre", String(255)),
    Column("super_usuario", String(255)),
    Column("nivel_1", String(2)),
    Column("nivel_2", String(2)),
    Column("nivel_3", String(2)),
    Column("nivel_4", String(2)),
    Column("nivel_5", String(2)),
    Column("pais", String(50)),
    schema="TOMA_FISICA"
)
 
class Usuario:
    pass

#¿cual es la diferencia entre declarative_base y map_imperatively?
mapper_registry.map_imperatively(Usuario, usuario)

usuario_ubicacion = Table(
    "USUARIO_UBICACION",
    metadata,
    Column("ID_USUARIO_UBICACION", Integer, primary_key=True, autoincrement=True),
    Column("USUARIO", String(255), nullable=False),
    Column("ID_UBICACION", String(50), nullable=False),
    ForeignKeyConstraint(["USUARIO"], ["usuario.usuario"]),
    ForeignKeyConstraint(["ID_UBICACION"], ["UBICACION.UBICACION"]),
    schema="TOMA_FISICA"
)

class Usuario_ubicacion:
    pass

mapper_registry.map_imperatively(Usuario_ubicacion, usuario_ubicacion)

bitacora = Table(
    "BITACORA",
    metadata,
    Column("ID_BITACORA", Integer, primary_key=True, autoincrement=True),
    Column("ID_USUARIO", String(255), ForeignKey("TOMA_FISICA.usuario.usuario"), nullable=False),
    Column("ACCION", String(255), nullable=False),
    Column("TABLA",String(50), nullable=False),
    Column("FECHA_REGISTRO", DateTime, server_default=func.current_timestamp()),
    Column("DETALLES", Text),
    schema="TOMA_FISICA"
)

class Bitacora:
    pass

mapper_registry.map_imperatively(Bitacora, bitacora)


#  SELECT * FROM "EXISTENCIA_UBICACION" WHERE "ALMACEN" = ''; 

#   SELECT "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION",SUM("CANTIDAD") AS "CANTIDAD" 
#   FROM "EXISTENCIA_UBICACION" WHERE ("LOTE" = '' AND "FECHA_EXPIRACION" IS NULL) AND "UBICACION" = 'A001' --AND "ARTICULO" = '1002000103' 
#   GROUP BY "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION"
#   ORDER BY "ARTICULO","UBICACION","ALMACEN"; 

#     SELECT "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION",SUM("CANTIDAD") AS "CANTIDAD" 
#   FROM "EXISTENCIA_UBICACION" WHERE "LOTE" IS NOT NULL AND "FECHA_EXPIRACION" IS NULL AND "UBICACION" = 'A001' 
#   AND "ARTICULO" IN ('1002000079','1002000103','1002000294','1002001116','1003000518','1101000048')
#   GROUP BY "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION"
#   ORDER BY "ARTICULO","UBICACION","ALMACEN"; 

#   SELECT "ARTICULO","DESCRIPCION" FROM "ARTICULO" WHERE "ARTICULO" IN ('1002000079','1002000103','1002000294','1002001116','1003000518','1101000048');

# 1 FCOYA NO NO NO SI NO NO
# PIN:  3712
# 2 RAYMOND SANTAMARIA SI SI NO NO NO NO
# PIN:  4981
# 3 ANA RIVERA NO NO NO NO SI NO
# PIN:  6408
# 4 JOHSELYNE DE GRACIA NO NO NO NO NO SI
# PIN:  1454
# 5 HECTOR DELGADO NO NO NO NO SI NO
# PIN:  8111
# 6 CARLOS TORRES NO NO NO NO NO NO
# PIN:  7931
# 7 JENNIFFER ROVIRA NO NO SI NO NO NO
# PIN:  9481
# 8 OSCAR RITTER NO NO NO NO NO SI
# PIN:  2932
# 9 EDGARDO MORALES NO NO NO NO NO SI
# PIN:  1188



# SELECT "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION",SUM("CANTIDAD") AS "CANTIDAD" 
# FROM "EXISTENCIA_UBICACION" WHERE "LOTE" IS NOT NULL AND "FECHA_EXPIRACION" IS NULL AND "UBICACION" = 'A005' 
# AND "ARTICULO" IN ('1002000079','1002000103','1002000294','1002001116','1003000518','1101000048')
# GROUP BY "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION"
# ORDER BY "ARTICULO","UBICACION","ALMACEN"; 

# SELECT "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION",SUM("CANTIDAD") AS "CANTIDAD" 
# FROM "EXISTENCIA_UBICACION" WHERE "UBICACION" = 'A005' AND "CANTIDAD" > 0
# AND "ARTICULO" IN ('1002000079','1002000103','1002000294','1002001116','1003000518','1101000048')
# GROUP BY "ARTICULO","UBICACION","ALMACEN","LOTE","FECHA_EXPIRACION"
# ORDER BY "ARTICULO","UBICACION","ALMACEN"; 
    
