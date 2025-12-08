"""
Script para agregar usuarios familiares
Simulador BIC Lankamar

Este script agrega usuarios familiares al sistema de autenticación SQLite
para poder practicar con el sistema de tokens de invitación.

Ejecutar:
    python seed_family_users.py
"""

from pathlib import Path
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import get_db_stats, DB_PATH, init_db
from auth_service import create_user, get_user_by_email


# Lista de usuarios familiares a agregar
FAMILY_USERS = [
    {"name": "Isaac Benjamín Lancry Domínguez", "email": "chakito.lancry@gmail.com"},
    {"name": "Matias Lancry", "email": "lancrymatias@live.com"},
    {"name": "Martin Lancry", "email": "titilancry70@gmail.com"},
    {"name": "Mariano Lancry", "email": "mdlancry@gmail.com"},
    {"name": "Guillermo Lancry", "email": "gglk23@gmail.com"},
    {"name": "Carina Lancry", "email": "cveronicalancry@gmail.com"},
    {"name": "Mónica Patricia Lancry", "email": "kamycki2005@gmail.com"},
]

DEFAULT_PASSWORD = "familia123"
DEFAULT_ROLE = "usuario"


def seed_family_users() -> dict:
    """
    Crea los usuarios familiares en la base de datos SQLite
    
    Returns:
        Dict con estadisticas de creación
    """
    stats = {
        "total": len(FAMILY_USERS),
        "created": 0,
        "skipped": 0,
        "errors": 0,
        "details": []
    }
    
    for user_data in FAMILY_USERS:
        email = user_data["email"]
        name = user_data["name"]
        
        # Verificar si ya existe
        if get_user_by_email(email):
            stats["skipped"] += 1
            stats["details"].append(f"[SKIP] {email} ya existe, saltando...")
            continue
        
        try:
            # Crear usuario con contraseña por defecto
            user_id = create_user(
                email=email,
                password=DEFAULT_PASSWORD,
                role=DEFAULT_ROLE,
                name=name
            )
            stats["created"] += 1
            stats["details"].append(f"[OK] Creado: {email} (ID: {user_id}, rol: {DEFAULT_ROLE})")
        except Exception as e:
            stats["errors"] += 1
            stats["details"].append(f"[ERROR] Creando {email}: {e}")
    
    return stats


def main():
    print("=" * 60)
    print("[*] SEED: Usuarios Familiares")
    print("=" * 60)
    
    # 1. Verificar que existe la base de datos
    print(f"\n[1] Base de datos: {DB_PATH}")
    if not DB_PATH.exists():
        print("   Inicializando base de datos...")
        init_db()
    else:
        print("   Base de datos encontrada")
    
    # 2. Mostrar estadísticas iniciales
    print("\n[2] Estado inicial de la base de datos:")
    db_stats = get_db_stats()
    print(f"   Usuarios actuales:  {db_stats['users']}")
    print(f"   Tamaño DB:          {db_stats['db_size_kb']} KB")
    
    # 3. Crear usuarios familiares
    print(f"\n[3] Agregando {len(FAMILY_USERS)} usuarios familiares...")
    print(f"   Contraseña por defecto: {DEFAULT_PASSWORD}")
    print(f"   Rol por defecto:        {DEFAULT_ROLE}")
    
    stats = seed_family_users()
    
    # 4. Mostrar resultados
    print("\n" + "-" * 40)
    for detail in stats["details"]:
        print(f"   {detail}")
    
    print("\n" + "=" * 60)
    print("[*] RESUMEN")
    print("=" * 60)
    print(f"   Total a agregar:    {stats['total']}")
    print(f"   Creados:            {stats['created']}")
    print(f"   Saltados:           {stats['skipped']}")
    print(f"   Errores:            {stats['errors']}")
    
    # 5. Estadísticas finales de la DB
    print("\n[i] Estado final de la base de datos:")
    db_stats = get_db_stats()
    print(f"   Usuarios:           {db_stats['users']}")
    print(f"   Invitaciones:       {db_stats['invites_total']}")
    print(f"   Tamaño DB:          {db_stats['db_size_kb']} KB")
    
    print("\n[OK] Proceso completado!")
    print(f"   Los usuarios pueden iniciar sesión con la contraseña: {DEFAULT_PASSWORD}")
    print("   El CEO puede cambiar roles desde el dashboard si es necesario.")


if __name__ == "__main__":
    main()
