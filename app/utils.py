# app/utils.py
"""
Módulo de utilidades

Contiene funciones para:
- Conectar a la base de datos (PostgreSQL) usando SQLAlchemy.
- Crear tablas si no existen.
- Insertar datos en la tabla de archivos subidos.
- Calcular el tamaño de la muestra.
- Obtener el tamaño de la población y datos de clientes.
- Configurar la aplicación (setup_app_config).
"""

import os
import math
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la base de datos (variables de entorno)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("Faltan variables de entorno para la base de datos.")

# Crear la conexión a la base de datos con SQLAlchemy (globalmente)
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def connect_to_database(config: dict):
    """
    Conecta a la base de datos utilizando la configuración proporcionada.
    
    Args:
        config (dict): Diccionario con claves: db_user, db_password, db_host, db_port, db_name.
        
    Returns:
        tuple: (engine, True) si la conexión es exitosa, o (None, False) en caso de error.
    """
    try:
        connection_string = f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"
        eng = create_engine(connection_string)
        with eng.connect() as connection:
            result = connection.execute(text("SELECT current_database()"))
            db_name_actual = result.scalar()
            if db_name_actual == config['db_name']:
                return eng, True
            else:
                st.warning(f"Conectado a {db_name_actual}, pero se esperaba {config['db_name']}.")
                return eng, False
    except Exception as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return None, False

def create_table_if_not_exists(engine, table_name):
    """
    Verifica y crea la tabla 'uploaded_files' si no existe en la base de datos.

    Args:
        engine: Conexión SQLAlchemy.
        table_name (str): Nombre de la tabla a verificar/crear.

    Returns:
        bool: True si la tabla existe o se creó exitosamente, False en caso de error.
    """
    try:
        with engine.connect() as connection:
            query = text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                )
            """)
            exists = connection.execute(query).scalar()
            if not exists:
                create_query = text("""
                    CREATE TABLE IF NOT EXISTS uploaded_files (
                        id SERIAL PRIMARY KEY,
                        file_name VARCHAR(255) NOT NULL,
                        file_content BYTEA NOT NULL,
                        upload_date TIMESTAMP NOT NULL
                    )
                """)
                connection.execute(create_query)
                connection.commit()
        return True
    except Exception as e:
        st.error(f"Error al crear la tabla: {e}")
        return False

def insert_data_into_table(engine, table_name, data):
    """
    Inserta datos en la tabla especificada.

    Args:
        engine: Conexión SQLAlchemy.
        table_name (str): Nombre de la tabla en la que se insertarán los datos.
        data (dict): Diccionario con las llaves 'file_name', 'file_content' y 'upload_date'.

    Returns:
        bool: True si la inserción fue exitosa, False en caso de error.
    """
    try:
        with engine.connect() as connection:
            query = text("""
                INSERT INTO uploaded_files (file_name, file_content, upload_date)
                VALUES (:file_name, :file_content, :upload_date)
            """)
            connection.execute(query, data)
            connection.commit()
        return True
    except Exception as e:
        st.error(f"Error al insertar datos: {e}")
        return False

def calculate_sample_size(population, confidence_level=0.95, margin_of_error=0.05, proportion=0.5):
    """
    Calcula el tamaño de la muestra utilizando la fórmula de muestreo finito.

    Args:
        population (int): Tamaño de la población.
        confidence_level (float): Nivel de confianza (0.95 o 0.99).
        margin_of_error (float): Margen de error permitido.
        proportion (float): Proporción estimada (valor entre 0 y 1).

    Returns:
        int: Tamaño mínimo de la muestra requerido.
    """
    Z = 1.96 if math.isclose(confidence_level, 0.95) else 2.58 if math.isclose(confidence_level, 0.99) else None
    if Z is None:
        raise ValueError("Nivel de confianza no soportado. Use 0.95 o 0.99.")
    
    sample_size = (Z ** 2) * proportion * (1 - proportion) / (margin_of_error ** 2)
    finite_correction = sample_size / (1 + ((sample_size - 1) / population))
    return math.ceil(finite_correction)

def obtener_poblacion():
    """
    Obtiene el tamaño de la población a partir de la tabla 'clientes'.

    Returns:
        int: Número de registros (población) o 0 en caso de error.
    """
    try:
        query = text("SELECT COUNT(*) as population FROM public.clientes")
        with engine.connect() as connection:
            result = connection.execute(query).fetchone()
            return result[0] if result else 0
    except Exception as e:
        st.error(f"Error al obtener población: {e}")
        return 0

def obtener_datos_clientes():
    """
    Obtiene datos agregados de la tabla 'clientes' agrupados por "Tipo de Tarjeta".

    Returns:
        pd.DataFrame: DataFrame con la columna "Tipo de Tarjeta" y el conteo de clientes.
    """
    query = """
    SELECT "Tipo de Tarjeta", COUNT(*) as "Volumen de Clientes" 
    FROM clientes GROUP BY "Tipo de Tarjeta"
    """
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df

def setup_app_config():
    """
    Carga la configuración de la aplicación a partir de un archivo de configuración,
    y establece una configuración base para la conexión a la base de datos.

    Returns:
        dict: Diccionario con la configuración de la base de datos.
    """
    load_dotenv()
    config_path = os.path.join(os.getcwd(), ".streamlit", "config.toml")
    db_config = {
        'db_user': 'app_admin',
        'db_password': 'app_secure_password',
        'db_host': 'localhost',
        'db_port': '5432',
        'db_name': 'visa_db'
    }
    if os.path.exists(config_path):
        st.sidebar.success("Config File Uploaded Successfully")
    else:
        st.sidebar.warning("Archivo de configuración no encontrado")
    
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = False
    if 'engine' not in st.session_state:
        st.session_state.engine = None
    
    return db_config
