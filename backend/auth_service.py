"""
Servicio de Autenticación
Simulador BIC Lankamar

Funciones para:
- Hash/verificación de contraseñas (bcrypt)
- Creación y gestión de usuarios
- Autenticación (login)
- Gestión de roles
"""

import bcrypt
from datetime import datetime
from typing import Optional, Dict, List
from db import get_conn


# ============================================================
# FUNCIONES DE CONTRASEÑAS
# ============================================================

def hash_password(plain: str) -> str:
    """
    Hashea una contraseña con bcrypt (12 rounds)
    
    Args:
        plain: Contraseña en texto plano
    
    Returns:
        Hash bcrypt como string
    """
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        plain: Contraseña en texto plano
        hashed: Hash bcrypt almacenado
    
    Returns:
        True si coinciden, False si no
    """
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


# ============================================================
# FUNCIONES DE USUARIOS
# ============================================================

def create_user(email: str, password: str, role: str = "usuario", name: str = None) -> int:
    """
    Crea un nuevo usuario con contraseña hasheada
    
    Args:
        email: Email único del usuario
        password: Contraseña en texto plano (se hashea automáticamente)
        role: Rol del usuario (default: "usuario")
        name: Nombre para mostrar (opcional)
    
    Returns:
        ID del usuario creado
    
    Raises:
        sqlite3.IntegrityError si el email ya existe
    """
    password_hash = hash_password(password)
    
    with get_conn() as conn:
        cursor = conn.execute(
            """INSERT INTO users (email, password_hash, name, role) 
               VALUES (?, ?, ?, ?)""",
            (email.lower().strip(), password_hash, name or email.split('@')[0], role)
        )
        return cursor.lastrowid


def create_user_with_hash(email: str, password_hash: str, role: str = "usuario", name: str = None) -> int:
    """
    Crea un usuario usando un hash existente (para migración)
    
    Args:
        email: Email único
        password_hash: Hash bcrypt ya existente
        role: Rol del usuario
        name: Nombre para mostrar
    
    Returns:
        ID del usuario creado
    """
    with get_conn() as conn:
        cursor = conn.execute(
            """INSERT INTO users (email, password_hash, name, role) 
               VALUES (?, ?, ?, ?)""",
            (email.lower().strip(), password_hash, name or email.split('@')[0], role)
        )
        return cursor.lastrowid


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Busca un usuario por email
    
    Returns:
        Dict con datos del usuario o None si no existe
    """
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Busca un usuario por ID"""
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def list_users() -> List[Dict]:
    """
    Lista todos los usuarios (sin el hash de contraseña)
    
    Returns:
        Lista de dicts con datos de usuarios
    """
    with get_conn() as conn:
        cursor = conn.execute(
            """SELECT id, email, name, role, email_verified, last_login_at, created_at, updated_at 
               FROM users 
               ORDER BY created_at DESC"""
        )
        return [dict(row) for row in cursor.fetchall()]


def update_user_role(user_id: int, new_role: str) -> bool:
    """
    Actualiza el rol de un usuario
    
    Args:
        user_id: ID del usuario
        new_role: Nuevo rol a asignar
    
    Returns:
        True si se actualizó, False si el usuario no existe
    """
    with get_conn() as conn:
        cursor = conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role, user_id)
        )
        return cursor.rowcount > 0


def update_last_login(user_id: int):
    """Actualiza la fecha de último login"""
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user_id)
        )


def delete_user(user_id: int) -> bool:
    """Elimina un usuario por ID"""
    with get_conn() as conn:
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0


# ============================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================

def authenticate(email: str, password: str) -> Optional[Dict]:
    """
    Autentica un usuario con email y contraseña
    
    Args:
        email: Email del usuario
        password: Contraseña en texto plano
    
    Returns:
        Dict con datos del usuario si las credenciales son válidas,
        None si son inválidas
    """
    if not email or not password:
        return None
        
    user = get_user_by_email(email)
    
    if not user:
        print("[AUTH] Usuario no encontrado")
        return None
    
    try:
        if not verify_password(password, user["password_hash"]):
            print("[AUTH] Contraseña incorrecta")
            return None
    except Exception as e:
        print(f"[AUTH] Error verificando password: {e}")
        return None
    
    # Actualizar último login
    update_last_login(user["id"])
    
    # Retornar sin el hash
    user_copy = dict(user)
    del user_copy["password_hash"]
    return user_copy


def change_password(user_id: int, new_password: str) -> bool:
    """
    Cambia la contraseña de un usuario
    
    Args:
        user_id: ID del usuario
        new_password: Nueva contraseña en texto plano
    
    Returns:
        True si se cambió, False si el usuario no existe
    """
    new_hash = hash_password(new_password)
    
    with get_conn() as conn:
        cursor = conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_hash, user_id)
        )
        return cursor.rowcount > 0


# ============================================================
# CONSTANTES DE ROLES
# ============================================================

ROLES = {
    "ceo": {
        "nivel": 100,
        "nombre": "CEO",
        "permisos": ["buscar", "videos", "estadisticas", "validacion", "exportar", "usuarios", "invitaciones"]
    },
    "director": {
        "nivel": 80,
        "nombre": "Director",
        "permisos": ["buscar", "videos", "estadisticas", "validacion", "exportar"]
    },
    "jefe_servicio": {
        "nivel": 60,
        "nombre": "Jefe de Servicio",
        "permisos": ["buscar", "estadisticas", "validacion"]
    },
    "usuario": {
        "nivel": 20,
        "nombre": "Usuario",
        "permisos": ["buscar"]
    }
}


def get_role_permissions(role: str) -> List[str]:
    """Obtiene los permisos de un rol"""
    return ROLES.get(role, ROLES["usuario"])["permisos"]


def user_has_permission(user_role: str, permission: str) -> bool:
    """Verifica si un rol tiene un permiso específico"""
    permisos = get_role_permissions(user_role)
    return permission in permisos


if __name__ == "__main__":
    # Test rápido
    print("🔐 Test del servicio de autenticación")
    
    test_password = "test123"
    hashed = hash_password(test_password)
    print(f"Password: {test_password}")
    print(f"Hash: {hashed[:50]}...")
    print(f"Verificación: {verify_password(test_password, hashed)}")
    print(f"Verificación incorrecta: {verify_password('wrong', hashed)}")
