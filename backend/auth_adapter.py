"""
Adaptador para streamlit-authenticator
Simulador BIC Lankamar

Este módulo conecta el sistema de auth SQLite con streamlit-authenticator,
permitiendo usar la librería existente pero con datos desde la base de datos.
"""

import streamlit_authenticator as stauth
from typing import Tuple, Dict
from auth_service import list_users, get_user_by_email


def build_credentials_dict() -> Dict:
    """
    Construye el diccionario de credenciales en el formato
    esperado por streamlit-authenticator, pero desde SQLite
    
    Returns:
        Dict con estructura:
        {
            "usernames": {
                "email@example.com": {
                    "email": "email@example.com",
                    "name": "Nombre",
                    "password": "$2b$12$...",  # hash bcrypt
                    "role": "usuario"
                },
                ...
            }
        }
    """
    creds = {"usernames": {}}
    
    for user in list_users():
        # Obtener datos completos (incluyendo hash)
        full_user = get_user_by_email(user["email"])
        
        if full_user:
            # Usar email como username para consistencia
            creds["usernames"][user["email"]] = {
                "email": user["email"],
                "name": user.get("name") or user["email"].split("@")[0].title(),
                "password": full_user["password_hash"],
                "role": user["role"]
            }
    
    return creds


def get_authenticator(
    cookie_name: str = "lankamar_auth",
    cookie_key: str = "lankamar_secret_key_2024_prod",
    cookie_expiry_days: int = 30
) -> Tuple[stauth.Authenticate, Dict]:
    """
    Crea y retorna el objeto Authenticate de streamlit-authenticator
    configurado para usar datos de SQLite
    
    Args:
        cookie_name: Nombre de la cookie de sesión
        cookie_key: Clave secreta para la cookie
        cookie_expiry_days: Días de validez de la cookie
    
    Returns:
        Tuple de (Authenticate, credentials_dict)
    """
    credentials = build_credentials_dict()
    
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_name,
        cookie_key=cookie_key,
        cookie_expiry_days=cookie_expiry_days
    )
    
    return authenticator, credentials


def get_user_role(username: str, credentials: Dict) -> str:
    """
    Obtiene el rol de un usuario desde el dict de credenciales
    
    Args:
        username: Email/username del usuario
        credentials: Dict de credenciales construido por build_credentials_dict
    
    Returns:
        Rol del usuario (default: "usuario")
    """
    user_data = credentials.get("usernames", {}).get(username, {})
    return user_data.get("role", "usuario")


def get_user_display_name(username: str, credentials: Dict) -> str:
    """Obtiene el nombre para mostrar del usuario"""
    user_data = credentials.get("usernames", {}).get(username, {})
    return user_data.get("name", username)


# Mapeo de roles a opciones de menú
ROLE_MENU_OPTIONS = {
    "ceo": [
        "🔍 Buscar Errores",
        "📹 Videos",
        "📊 Estadísticas",
        "🔧 Validación",
        "📥 Exportar",
        "👥 Usuarios",
        "🎫 Invitaciones"
    ],
    "director": [
        "🔍 Buscar Errores",
        "📹 Videos",
        "📊 Estadísticas",
        "🔧 Validación",
        "📥 Exportar"
    ],
    "jefe_servicio": [
        "🔍 Buscar Errores",
        "📊 Estadísticas",
        "🔧 Validación"
    ],
    "usuario": [
        "🔍 Buscar Errores"
    ]
}


def get_menu_options(role: str) -> list:
    """Retorna las opciones de menú disponibles para un rol"""
    return ROLE_MENU_OPTIONS.get(role, ROLE_MENU_OPTIONS["usuario"])


if __name__ == "__main__":
    print("🔌 Test del adaptador de autenticación")
    
    creds = build_credentials_dict()
    print(f"\n👥 Usuarios encontrados: {len(creds['usernames'])}")
    
    for email, data in creds["usernames"].items():
        print(f"   - {email}: {data['name']} ({data['role']})")
