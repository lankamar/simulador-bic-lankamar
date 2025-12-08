"""
Servicio de Invitaciones con Token
Simulador BIC Lankamar

Sistema para:
- Crear invitaciones con roles específicos
- Tokens seguros con expiración
- Canjear invitaciones (usuarios nuevos o existentes)
- Revocar invitaciones pendientes
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from db import get_conn
from auth_service import create_user, get_user_by_email, ROLES


# ============================================================
# FUNCIONES DE INVITACIONES
# ============================================================

def create_invite(
    role: str,
    email: Optional[str] = None,
    hours_valid: int = 72,
    created_by: Optional[int] = None
) -> str:
    """
    Crea una nueva invitación con token
    
    Args:
        role: Rol a otorgar al usar la invitación
        email: Email específico (opcional, None = invitación abierta)
        hours_valid: Horas de validez (default: 72 = 3 días)
        created_by: ID del usuario que crea la invitación
    
    Returns:
        Token de invitación (string de 32 caracteres base64url)
    
    Raises:
        ValueError si el rol no es válido
    """
    if role not in ROLES:
        raise ValueError(f"Rol inválido. Opciones válidas: {list(ROLES.keys())}")
    
    # Generar token seguro
    token = secrets.token_urlsafe(24)  # 32 caracteres
    
    # Calcular expiración
    expires_at = (datetime.utcnow() + timedelta(hours=hours_valid)).isoformat()
    
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO invites (email, role, token, expires_at, created_by) 
               VALUES (?, ?, ?, ?, ?)""",
            (
                email.lower().strip() if email else None,
                role,
                token,
                expires_at,
                created_by
            )
        )
    
    return token


def get_invite_by_token(token: str) -> Optional[Dict]:
    """Busca una invitación por su token"""
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM invites WHERE token = ?",
            (token,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def validate_invite(token: str) -> Dict:
    """
    Valida si un token de invitación es válido
    
    Args:
        token: Token a validar
    
    Returns:
        Dict con info de la invitación si es válida
    
    Raises:
        ValueError si el token es inválido, usado o expirado
    """
    invite = get_invite_by_token(token)
    
    if not invite:
        raise ValueError("Token inválido o no existe")
    
    if invite["used_at"]:
        raise ValueError("Este token ya fue utilizado")
    
    now = datetime.utcnow().isoformat()
    if invite["expires_at"] and invite["expires_at"] < now:
        raise ValueError("Este token ha expirado")
    
    return invite


def redeem_invite(token: str, email: str, password: Optional[str] = None) -> Dict:
    """
    Canjea una invitación
    
    - Si el usuario ya existe: eleva su rol
    - Si no existe: crea usuario nuevo (requiere password)
    
    Args:
        token: Token de invitación
        email: Email del usuario
        password: Contraseña (requerida solo si es usuario nuevo)
    
    Returns:
        Dict con resultado: {success, role, is_new_user, message}
    
    Raises:
        ValueError si hay algún problema con el token o datos
    """
    # Validar el token
    invite = validate_invite(token)
    
    # Verificar que el email coincida si la invitación es específica
    if invite["email"] and invite["email"].lower() != email.lower().strip():
        raise ValueError("Este token está destinado a otro email")
    
    now = datetime.utcnow().isoformat()
    email = email.lower().strip()
    
    # Verificar si el usuario existe
    existing_user = get_user_by_email(email)
    
    with get_conn() as conn:
        if existing_user:
            # Usuario existe → actualizar rol
            conn.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (invite["role"], existing_user["id"])
            )
            is_new = False
            message = f"Rol actualizado a: {invite['role']}"
        else:
            # Usuario nuevo → crear
            if not password:
                raise ValueError("Se requiere contraseña para usuarios nuevos")
            
            create_user(email=email, password=password, role=invite["role"])
            is_new = True
            message = f"Usuario creado con rol: {invite['role']}"
        
        # Marcar invitación como usada
        conn.execute(
            "UPDATE invites SET used_at = ? WHERE id = ?",
            (now, invite["id"])
        )
    
    return {
        "success": True,
        "role": invite["role"],
        "is_new_user": is_new,
        "message": message
    }


def list_invites(include_used: bool = False, include_expired: bool = False) -> List[Dict]:
    """
    Lista las invitaciones
    
    Args:
        include_used: Si True, incluye invitaciones ya usadas
        include_expired: Si True, incluye invitaciones expiradas
    
    Returns:
        Lista de dicts con datos de invitaciones
    """
    now = datetime.utcnow().isoformat()
    
    with get_conn() as conn:
        query = "SELECT * FROM invites WHERE 1=1"
        params = []
        
        if not include_used:
            query += " AND used_at IS NULL"
        
        if not include_expired:
            query += " AND (expires_at IS NULL OR expires_at > ?)"
            params.append(now)
        
        query += " ORDER BY created_at DESC"
        
        cursor = conn.execute(query, params)
        invites = [dict(row) for row in cursor.fetchall()]
        
        # Agregar estado calculado
        for inv in invites:
            if inv["used_at"]:
                inv["status"] = "usado"
            elif inv["expires_at"] and inv["expires_at"] < now:
                inv["status"] = "expirado"
            else:
                inv["status"] = "pendiente"
        
        return invites


def revoke_invite(token: str) -> bool:
    """
    Revoca (elimina) una invitación pendiente
    
    Args:
        token: Token a revocar
    
    Returns:
        True si se revocó, False si no existía o ya estaba usada
    """
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM invites WHERE token = ? AND used_at IS NULL",
            (token,)
        )
        return cursor.rowcount > 0


def cleanup_expired_invites() -> int:
    """
    Elimina invitaciones expiradas y no usadas
    
    Returns:
        Número de invitaciones eliminadas
    """
    now = datetime.utcnow().isoformat()
    
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM invites WHERE expires_at < ? AND used_at IS NULL",
            (now,)
        )
        return cursor.rowcount


def get_invite_stats() -> Dict:
    """Estadísticas de invitaciones"""
    now = datetime.utcnow().isoformat()
    
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM invites").fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM invites WHERE used_at IS NULL AND (expires_at IS NULL OR expires_at > ?)",
            (now,)
        ).fetchone()[0]
        used = conn.execute(
            "SELECT COUNT(*) FROM invites WHERE used_at IS NOT NULL"
        ).fetchone()[0]
        expired = conn.execute(
            "SELECT COUNT(*) FROM invites WHERE used_at IS NULL AND expires_at < ?",
            (now,)
        ).fetchone()[0]
    
    return {
        "total": total,
        "pendientes": pending,
        "usadas": used,
        "expiradas": expired
    }


if __name__ == "__main__":
    print("🎫 Test del servicio de invitaciones")
    
    # Crear una invitación de prueba
    token = create_invite(role="usuario", hours_valid=1)
    print(f"Token creado: {token}")
    
    # Validar
    try:
        invite = validate_invite(token)
        print(f"Invitación válida: rol={invite['role']}, expira={invite['expires_at']}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Stats
    print("\n📊 Estadísticas:")
    stats = get_invite_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
