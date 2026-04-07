
import sys
from disagro_i.conexion_orm import SessionLocal
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash
from disagro_i.clases import modelo
from disagro_i.error_reporter import ErrorReporter

def main():

    try:
        print(sys.argv)
        if(len(sys.argv) != 3):
            print("Uso: python super_usuario.py <usuario> <contraseña>")
            sys.exit(1)

        db: Session = SessionLocal()
        hash_contrasena = generate_password_hash(sys.argv[2])
        usuario = db.query(modelo.Usuario).filter_by(usuario=sys.argv[1]).first()
        if not usuario:
            usuario = modelo.Usuario(usuario=sys.argv[1],contrasena=hash_contrasena,
                                     nombre=sys.argv[1],super_usuario='SI',nivel_1 = 'SI',
                                     nivel_2 = 'SI',nivel_3 = 'SI',nivel_4 = 'SI', nivel_5 = 'SI',pais='TODOS')
            db.add(usuario)
            db.commit()
            print("Usuario registrado.")
        else:
            print("Usuario existente.")
        db.close()
    except Exception:
        error = ErrorReporter(sys.exc_info())
        error.print_error_info()
       
if __name__ == "__main__":
    main()
