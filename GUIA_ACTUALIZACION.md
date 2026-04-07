Buenas tardes Moises y Valetín

A continuación comparto el procedimiento a seguir para actualizar la aplicación de inventario.

PROCEDIMIENTO DE ACTUALIZACIÓN 

IP SERVIDOR APP: 10.10.202.36

PUERTO APP CALIDAD: 3000

PUERTO APP PRODUCCION:

Pre requisito: solicitar a ciberseguridad internet en el nodo

DIRECTORIO DE CALIDAD: /mnt/container/disagro_inventario/ 


Descargar cambios del repositorio

Ir a la ruta: /mnt/container/disagro_inventario/ y en el archivo dockerfile esta la IP de la base de datos (en caso de requerir)
Guardar los cambios de configuración : git stash save
Descargar cambios: git pull
Ingresar token de seguridad para poder descargar: TOKEN
Restablecer la configuración: git stash pop 

Detener el contenedor actual, eliminar el contenedor actual y la imagen
Detener el contenedor: docker stop disagro_inventario_dev
Eliminar el contenedor: docker rm disagro_inventario_dev
Mostrar las imágenes: docker images
Eliminar la imagen: docker rmi disagro_inventario
Generar una nueva imagen: docker build --tag disagro_inventario .
Crear nuevo contenedor y lanzarlo: docker run -d --name disagro_inventario_dev -p 3000:3000 disagro_inventario