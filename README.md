# disagro_i
# PORTAL

# --------------- Windows -----------------

# CREAR ENTORNO VIRTUAL Y ACTIVAR
python -m venv venv 
.\venv\Scripts\activate

# INSTALAR PROYECTO DEPENDENCIAS
pip install -e .

# RECOMPILAR TAILWINDCSS LOCAL
bash scripts/build_tailwind.sh

# DESPLEGAR EL PROYECTO EN WINDOWS
$env:FLASK_APP = "disagro_i"
$env:FLASK_ENV = "development"
flask run --host localhost --port 3000 

# -----------------------------------------


# ----- Linux|Mac -----

# CREAR ENTORNO VIRTUAL Y ACTIVAR
python -m venv venv 
source venv/bin/activate 

# INSTALAR PROYECTO DEPENDENCIAS
pip install -e .

# DESPLEGAR EL PROYECTO EN LINUX|MAC
export SERVER=localhost
export DATABASE=disagro_db
export USERNAME=disagro
export PASSWORD=disagro2024
export PUERTO=5432
export FLASK_APP=disagro_i
export FLASK_ENV=development
flask run --host localhost --port 3000
----------------------------

env SERVER=localhost DATABASE=disagro_db USERNAME=disagro PASSWORD=disagro2024 PUERTO=5432 FLASK_APP=disagro_i FLASK_ENV=development flask run --host localhost --port 3000

env SERVER=0.0.0.0 DATABASE=disagro_db USERNAME=disagro PASSWORD=disagro2024 PUERTO=5432 FLASK_APP=disagro_i FLASK_ENV=development flask run --host 0.0.0.0 --port 4000

# TailwindCSS
- Archivo fuente: `disagro_p/static/css/tailwind.input.css`
- Archivo compilado: `disagro_p/static/css/tailwind.css`
- Configuración: `tailwind.config.js`
- Binario standalone incluido en el repo: `./tailwindcss`

# CREACION DE SUPER USUARIO

docker exec -it postgres psql -h localhost -p 5432 -U disagro -d disagro_db
docker exec -it disagro_inventario bash

# COMANDO PARA CREAR EL SUPER USUARIO
docker exec -it disagro_inventario python /app/disagro_i/super_usuario.py param1 param2

# COMANDO PARA LANZAR LA CONSOLA DE POSTGRES
docker exec -it 4229dbe27e1d4681ab066d472e48490873b09f1dc98dcd039b6fc6e84f045594 psql -U disagro -d disagro_db


# Recursos del nodo
# server app:
# Red Hat Enterprise Linux 9.4
# RAM 16GB
# Vcpu: 4
# Docker version 28.0.4, build b8034c0


# GPC

#  En la carpeta principal del profecto sobre el dockerfile de flask
sudo docker build -t disagro_flask .

# docker run -d --name disagro_inventario_dev --network disagro_network disagro_flask
sudo docker run -d --name disagro_inventario_dev --network disagro_network -p 3000:3000 disagro_flask


# Base de datos: Postgres
sudo docker build -t disagro_postgres .
sudo docker run -d --name disagro_postgres_dev --network disagro_network -p 5432:5432 disagro_postgres

# Cuando los contenedores estan detenido no dejausar ese nombre para ese se usa el comando
# logras ver los deteneido 
sudo docker ps -a

# Eliminar imagen 
docker image rm -f nombre_imagen

# Postgress
docker build -t disagro_flask_postgres



# ____________################

# Detener el contenedor, eliminarlo y luego eliminar la imagen

docker stop disagro_inventario_dev
docker rm disagro_inventario_dev
docker image rm disagro_flask

# Para borrar la imagen 'disagro_flask'

Si hay algún contenedor en ejecución o detenido que esté basado en esta imagen, primero detén y elimina esos contenedores. Por ejemplo:

docker stop disagro_inventario_dev  
docker rm disagro_inventario_dev  

Una vez sin contenedores asociados, elimina la imagen usando su ID:

docker rmi ef6b78eab032

# 1.
sudo docker stop disagro_flask_c
sudo docker stop disagro_postgres_c

sudo docker rm disagro_flask_c 
sudo docker rm disagro_postgres_c 

# 2.
sudo docker ps -a

# 3.
sudo docker images

# 4.
sudo docker rmi disagro_flask:latest
sudo docker rmi disagro_postgres:latest

# sudo docker rmi 5901a1545b07

# 5.
sudo docker build -t disagro_flask .
sudo docker run -d --name disagro_flask_c --network disagro_network -p 3000:3000 disagro_flask

# 6.
sudo docker exec -it disagro_flask_c bash

# 7.
sudo docker build -t disagro_postgres .
sudo docker run -d --name disagro_postgres_c --network disagro_network -p 5432:5432 disagro_postgres


## Reporte de conteo por usuario

- Disponible desde el catálogo de reportes dentro de una planificación activa, bajo la opción `Conteo por usuario`.
- Requiere seleccionar al menos un usuario captador. También permite incluir registros sin captura marcando la opción `Sin captador`.
- Los filtros de ubicaciones y almacenes aceptan multiselección; al dejarlos vacíos el reporte utiliza todas las ubicaciones/almacenes planificados.
- La tabla principal muestra artículo, descripción, cantidades planificadas vs. contadas, diferencia, últimas fechas de captura y el usuario responsable.
- El panel lateral permite limpiar o restablecer filtros rápidamente y conserva chips removibles para indicar los filtros activos.
- Los resultados pueden descargarse en Excel respetando los filtros aplicados.

## Reporte consolidado cantidades/costo

- Disponible en el catálogo como `Consolidado cantidades/costo`; fusiona los reportes de inventario físico y diferencias por costo.
- Presenta en una sola tabla las columnas de cantidades (físico, sistema, diferencia) y sus equivalentes monetarios.
- Respeta el estilo del reporte original (estructura por ubicación/artículo, totales por sección y formato “waffle”).
- Incluye opción de exportación a Excel con los valores filtrados.

## Reporte inventario con comentarios

- Disponible en el catálogo como `Inventario con comentarios`; replica el reporte básico de diferencias agregando marcadores visuales de observaciones.
- Cada línea de captación muestra un ícono de comentario cuando existen notas registradas; el tooltip expone un resumen rápido y la tabla inferior detalla la información completa.
- El bloque “Comentarios registrados” lista artículo, ubicación, captador, fecha y texto capturado para vincular fácilmente la observación con la línea consolidada.
- El resto de reportes se mantiene sin cambios; el indicador y la tabla adicional solo aparecen en este nuevo reporte.
