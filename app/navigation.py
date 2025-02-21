# app/navigation.py
import os
import streamlit as st
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# Importar funciones de UI y otros módulos
from ui import set_global_styles, get_logo_img, show_page_content
from utils import connect_to_database, create_table_if_not_exists, insert_data_into_table, setup_app_config
from algoritmos_calc import DBConnector, Algoritmos

# Importar funciones de seguridad si es necesario
from security import require_auth

def select_nav(selected_key):
    nav_keys = ["nav_home", "nav_application", "nav_documentation", "nav_about", "nav_formulas", "nav_logs"]
    for key in nav_keys:
        if key != selected_key:
            st.session_state[key] = False

def setup_sidebar():
    st.markdown(set_global_styles(), unsafe_allow_html=True)
    
    st.sidebar.markdown(
        f"""
        <div class="user-section">
            {get_logo_img()}
            <div style="margin-left: 1rem;">
                <span style="text-transform: capitalize; color: #ffffff;">{st.session_state.username or "Guest"}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.header("Navigation")
    nav_home_btn = st.sidebar.checkbox("🏠 Home", value=True, key="nav_home", on_change=select_nav, args=("nav_home",))
    nav_application_btn = st.sidebar.checkbox("📊 Application", value=False, key="nav_application", on_change=select_nav, args=("nav_application",))
    nav_documentation_btn = st.sidebar.checkbox("📚 Documentation", value=False, key="nav_documentation", on_change=select_nav, args=("nav_documentation",))
    nav_about_btn = st.sidebar.checkbox("ℹ️ About", value=False, key="nav_about", on_change=select_nav, args=("nav_about",))
    nav_formulas_btn = st.sidebar.checkbox("➗ Formulas", value=False, key="nav_formulas", on_change=select_nav, args=("nav_formulas",))
    nav_logs_btn = st.sidebar.checkbox("📜 Logs", value=False, key="nav_logs", on_change=select_nav, args=("nav_logs",))
    
    nav_options = {
        "Home": st.session_state.get("nav_home", True),
        "Application": st.session_state.get("nav_application", False),
        "Documentation": st.session_state.get("nav_documentation", False),
        "About": st.session_state.get("nav_about", False),
        "Formulas": st.session_state.get("nav_formulas", False),
        "Logs": st.session_state.get("nav_logs", False)
    }
    
    if st.sidebar.button("🚪 Log Out", key="logout_button", help="Click to log out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.sidebar.header("Calculations")
    search_by_id_btn = st.sidebar.button("Search By ID", key="search_by_id_button")
    show_full_btn = st.sidebar.button("Show Full Results", key="show_full_button")
    generate_full_report_btn = st.sidebar.button("Generate Full Report", key="generate_full_report_button")
    manual_analysis_btn = st.sidebar.button("Manual Analysis", key="manual_analysis_button")
    
    id_input = st.sidebar.text_input("Enter ID to search", key="search_id_input")
    
    # Ajuste de la bandera para análisis manual
    if search_by_id_btn or show_full_btn or generate_full_report_btn:
        st.session_state.show_manual_analysis = False
    elif manual_analysis_btn:
        st.session_state.show_manual_analysis = True

    # Sección para análisis manual
    if st.session_state.get('show_manual_analysis', False):
        st.sidebar.markdown("### 📊 Manual Analysis")
        st.sidebar.markdown("Sube tus archivos para realizar el análisis manual:")
        st.sidebar.file_uploader("CUENTAS File (Excel/CSV) - OCTUBRE", key="manual_cuentas_oct", type=['xlsx', 'csv'])
        st.sidebar.file_uploader("MOVIMIENTOS File (Excel/CSV) - OCTUBRE", key="manual_movimientos_oct", type=['xlsx', 'csv'])
        st.sidebar.file_uploader("PROMOCIONES File (Excel/CSV) - OCTUBRE", key="manual_promociones_oct", type=['xlsx', 'csv'])
        st.sidebar.markdown("---")
        st.sidebar.file_uploader("CUENTAS File (Excel/CSV) - NOVIEMBRE", key="manual_cuentas_nov", type=['xlsx', 'csv'])
        st.sidebar.file_uploader("MOVIMIENTOS File (Excel/CSV) - NOVIEMBRE", key="manual_movimientos_nov", type=['xlsx', 'csv'])
        st.sidebar.file_uploader("PROMOCIONES File (Excel/CSV) - NOVIEMBRE", key="manual_promociones_nov", type=['xlsx', 'csv'])
        if st.sidebar.button("REALIZAR ANALISIS", key="run_manual_analysis_button"):
            run_manual_analysis()

    # Sección para subir archivos a la BD
    st.sidebar.markdown("### 📁 Upload Files")
    uploaded_file1 = st.sidebar.file_uploader("Archivos - CUENTAS", key="upload_file1")
    uploaded_file2 = st.sidebar.file_uploader("Archivos - MOVIMIENTOS", key="upload_file2")
    uploaded_file3 = st.sidebar.file_uploader("Archivos - PROMOCIONES", key="upload_file3")
    
    if uploaded_file1 or uploaded_file2 or uploaded_file3:
        config = setup_app_config()
        engine, db_connected = connect_to_database(config)
        st.session_state.db_connection = db_connected
        st.session_state.engine = engine
        if db_connected:
            try:
                create_table_if_not_exists(engine, "uploaded_files")
                for uploaded_file in [uploaded_file1, uploaded_file2, uploaded_file3]:
                    if uploaded_file is not None:
                        with engine.connect() as connection:
                            query = text("SELECT COUNT(*) FROM uploaded_files WHERE file_name = :filename")
                            result = connection.execute(query, {"filename": uploaded_file.name})
                            count = result.scalar()
                        if count > 0:
                            st.sidebar.info(f"El archivo {uploaded_file.name} ya existe.")
                        else:
                            file_content = uploaded_file.getvalue()
                            data = {
                                "file_name": uploaded_file.name,
                                "file_content": file_content,
                                "upload_date": datetime.now()
                            }
                            success = insert_data_into_table(engine, "uploaded_files", data)
                            if success:
                                st.sidebar.success(f"Archivo {uploaded_file.name} cargado exitosamente.")
                            else:
                                st.sidebar.error(f"Error al cargar el archivo {uploaded_file.name}.")
            except Exception as e:
                st.sidebar.error(f"Error al cargar archivos: {str(e)}")
        else:
            st.sidebar.error("No se pudo conectar a la base de datos para cargar archivos.")
    
    upload_files_btn = st.sidebar.button("Upload Files to Database", key="upload_files_button")
    if upload_files_btn:
        if uploaded_file1 or uploaded_file2 or uploaded_file3:
            config = setup_app_config()
            engine, db_connected = connect_to_database(config)
            st.session_state.db_connection = db_connected
            st.session_state.engine = engine
            if db_connected:
                try:
                    create_table_if_not_exists(engine, "uploaded_files")
                    for uploaded_file in [uploaded_file1, uploaded_file2, uploaded_file3]:
                        if uploaded_file is not None:
                            with engine.connect() as connection:
                                query = text("SELECT COUNT(*) FROM uploaded_files WHERE file_name = :filename")
                                result = connection.execute(query, {"filename": uploaded_file.name})
                                count = result.scalar()
                            if count > 0:
                                st.sidebar.info(f"El archivo {uploaded_file.name} ya existe en la base de datos.")
                            else:
                                file_content = uploaded_file.getvalue()
                                data = {
                                    "file_name": uploaded_file.name,
                                    "file_content": file_content,
                                    "upload_date": datetime.now()
                                }
                                success = insert_data_into_table(engine, "uploaded_files", data)
                                if success:
                                    st.sidebar.success(f"Archivo {uploaded_file.name} cargado exitosamente.")
                                else:
                                    st.sidebar.error(f"Error al cargar el archivo {uploaded_file.name}.")
                except Exception as e:
                    st.sidebar.error(f"Error al cargar archivos: {str(e)}")
        else:
            st.sidebar.info("Por favor, seleccione al menos un archivo para cargar.")
    
    return nav_options, search_by_id_btn, show_full_btn, id_input, generate_full_report_btn


def run_manual_analysis():
    results_list = []
    import tempfile
    from io import BytesIO

    if (st.session_state.get("manual_cuentas") is not None and
        st.session_state.get("manual_movimientos") is not None and
        st.session_state.get("manual_promociones") is not None):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp1:
            tmp1.write(st.session_state.manual_cuentas.getvalue())
            cuentas_oct_path = tmp1.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp2:
            tmp2.write(st.session_state.manual_movimientos.getvalue())
            movimientos_oct_path = tmp2.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp3:
            tmp3.write(st.session_state.manual_promociones.getvalue())
            promociones_oct_path = tmp3.name

        from manual_analysis import process_octubre
        df_oct = process_octubre(
            cuentas_path=cuentas_oct_path,
            movimientos_path=movimientos_oct_path,
            promociones_path=promociones_oct_path
        )
        st.success("Análisis OCTUBRE completado.")
        results_list.append(df_oct)

    if (st.session_state.get("manual_cuentas_nov") is not None and
        st.session_state.get("manual_movimientos_nov") is not None and
        st.session_state.get("manual_promociones_nov") is not None):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp4:
            tmp4.write(st.session_state.manual_cuentas_nov.getvalue())
            cuentas_nov_path = tmp4.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp5:
            tmp5.write(st.session_state.manual_movimientos_nov.getvalue())
            movimientos_nov_path = tmp5.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp6:
            tmp6.write(st.session_state.manual_promociones_nov.getvalue())
            promociones_nov_path = tmp6.name

        from manual_analysis import process_octubre
        df_nov = process_octubre(
            cuentas_path=cuentas_nov_path,
            movimientos_path=movimientos_nov_path,
            promociones_path=promociones_nov_path
        )
        df_nov["Mes"] = "Noviembre"
        st.success("Análisis NOVIEMBRE completado.")
        results_list.append(df_nov)

    if not results_list:
        st.error("No se encontraron conjuntos completos de archivos para análisis.")
        return

    df_final = results_list[0] if len(results_list) == 1 else pd.concat(results_list, ignore_index=True)

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Analisis Manual")
    output.seek(0)

    st.success("Análisis manual completado exitosamente. Revisa el DataFrame a continuación:")
    st.dataframe(df_final)
    st.download_button(
        label="Descargar Archivo Excel",
        data=output,
        file_name='manual_analysis.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def perform_show_full_results():
    try:
        st.markdown("""
        <style>
        .dataframe-container {
            width: 100% !important;
            max-width: 100% !important;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

        st.info("Cálculos para todos los IDS.")

        from algoritmos_calc import DBConnector, Algoritmos
        db_connector = DBConnector()
        alg = Algoritmos(db_connector)

        st.markdown("#### INTERÉS ORDINARIO")
        df_io = alg.get_interes_ordinario()
        st.dataframe(df_io, use_container_width=True)

        st.markdown("#### SALDO AL CIERRE DE MES")
        df_scme = alg.get_saldo_cierre_mes()
        st.dataframe(df_scme, use_container_width=True)

        st.markdown("#### PAGO PARA NO GENERAR INTERESES")
        df_pngi = alg.get_pago_no_genera_intereses()
        st.dataframe(df_pngi, use_container_width=True)

        st.markdown("#### PAGO MÍNIMO")
        df_pm = alg.get_pago_minimo()
        st.dataframe(df_pm, use_container_width=True)

        st.markdown("#### SALDO AL CORTE")
        df_sac = alg.get_saldo_al_corte()
        st.dataframe(df_sac, use_container_width=True)

        st.markdown("#### INTERÉS DE PROMOCIONES")
        df_ip = alg.get_interes_promocional()
        st.dataframe(df_ip, use_container_width=True)

        st.markdown("#### INTERÉS A FAVOR")
        df_iaf = alg.get_interes_a_favor()
        st.dataframe(df_iaf, use_container_width=True)

        db_connector.close()
    except Exception as e:
        st.error(f"Error during full results calculations: {e}")

def perform_search_by_id(search_id: str):
    try:
        from algoritmos_calc import DBConnector, Algoritmos
        db_connector = DBConnector()
        alg = Algoritmos(db_connector)
        st.markdown(f"<div class='section-title'>Cálculos para ID: {search_id}</div>", unsafe_allow_html=True)
        
        df_io   = alg.get_interes_ordinario(id=int(search_id))
        df_scme = alg.get_saldo_cierre_mes(id=int(search_id))
        df_pngi = alg.get_pago_no_genera_intereses(id=int(search_id))
        df_pm   = alg.get_pago_minimo(id=int(search_id))
        df_sac  = alg.get_saldo_al_corte(id=int(search_id))
        df_ip   = alg.get_interes_promocional(id=int(search_id))
        df_iaf  = alg.get_interes_a_favor(id=int(search_id))
        
        from navigation import display_styled_dataframe
        display_styled_dataframe(df_io,   "INTERÉS ORDINARIO")
        display_styled_dataframe(df_scme, "SALDO AL CIERRE DE MES")
        display_styled_dataframe(df_pngi, "PAGO PARA NO GENERAR INTERESES")
        display_styled_dataframe(df_pm,   "PAGO MÍNIMO")
        display_styled_dataframe(df_sac,  "SALDO AL CORTE")
        display_styled_dataframe(df_ip,   "INTERÉS DE PROMOCIONES")
        display_styled_dataframe(df_iaf,  "INTERÉS A FAVOR")
        
        def get_row(df, id_val):
            if df is not None:
                subset = df[df["id"] == int(id_val)]
                if not subset.empty:
                    return subset.iloc[0]
            return None
        
        row_sac = get_row(df_sac, search_id)
        saldo_al_corte = {}
        if row_sac is not None:
            saldo_al_corte = {
                "Producto": row_sac.get("producto", None),
                "ID Cliente": row_sac.get("id", None),
                "Tipo de cliente": row_sac.get("estatus", None),
                "Mes": row_sac.get("fecha_corte", None),
                "Límite de crédito del producto": row_sac.get("limite_credito", None),
                "Saldo Total": row_sac.get("saldo_cierre", None),
                "Tasa de interes aplicada (%)": None,
                "Tipo de promoción": row_sac.get("tipo", None),
                "Periodo de la promoción": None,
                "Cargos adicionales": None,
                "Número de días del ciclo": None,
                "Fecha de corte": row_sac.get("fecha_corte", None),
                "Fecha última transacción": row_sac.get("fecha_limite_impresa", None),
                "Valor del sistema": row_sac.get("saldo_cierre", None),
                "Valor de la calculadora": None,
                "Diferencia absoluta": None,
                "Diferencia porcentual": None,
                "Grado de la discrepancia": None,
                "Tipo de impacto (severidad)": None,
                "Impacto financiero": None,
                "Clasificación del impacto financiero": None
            }
        
        row_io = get_row(df_io, search_id)
        interes_ordinario = {}
        if row_io is not None:
            interes_ordinario = {
                "Valor del sistema": row_io.get("valor_sistema", None),
                "Valor de la calculadora": row_io.get("valor_calculadora", None),
                "Diferencia absoluta": row_io.get("diferencia_absoluta", None),
                "Diferencia porcentual": row_io.get("diferencia_porcentual", None),
                "Grado de la discrepancia": row_io.get("grado_discrepancia", None),
                "Tipo de impacto (severidad)": row_io.get("tipo_impacto", None),
                "Impacto financiero": row_io.get("impacto_financiero", None)
            }
        
        row_pngi = get_row(df_pngi, search_id)
        pago_no_generar = {}
        if row_pngi is not None:
            pago_no_generar = {
                "Valor del sistema": row_pngi.get("valor_sistema", None),
                "Valor de la calculadora": row_pngi.get("valor_calculadora", None),
                "Diferencia absoluta": row_pngi.get("diferencia_absoluta", None),
                "Diferencia porcentual": row_pngi.get("diferencia_porcentual", None),
                "Grado de la discrepancia": row_pngi.get("grado_discrepancia", None),
                "Tipo de impacto (severidad)": row_pngi.get("tipo_impacto", None),
                "Impacto financiero": row_pngi.get("impacto_financiero", None)
            }
        
        row_pm = get_row(df_pm, search_id)
        pago_minimo = {}
        if row_pm is not None:
            pago_minimo = {
                "Valor del sistema": row_pm.get("valor_sistema", None),
                "Valor de la calculadora": row_pm.get("valor_calculadora", None),
                "Diferencia absoluta": row_pm.get("diferencia_absoluta", None),
                "Diferencia porcentual": row_pm.get("diferencia_porcentual", None),
                "Grado de la discrepancia": row_pm.get("grado_discrepancia", None),
                "Tipo de impacto (severidad)": row_pm.get("tipo_impacto", None),
                "Impacto financiero": row_pm.get("impacto_financiero", None)
            }
        
        row_ip = get_row(df_ip, search_id)
        interes_promociones = {}
        if row_ip is not None:
            interes_promociones = {
                "Valor del sistema": row_ip.get("valor_sistema", None),
                "Valor de la calculadora": row_ip.get("valor_calculadora", None),
                "Diferencia absoluta": row_ip.get("diferencia_absoluta", None),
                "Diferencia porcentual": row_ip.get("diferencia_porcentual", None),
                "Grado de la discrepancia": row_ip.get("grado_discrepancia", None),
                "Tipo de impacto (severidad)": row_ip.get("tipo_impacto", None),
                "Impacto financiero": row_ip.get("impacto_financiero", None)
            }
        
        row_scme = get_row(df_scme, search_id)
        saldo_al_cierre_de_mes = {}
        if row_scme is not None:
            saldo_al_cierre_de_mes = {
                "Valor del sistema": row_scme.get("valor_sistema", None),
                "Valor de la calculadora": row_scme.get("valor_calculadora", None),
                "Diferencia absoluta": row_scme.get("diferencia_absoluta", None),
                "Diferencia porcentual": row_scme.get("diferencia_porcentual", None),
                "Grado de la discrepancia": row_scme.get("grado_discrepancia", None),
                "Tipo de impacto (severidad)": row_scme.get("tipo_impacto", None),
                "Impacto financiero": row_scme.get("impacto_financiero", None)
            }
        
        row_iaf = get_row(df_iaf, search_id)
        intereses_a_favor = {}
        if row_iaf is not None:
            intereses_a_favor = {
                "Valor del sistema": row_iaf.get("valor_sistema", None),
                "Valor de la calculadora": row_iaf.get("valor_calculadora", None),
                "Diferencia absoluta": row_iaf.get("diferencia_absoluta", None),
                "Diferencia porcentual": row_iaf.get("diferencia_porcentual", None),
                "Grado de la discrepancia": row_iaf.get("grado_discrepancia", None),
                "Tipo de impacto (severidad)": row_iaf.get("tipo_impacto", None),
                "Impacto financiero": row_iaf.get("impacto_financiero", None)
            }
        
        resultados = {
            "Saldo al corte": saldo_al_corte,
            "Interés Ordinario": interes_ordinario,
            "Interés de promociones con interés": interes_promociones,
            "Saldo al cierre de mes": saldo_al_cierre_de_mes,
            "Pago para no generar intereses": pago_no_generar,
            "Pago Mínimo": pago_minimo,
            "Intereses a favor (que no se generen)": intereses_a_favor,
            "CAT": None
        }
        
        plantilla_obj.agregar_resultados(search_id, resultados)
        db_connector.close()
        
        from utils import flatten_template_data
        flat_list = flatten_template_data(plantilla_obj.data)
        df_template = pd.DataFrame(flat_list)
        
        st.markdown("<h2>Plantilla Completa Generada</h2>", unsafe_allow_html=True)
        st.dataframe(df_template, use_container_width=True)
        
        csv_data = df_template.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Reporte Completo",
            data=csv_data,
            file_name='reporte_completo.csv',
            mime='text/csv'
        )
    except Exception as e:
        st.error(f"Error durante los cálculos para ID {search_id}: {str(e)}")
        st.error("Detalles del error para debug:")
        st.code(str(e))
