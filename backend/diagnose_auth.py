"""
Script de diagnóstico para el problema de login
"""
import sqlite3
from pathlib import Path

# Conectar directamente a la DB
db_path = Path(__file__).parent / "auth.db"

print("🔍 Diagnóstico de autenticación")
print("=" * 50)

# Ver usuarios en la DB
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.execute("SELECT email, password_hash, role FROM users")
users = cursor.fetchall()

print(f"\n📋 Usuarios en la DB ({len(users)}):")
for u in users:
    hash_preview = u['password_hash'][:30] if u['password_hash'] else 'NULL'
    print(f"  - {u['email']} | rol: {u['role']} | hash: {hash_preview}...")

# Test bcrypt simple
print("\n🔐 Test bcrypt:")
import bcrypt
plain = "admin123"
hashed = bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(rounds=4))  # 4 rounds = rapido
print(f"  Password: {plain}")
print(f"  Hash nuevo (4 rounds): {hashed.decode()}")

# Verificar
check = bcrypt.checkpw(plain.encode(), hashed)
print(f"  Verificacion: {check}")

conn.close()

# Ahora probar la build de credenciales
print("\n🔌 Build credentials dict:")
from auth_adapter import build_credentials_dict
creds = build_credentials_dict()
print(f"  Usuarios cargados: {len(creds['usernames'])}")

for email, data in creds['usernames'].items():
    print(f"    - {email}: {data.get('name', 'N/A')} | hash: {data.get('password', 'N/A')[:30]}...")



print("\n✅ Diagnóstico completado")
