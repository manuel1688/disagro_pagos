import csv
from datetime import datetime
from sqlalchemy.orm import Session
from disagro_i.conexion_orm import SessionLocal
from disagro_i.clases.modelo import Existencia

def cargar_csv_a_existencia():
    try:
        # Ruta del archivo CSV
        archivo_csv = "EXISTENCIA_UBICACION_DATA.csv"

        # Abrir conexión a la base de datos
        db: Session = SessionLocal()

        # Iniciar transacción
        with db.begin():
            try:
                # Leer el archivo CSV
                with open(archivo_csv, mode='r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Manejar valores vacíos en FECHA_EXPIRACION
                        if row['FECHA_EXPIRACION'].strip():
                            # Solución 1: Ajustar el formato para incluir milisegundos
                            fecha_expiracion = datetime.strptime(row['FECHA_EXPIRACION'], '%Y-%m-%d %H:%M:%S.%f')
                            # O usar Solución 2: Eliminar los milisegundos
                            # fecha_expiracion = datetime.strptime(row['FECHA_EXPIRACION'].split('.')[0], '%Y-%m-%d %H:%M:%S')
                        else:
                            fecha_expiracion = None  # O usa una fecha predeterminada como datetime(1970, 1, 1)

                        # Crear un nuevo registro
                        nueva_existencia = Existencia(
                            ARTICULO=row['ARTICULO'],
                            ID_PLANIFICACION=int(row['ID_PLANIFICACION']),
                            UBICACION=row['UBICACION'],
                            ALMACEN=row['ALMACEN'],
                            CANTIDAD=float(row['CANTIDAD']),
                            COSTO=float(row['COSTO']) if row['COSTO'].strip() else 0.0,  # Manejar valores vacíos en COSTO
                            LOTE=row['LOTE'],
                            FECHA_EXPIRACION=fecha_expiracion
                        )
                        db.add(nueva_existencia)

            except FileNotFoundError as fnf_error:
                raise FileNotFoundError(f"El archivo CSV no se encontró en la ruta especificada: {archivo_csv}. Detalles: {fnf_error}")
            except ValueError as value_error:
                raise ValueError(f"Error al procesar los datos del archivo CSV. Verifica el formato de los datos. Detalles: {value_error}")
            except Exception as e:
                raise Exception(f"Error inesperado al procesar el archivo CSV. Detalles: {e}")

            # Confirmar los cambios
            db.commit()
            print("Datos cargados exitosamente.")

    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except ValueError as value_error:
        print(f"Error: {value_error}")
    except Exception as e:
        print(f"Ocurrió un error inesperado, se realizó un rollback: {e}")
        db.rollback()

    finally:
        # Cerrar la conexión
        db.close()

if __name__ == "__main__":
    cargar_csv_a_existencia()

# comando de ejecución:
# env SERVER=0.0.0.0 DATABASE=disagro_db USERNAME=disagro PASSWORD=disagro2024 PUERTO=5432 FLASK_APP=disagro_i FLASK_ENV=development python migrador_de_existencias.py