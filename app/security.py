# app/security.py
import os
import re
import bcrypt
import yaml
import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict

def validate_input(input_str: str, input_type: str) -> bool:
    patterns = {
        'username': r'^[a-zA-Z0-9_]{3,20}$',
        'text': r'^[a-zA-Z0-9\s.,!?-]{1,500}$',
        'number': r'^\d+(\.\d+)?$',
        'date': r'^\d{4}-\d{2}-\d{2}$'
    }
    return bool(re.match(patterns[input_type], input_str)) if input_type in patterns else False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not plain_password or not hashed_password:
            return False
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def load_users(file_path='users.yaml'):
    try:
        if not os.path.exists(file_path):
            st.error(f"Archivo de usuarios no encontrado: {file_path}")
            return {}
        with open(file_path, 'r', encoding='utf-8') as file:
            users = yaml.safe_load(file)
            if not isinstance(users, dict):
                raise ValueError("El archivo de usuarios debe contener un diccionario")
            return users
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")
        return {}

def authenticate(username: str, password: str, users: dict) -> bool:
    return verify_password(password, users[username]['password']) if username in users else False

class SecurityLogger:
    @staticmethod
    def log_security_event(event_type: str, user: str, details: str, success: bool):
        import logging
        status = "SUCCESS" if success else "FAILED"
        logging.info(f"Security Event - Type: {event_type} - User: {user} - Status: {status} - Details: {details}")

class RateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)
        self.blocked_users = defaultdict(lambda: datetime.min)

    def is_rate_limited(self, username: str) -> bool:
        import time
        current_time = time.time()
        if username in self.blocked_users:
            block_time = self.blocked_users[username]
            if datetime.now() < block_time:
                return True
            else:
                del self.blocked_users[username]
        self.attempts[username] = [t for t in self.attempts[username] if current_time - t < self.window_seconds]
        if len(self.attempts[username]) >= self.max_attempts:
            self.blocked_users[username] = datetime.now() + timedelta(minutes=10)
            return True
        self.attempts[username].append(current_time)
        return False

    def is_user_blocked(self, username: str) -> bool:
        if username in self.blocked_users:
            if datetime.now() < self.blocked_users[username]:
                return True
            else:
                del self.blocked_users[username]
        return False

class SessionManager:
    def __init__(self, timeout_minutes: int = 30):
        self.timeout_minutes = timeout_minutes

    def check_session_timeout(self) -> bool:
        if 'last_activity' not in st.session_state:
            return True
        last_activity = st.session_state.last_activity
        if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
            return True
        self.update_last_activity()
        return False

    def update_last_activity(self):
        st.session_state.last_activity = datetime.now()

class UserRoleManager:
    ROLES = {
        'admin': ['all'],
        'analyst': ['view_data', 'run_analysis', 'export_results'],
        'viewer': ['view_data']
    }
    @staticmethod
    def check_permission(required_permission: str) -> bool:
        if 'user_role' not in st.session_state:
            return False
        user_role = st.session_state.user_role
        if user_role == 'admin':
            return True
        return required_permission in UserRoleManager.ROLES.get(user_role, [])

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_manager = SessionManager()
        if not st.session_state.get('authenticated'):
            st.error("Por favor inicie sesión para continuar.")
            return None
        if session_manager.check_session_timeout():
            st.warning("Su sesión ha expirado. Por favor inicie sesión nuevamente.")
            logout()
            return None
        session_manager.update_last_activity()
        return func(*args, **kwargs)
    return wrapper

def logout():
    from security import SecurityLogger
    if 'username' in st.session_state:
        SecurityLogger.log_security_event("LOGOUT", st.session_state.username, "User logged out", True)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def init_session_state():
    """
    Inicializa las variables de sesión necesarias para la aplicación.
    """
    session_vars = {
        'authenticated': False,
        'username': None,
        'data_cuentas_octubre': None,
        'data_movimientos_octubre': None,
        'data_promociones_octubre': None,
        'processed_data': None,
        'db_connection': False,
        'user_role': None,
        'last_activity': None,
        'blocked': False
    }
    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

def login_page(rate_limiter):
    # Importar funciones de UI para estilos y logo
    from ui import set_global_styles, get_logo_img
    st.markdown(set_global_styles(), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="login-container" style="text-align: center; margin-bottom: 2rem;">
            {get_logo_img()}
            <h1>Calculadora de Revisión</h1>
        </div>
        """, unsafe_allow_html=True)
    
    users = load_users()
    if not users:
        SecurityLogger.log_security_event("USER_LOAD", "system", "Failed to load user database", False)
        st.error("Error al cargar usuarios. Contacte al administrador.")
        return

    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    login_disabled = st.session_state.login_attempts >= 3

    with st.form("login_form"):
        username = st.text_input("User", disabled=login_disabled).strip()
        password = st.text_input("Password", type="password", disabled=login_disabled)
        submit = st.form_submit_button("Submit", disabled=login_disabled)
        
        if submit:
            if login_disabled:
                st.error("Has alcanzado el límite de intentos. Contacta al administrador.")
                return
            if rate_limiter.is_user_blocked(username):
                SecurityLogger.log_security_event("LOGIN_BLOCKED", username, "User is blocked due to too many failed attempts", False)
                st.error("Too many attempts. Please contact the administrator.")
                return
            if not validate_input(username, 'username'):
                SecurityLogger.log_security_event("LOGIN_ATTEMPT", username, "Invalid username format", False)
                st.error("Invalid username format")
                return
            if rate_limiter.is_rate_limited(username):
                SecurityLogger.log_security_event("RATE_LIMIT", username, "Too many login attempts", False)
                st.error("Too many attempts. Please contact the administrator.")
                return
            if authenticate(username, password, users):
                SecurityLogger.log_security_event("LOGIN", username, "Successful login", True)
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = users[username].get('role', 'viewer')
                st.session_state.last_activity = datetime.now()
                st.session_state.login_attempts = 0
                st.success("Authorized User", icon="✅")
            else:
                st.session_state.login_attempts += 1
                remaining_attempts = 3 - st.session_state.login_attempts
                SecurityLogger.log_security_event("LOGIN_ATTEMPT", username, "Failed login attempt", False)
                if remaining_attempts > 0:
                    st.error(f"Invalid credentials. Attempts remaining: {remaining_attempts}", icon="❌")
                else:
                    st.error("Exceeded maximum login attempts. Your access is now blocked.", icon="🚫")
