"""
Script para resetear contraseñas de usuarios
Simulador BIC Lankamar
"""

from auth_service import get_user_by_email, hash_password
from db import get_conn

def reset_password(email: str, new_password: str):
    """Resetea la contraseña de un usuario"""
    user = get_user_by_email(email)
    
    if not user:
        print(f"❌ Usuario no encontrado: {email}")
        return False
    
    new_hash = hash_password(new_password)
    
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (new_hash, email.lower().strip())
        )
    
    print(f"✅ Contraseña reseteada para: {email}")
    print(f"   Nueva contraseña: {new_password}")
    return True


if __name__ == "__main__":
    # Resetear contraseña del CEO
    print("🔐 Reset de contraseñas - Simulador BIC Lankamar")
    print("=" * 50)
    
    # Resetear a contraseñas simples para testing
    users_to_reset = [
        ("lankamar@gmail.com", "admin123"),
        ("director@hospital.com", "director123"),
        ("jefe@hospital.com", "jefe123"),
        ("enfermero@hospital.com", "user123"),
    ]
    
    for email, password in users_to_reset:
        reset_password(email, password)
    
    print("\n" + "=" * 50)
    print("✅ Todas las contraseñas han sido reseteadas")
    print("\n📋 Credenciales de acceso:")
    print("   CEO:      lankamar@gmail.com / admin123")
    print("   Director: director@hospital.com / director123")
    print("   Jefe:     jefe@hospital.com / jefe123")
    print("   Usuario:  enfermero@hospital.com / user123")
