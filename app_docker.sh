# COMANDO PARA CREAR IMAGEN Y CONTENEDOR
docker build -t disagro_inventario .  
# COMANDO PARA CREAR RED Y CONTENEDOR
docker run --name disagro_inventario --network mynetwork -p 3000:3000 disagro_inventario

