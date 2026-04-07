import csv
import base64
from datetime import datetime
from sqlalchemy.orm import Session
from disagro_i.conexion_orm import SessionLocal
from disagro_i.clases.modelo import CaptacionFisica

CSV_PATH = "CAPTACION_FISICA_DATA.csv"

def parse_datetime(value: str):
    if not value or not value.strip():
        return None
    s = value.strip()
    # Try with microseconds, then without fractional seconds
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    # Try ISO fallback
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def parse_float(value: str, default=0.0):
    try:
        return float(value) if value and value.strip() else default
    except Exception:
        return default

def parse_image_field(value: str):
    # If CSV stores base64, decode; otherwise return None
    if not value or not value.strip():
        return None
    s = value.strip()
    try:
        return base64.b64decode(s)
    except Exception:
        # Not base64, ignore or return None
        return None

def cargar_csv_a_captacion():
    db: Session = SessionLocal()
    try:
        with db.begin():
            try:
                with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    count = 0
                    for row in reader:
                        # Normalize keys access (some CSVs may have different casing)
                        def get(k): return row.get(k) or row.get(k.upper()) or row.get(k.lower()) or ""

                        fecha_exp = parse_datetime(get('FECHA_EXPIRACION'))
                        fecha = parse_datetime(get('FECHA'))

                        imagen = parse_image_field(get('IMAGEN'))

                        nueva = CaptacionFisica(
                            # ID is serial in DB; omit to let DB assign
                            ID_PLANIFICACION = int(get('ID_PLANIFICACION') or 0),
                            ARTICULO = get('ARTICULO') or None,
                            DESCRIPCION = get('DESCRIPCION') or None,
                            UBICACION = get('UBICACION') or None,
                            ALMACEN = get('ALMACEN') or None,
                            LOTE = get('LOTE') or None,
                            FECHA_EXPIRACION = fecha_exp,
                            ETIQUETA = get('ETIQUETA') or None,
                            FECHA = fecha,
                            CANTIDAD = parse_float(get('CANTIDAD'), 0.0),
                            USUARIO = get('USUARIO') or None,
                            IMAGEN = imagen,
                            ESTADO = get('ESTADO') or None
                        )
                        db.add(nueva)
                        count += 1
                # commit is implicit with db.begin()
                print(f"Rows processed and inserted: {count}")
            except FileNotFoundError as e:
                raise FileNotFoundError(f"CSV not found: {CSV_PATH}. Details: {e}")
            except Exception as e:
                raise Exception(f"Error processing CSV: {e}")
    except Exception as outer_e:
        print("Transaction failed:", outer_e)
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()

if __name__ == "__main__":
    cargar_csv_a_captacion()

# comando de ejecución:
# env SERVER=0.0.0.0 DATABASE=disagro_db USERNAME=disagro PASSWORD=disagro2024 PUERTO=5432 FLASK_APP=disagro_i FLASK_ENV=development python migrador_de_captaciones.py