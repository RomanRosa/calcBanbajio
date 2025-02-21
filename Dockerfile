# Dockerfile
FROM ubuntu:22.04

#

# Configurar entorno para instalaciones no interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar el sistema e instalar Python3 y pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivo de requerimientos y actualizar pip, e instalar bcrypt y pytz
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install -r /tmp/requirements.txt && \
    pip3 install bcrypt pytz

# Copiar el archivo .env al directorio de trabajo
COPY .env /app/.env

# Configurar el directorio de trabajo y copiar el código completo de la aplicación
WORKDIR /app
COPY . /app

# Exponer el puerto en el que se ejecuta la app (se utilizará el 8502)
EXPOSE 8502

# Comando para ejecutar la aplicación con Streamlit, apuntando a "app/main.py"
CMD ["streamlit", "run", "app/main.py", "--server.enableCORS=false", "--server.port=8502"]
