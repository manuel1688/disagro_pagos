# Eliminar la network "mynetwork" si existe
docker network rm mynetwork || true

# Crea la red personalizada (si ya existe, se ignora el error)
docker network create mynetwork || true

# Construye la imagen a partir del Dockerfile ubicado en disagro_i/base_de_datos
docker build -t disagro_db_postgres .

# Ejecuta el contenedor de Postgres en la red "mynetwork", mapeando el puerto 5432
docker run --name postgres --network mynetwork -p 5432:5432 -d disagro_db_postgres

# Validar el log 
docker logs postgres