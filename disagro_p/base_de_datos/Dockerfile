# Use an official PostgreSQL runtime as a parent image
FROM postgres:13.3

# Set the working directory in the container to /docker-entrypoint-initdb.d
# This is the directory that Postgres runs scripts from during initialization
WORKDIR /docker-entrypoint-initdb.d

# Copy the current directory contents into the container at /docker-entrypoint-initdb.d
COPY . /docker-entrypoint-initdb.d

# Run the rest of the commands as the ``postgres`` user 
# created by the ``postgres-13.3`` image
USER postgres

# Set environment variables
ENV POSTGRES_USER disagro
ENV POSTGRES_PASSWORD disagro2024
ENV POSTGRES_DB disagro_db
 
# Expose port 5432 to the outside world
EXPOSE 5432

# Run the rest of the commands as the ``postgres`` user 
# created by the ``postgres-13.3`` image
USER postgres

# Start PostgreSQL service
CMD ["postgres"]