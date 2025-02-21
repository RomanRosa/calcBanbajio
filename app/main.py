# app/main.py
import os
import streamlit as st
import logging
import logging.config
import yaml
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configuración básica de logging (fallback)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")
logger.info("Iniciando Calculadora Financiera BanBajio (configuración básica)")

# Intentar cargar configuración detallada de logging desde config/logging_config.yaml
config_path = os.path.join(os.getcwd(), "config", "logging_config.yaml")
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        logging_config = yaml.safe_load(f)
    try:
        logging.config.dictConfig(logging_config)
        logger = logging.getLogger("app")
        logger.info("Configuración detallada de logging cargada correctamente.")
    except Exception as e:
        logger.warning(f"No se pudo cargar la configuración detallada de logging: {e}")

# Importar módulos de negocio y utilidades (usando rutas relativas, WORKDIR es /app)
from utils import (
    connect_to_database,
    create_table_if_not_exists,
    insert_data_into_table,
    calculate_sample_size,
    obtener_poblacion,
    obtener_datos_clientes,
    setup_app_config
)
from manual_analysis import process_octubre
from calculos import BanBajioCalculator
from calc_tools import (
    FinancialCalculationPRIME,
    FinancialCalculationPRIME360,
    CreditCardStats
)
from algoritmos_calc import DBConnector, Algoritmos
from ui import set_custom_styles, set_global_styles, get_logo_img, show_page_content
from navigation import setup_sidebar, perform_search_by_id, perform_show_full_results, run_manual_analysis
from security import require_auth, init_session_state, RateLimiter, SecurityLogger

# Configurar la página de Streamlit
st.set_page_config(page_title="Calculadora Financiera BanBajio", layout="wide")
st.title("Calculadora Financiera BanBajio")

def main_app():
    nav_options, search_by_id_btn, show_full_btn, id_input, generate_full_report_btn = setup_sidebar()
    
    if nav_options.get("Logs"):
        # Supón que show_logs_page se define en navigation o en ui (según convenga)
        from ui import show_logs_page
        show_logs_page()
    elif generate_full_report_btn:
        perform_show_full_results()
    else:
        if nav_options.get("Application"):
            show_page_content("Application")
        elif nav_options.get("Documentation"):
            show_page_content("Documentation")
        elif nav_options.get("About"):
            show_page_content("About")
        elif nav_options.get("Formulas"):
            show_page_content("Formulas")
        else:
            st.markdown("<h2 style='text-align: center;'>Cálculos Financieros</h2>", unsafe_allow_html=True)
            if search_by_id_btn:
                if id_input.strip() == "":
                    st.error("Please enter an ID to search.")
                else:
                    perform_search_by_id(id_input.strip())
            if show_full_btn:
                perform_show_full_results()

if __name__ == "__main__":
    try:
        st.markdown(set_custom_styles(), unsafe_allow_html=True)
        # Inicializar el estado de sesión si aún no existe
        if 'session_initialized' not in st.session_state:
            init_session_state()
            st.session_state.session_initialized = True

        # Forzamos la autenticación por defecto para acceder directamente al menú
        st.session_state["authenticated"] = True
        st.session_state["username"] = "Guest"

        rate_limiter = RateLimiter()
        main_app()
    except Exception as e:
        SecurityLogger.log_security_event(
            "CRITICAL_ERROR",
            st.session_state.get("username", "system"),
            f"Critical application error: {str(e)}",
            False
        )
        st.error(f"Ha ocurrido un error crítico: {e}")
