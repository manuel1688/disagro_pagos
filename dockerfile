FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece las variables de entorno para Flask
ENV FLASK_APP=disagro_i
ENV FLASK_ENV=development

# Variables de entorno para la base de datos
ENV SERVER=disagro_postgres_c
ENV DATABASE=disagro_db
ENV USERNAME=disagro
ENV PASSWORD=disagro2024
ENV PUERTO=5432

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install wheel 

RUN pip install -e .

# Expone el puerto que usarás (en este caso, el 3000)
EXPOSE 3000

# Inicia la aplicación usando el mismo comando que en inicio.sh
CMD ["flask", "run", "--host=0.0.0.0", "--port", "3000"]