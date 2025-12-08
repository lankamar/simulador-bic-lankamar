"""
Script de Migracion: config.yaml -> SQLite
Simulador BIC Lankamar

Este script migra los usuarios existentes de config.yaml a la nueva
base de datos SQLite, preservando los hashes de password existentes.

Ejecutar UNA VEZ:
    python migrate_from_yaml.py
"""

import yaml
from pathlib import Path
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import init_db, get_db_stats, DB_PATH
from auth_service import create_user_with_hash, get_user_by_email


def load_yaml_config(config_path: Path) -> dict:
    """Carga el archivo config.yaml"""
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontro: {config_path}")
    
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def migrate_users(config: dict) -> dict:
    """
    Migra usuarios desde el config YAML a SQLite
    
    Returns:
        Dict con estadisticas de migracion
    """
    users = config.get("credentials", {}).get("usernames", {})
    
    stats = {
        "total": len(users),
        "migrated": 0,
        "skipped": 0,
        "errors": 0,
        "details": []
    }
    
    for username, user_data in users.items():
        email = user_data.get("email", f"{username}@migrated.local")
        password_hash = user_data.get("password")
        role = user_data.get("role", "usuario")
        name = user_data.get("name", username)
        
        # Verificar si ya existe
        if get_user_by_email(email):
            stats["skipped"] += 1
            stats["details"].append(f"[SKIP] {email} ya existe, saltando...")
            continue
        
        try:
            # Migrar con hash existente
            create_user_with_hash(
                email=email,
                password_hash=password_hash,
                role=role,
                name=name
            )
            stats["migrated"] += 1
            stats["details"].append(f"[OK] Migrado: {email} (rol: {role})")
        except Exception as e:
            stats["errors"] += 1
            stats["details"].append(f"[ERROR] Migrando {email}: {e}")
    
    return stats


def main():
    print("=" * 60)
    print("[*] MIGRACION: config.yaml -> SQLite")
    print("=" * 60)
    
    config_path = Path(__file__).resolve().parent / "config.yaml"
    
    # 1. Verificar que existe config.yaml
    print(f"\n[1] Buscando: {config_path}")
    if not config_path.exists():
        print("[ERROR] No se encontro config.yaml")
        print("   Asegurate de que el archivo existe en backend/")
        return
    
    # 2. Cargar config
    print("[2] Cargando configuracion...")
    config = load_yaml_config(config_path)
    users_count = len(config.get("credentials", {}).get("usernames", {}))
    print(f"   Encontrados {users_count} usuarios")
    
    # 3. Inicializar DB si no existe
    print(f"\n[3] Base de datos: {DB_PATH}")
    if not DB_PATH.exists():
        print("   Inicializando base de datos...")
        init_db()
    else:
        print("   Base de datos ya existe")
    
    # 4. Migrar usuarios
    print("\n[4] Migrando usuarios...")
    stats = migrate_users(config)
    
    # 5. Mostrar resultados
    print("\n" + "-" * 40)
    for detail in stats["details"]:
        print(f"   {detail}")
    
    print("\n" + "=" * 60)
    print("[*] RESUMEN DE MIGRACION")
    print("=" * 60)
    print(f"   Total en YAML:  {stats['total']}")
    print(f"   Migrados:       {stats['migrated']}")
    print(f"   Saltados:       {stats['skipped']}")
    print(f"   Errores:        {stats['errors']}")
    
    # 6. Estadisticas finales de la DB
    print("\n[i] Estado final de la base de datos:")
    db_stats = get_db_stats()
    print(f"   Usuarios:           {db_stats['users']}")
    print(f"   Invitaciones:       {db_stats['invites_total']}")
    print(f"   Tamano DB:          {db_stats['db_size_kb']} KB")
    
    print("\n[OK] Migracion completada!")
    print("   Ahora podes usar el dashboard con autenticacion SQLite.")
    print("   El archivo config.yaml se mantiene como backup.")


if __name__ == "__main__":
    main()
