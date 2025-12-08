"""
Script para resetear el sistema de autenticación
Simulador BIC Lankamar

Uso:
    python reset_auth.py

Acciones:
1. Elimina auth.db si existe
2. Reinicializa la base de datos
3. Crea el usuario CEO con credenciales conocidas

Credenciales del CEO:
- Email: lankamar@gmail.com
- Password: password123
- Role: ceo
- Name: Marcelo (CEO)
"""

from pathlib import Path
from db import init_db, DB_PATH, get_db_stats
from auth_service import create_user, get_user_by_email


def reset_auth():
    """Resetea completamente el sistema de autenticación"""
    
    print("🔄 Reseteando sistema de autenticación...\n")
    
    # 1. Eliminar auth.db si existe
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[✓] Base de datos eliminada: {DB_PATH}")
    else:
        print(f"[i] No existe base de datos previa en: {DB_PATH}")
    
    # 2. Reinicializar base de datos
    print("\n[*] Inicializando base de datos...")
    init_db()
    
    # 3. Crear usuario CEO
    print("\n[*] Creando usuario CEO...")
    
    ceo_email = "lankamar@gmail.com"
    ceo_password = "password123"
    ceo_role = "ceo"
    ceo_name = "Marcelo (CEO)"
    
    try:
        # Crear usuario CEO (no debería existir después del reset)
        user_id = create_user(
            email=ceo_email,
            password=ceo_password,
            role=ceo_role,
            name=ceo_name
        )
        print(f"[✓] Usuario CEO creado exitosamente (ID: {user_id})")
    except Exception as e:
        print(f"[✗] Error al crear usuario: {e}")
        return False
    
    # 4. Mostrar estadísticas
    print("\n" + "="*60)
    print("✅ SISTEMA RESETEADO EXITOSAMENTE")
    print("="*60)
    
    stats = get_db_stats()
    print(f"\n📊 Estadísticas:")
    print(f"   - Usuarios: {stats['users']}")
    print(f"   - Base de datos: {stats['db_path']}")
    print(f"   - Tamaño: {stats['db_size_kb']} KB")
    
    print(f"\n🔑 Credenciales de acceso:")
    print(f"   - Email: {ceo_email}")
    print(f"   - Password: {ceo_password}")
    print(f"   - Role: {ceo_role}")
    print(f"   - Name: {ceo_name}")
    
    print(f"\n💡 Para acceder al dashboard:")
    print(f"   cd backend")
    print(f"   streamlit run admin_dashboard.py")
    
    return True


if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("🔐 RESET DE SISTEMA DE AUTENTICACIÓN")
    print("    Simulador BIC Lankamar")
    print("="*60)
    print()
    
    confirm = input("⚠️  Esta acción eliminará todos los usuarios existentes.\n¿Continuar? (s/N): ")
    
    if confirm.lower() in ['s', 'si', 'yes', 'y']:
        success = reset_auth()
        sys.exit(0 if success else 1)
    else:
        print("\n[i] Operación cancelada")
        sys.exit(0)
