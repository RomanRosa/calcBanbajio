# app/ui.py
import os
import base64
import streamlit as st

def set_custom_styles():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
    .main-content {
        font-family: 'Poppins', sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
        color: #ffffff;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .stDataFrame {
        width: 100% !important;
        padding: 1rem 0;
    }
    .stDataFrame > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    .stDataFrame table {
        width: 100% !important;
    }
    div[data-testid="stDataFrame"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    .dataframe {
        width: 100% !important;
        max-width: none !important;
        margin-bottom: 1rem;
    }
    .dataframe th {
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
        padding: 10px !important;
        text-align: left !important;
    }
    .dataframe td {
        padding: 8px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    [data-testid="stDataFrameResizable"] {
        width: 100% !important;
        max-width: none !important;
    }
    .options-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin: 1.5rem auto;
        max-width: 400px;
    }
    .option-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
        height: 100px;
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .option-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .option-title {
        font-size: 1rem;
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    .option-description {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.7);
        line-height: 1.2;
    }
    .homepage-options-container {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        justify-content: center;
        margin: 1.5rem auto;
        max-width: 800px;
    }
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        border: none;
        font-weight: 500;
        width: 200px;
        margin: 1rem auto;
        display: block;
        font-size: 0.9rem;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #45a049, #4CAF50);
        box-shadow: 0 2px 6px rgba(76, 175, 80, 0.3);
    }
    .section-title {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 1rem;
        border-radius: 5px;
        margin: 1.5rem 0 1rem 0;
        color: white;
        font-weight: 500;
    }
    </style>
    """

def set_global_styles():
    return """
    <style>
    body {
        margin: 0;
        padding: 0;
        background: #31333F;
    }
    .sidebar .block-container {
        padding-top: 2rem;
    }
    </style>
    """ + set_custom_styles()

def get_logo_svg():
    return """
    <svg width="50" height="50" viewBox="0 0 50 50">
        <circle cx="25" cy="25" r="20" fill="#4CAF50"/>
        <text x="25" y="25" text-anchor="middle" fill="white"
              dominant-baseline="middle" style="font-size: 14px;">BB</text>
    </svg>
    """

def get_logo_img():
    # Intenta cargar el logo desde la carpeta images; si no existe, usa un URL predeterminado.
    logo_path = os.path.join(os.getcwd(), "images", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{encoded_string}" width="350" height="80" alt="Logo BanBajío">'
    else:
        logo_url = "https://upload.wikimedia.org/wikipedia/commons/6/69/Logo_de_BanBaj%C3%ADo.svg"
        return f'<img src="{logo_url}" width="200" height="150" alt="Logo BanBajío">'

def show_page_content(page: str):
    """
    Carga y muestra el contenido Markdown de la página solicitada.
    Se espera que los archivos Markdown estén en la carpeta 'docs'.
    """
    mapping = {
        "Application": "application.md",
        "Documentation": "documentation.md",
        "About": "about.md",
        "Formulas": "formulas.md",
        "Logs": "logs.md"  
    }
    if page in mapping:
        md_file = mapping[page]
        # Construir la ruta absoluta a la carpeta docs
        md_path = os.path.join(os.getcwd(), "docs", md_file)
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content, unsafe_allow_html=True)
        else:
            st.error(f"El archivo markdown '{md_file}' no se encontró en la carpeta docs.")
    else:
        st.error("No se ha seleccionado un archivo válido.")
        st.warning("No se ha seleccionado un archivo válido.")
