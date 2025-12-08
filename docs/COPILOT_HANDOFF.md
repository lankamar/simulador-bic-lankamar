# 🤖 COPILOT HANDOFF - Sistema de Autenticación con SQLite

**Proyecto:** Simulador BIC Lankamar  
**Fecha:** 2025-12-07  
**Preparado por:** Antigravity (Agente IA)  
**Para:** GitHub Copilot (Agente IA)  

---

## 📋 RESUMEN EJECUTIVO

Este documento contiene todo el contexto necesario para implementar un **sistema de autenticación con roles e invitaciones usando SQLite** en el proyecto Simulador BIC Lankamar.

### Objetivo
Evolucionar el sistema de autenticación actual (YAML + streamlit-authenticator) a una solución basada en SQLite que soporte:
- ✅ Usuarios con roles (CEO, Director, Jefe de Servicio, Usuario)
- ✅ Sistema de invitaciones con tokens que otorgan roles específicos
- ✅ Refresh de sesiones
- ✅ Migración de usuarios existentes desde config.yaml

---

## 📁 ESTRUCTURA DEL PROYECTO

```
simulador-bic-lankamar/
├── backend/                    # ⚡ ÁREA DE TRABAJO PRINCIPAL
│   ├── admin_dashboard.py      # Dashboard Streamlit (503 líneas)
│   ├── config.yaml             # Auth actual - MIGRAR A SQLite
│   └── data_validation/        # Scripts de validación
├── data/
│   ├── pumps_db.json          # DB bombas (49KB, 77+ errores)
│   └── content_manifest.json   # Videos educativos
├── lib/                        # App Flutter (Dart)
│   ├── main.dart
│   ├── app_theme.dart
│   ├── screens/
│   ├── services/
│   └── widgets/
├── assets/
├── docs/
├── pubspec.yaml               # Flutter deps
└── README.md
```

---

## 🔧 STACK TECNOLÓGICO ACTUAL

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Dashboard Web | Python + Streamlit | 3.x |
| Autenticación | streamlit-authenticator | Última |
| App Móvil | Flutter/Dart | SDK >=3.0.0 |
| Base de Datos | JSON files (pumps_db.json) | - |
| Auth Actual | YAML + bcrypt hashes | - |

### Dependencias Python Requeridas
```
streamlit
streamlit-authenticator
pyyaml
bcrypt
```

---

## 👥 USUARIOS ACTUALES (config.yaml)

Los siguientes usuarios existen y deben migrarse a SQLite:

| Username | Email | Role | Password Hash |
|----------|-------|------|---------------|
| marcelo | lankamar@gmail.com | ceo | $2b$12$qayCsOO0RWD74uTUXXLs7u... |
| director1 | director@hospital.com | director | (mismo hash) |
| jefe_enfermeria | jefe@hospital.com | jefe_servicio | (mismo hash) |
| enfermero1 | enfermero@hospital.com | usuario | (mismo hash) |

**NOTA:** Todos usan el mismo hash bcrypt actualmente (password: `password123`).

---

## 🎯 TAREA PARA IMPLEMENTAR

### 1. Crear Esquema SQLite (`backend/schema.sql`)

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  email_verified INTEGER NOT NULL DEFAULT 0,
  last_login_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invites (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT,
  role TEXT NOT NULL,
  token TEXT NOT NULL UNIQUE,
  expires_at TEXT,
  used_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_users_updated_at
AFTER UPDATE ON users
BEGIN
  UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 2. Crear Módulo DB (`backend/db.py`)

```python
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "auth.db"

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.commit()
    conn.close()

def init_db():
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(schema)

if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada en:", DB_PATH)
```

### 3. Crear Servicio de Auth (`backend/auth_service.py`)

```python
import bcrypt
import secrets
from datetime import datetime
from typing import Optional
from db import get_conn

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_user(email: str, password: str, role: str = "user"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email.lower(), hash_password(password), role),
        )

def create_user_with_hash(email: str, password_hash: str, role: str = "user"):
    """Para migración desde YAML - usa hash existente"""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email.lower(), password_hash, role),
        )

def get_user_by_email(email: str):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower(),)
        )
        return cur.fetchone()

def authenticate(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user["id"])
        )
    return dict(user)

def list_users():
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, email, role, email_verified, last_login_at, created_at FROM users ORDER BY created_at DESC"
        )
        return [dict(row) for row in cur.fetchall()]

def update_user_role(user_id: int, new_role: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role, user_id)
        )
```

### 4. Crear Servicio de Invitaciones (`backend/invites_service.py`)

```python
import secrets
from datetime import datetime, timedelta
from typing import Optional
from db import get_conn
from auth_service import create_user, get_user_by_email

VALID_ROLES = ["usuario", "jefe_servicio", "director", "ceo", "helper", "admin"]

def create_invite(role: str, email: Optional[str] = None, hours_valid: int = 72) -> str:
    if role not in VALID_ROLES:
        raise ValueError(f"Rol inválido. Usar: {VALID_ROLES}")
    
    token = secrets.token_urlsafe(24)
    expires_at = (datetime.utcnow() + timedelta(hours=hours_valid)).isoformat()
    
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO invites (email, role, token, expires_at) VALUES (?, ?, ?, ?)",
            (email.lower() if email else None, role, token, expires_at),
        )
    return token

def get_invite_by_token(token: str):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM invites WHERE token = ?", (token,)
        )
        return cur.fetchone()

def redeem_invite(token: str, email: str, password: Optional[str] = None):
    """
    Canjea una invitación:
    - Si el usuario existe, eleva su rol
    - Si no existe, crea usuario nuevo (requiere password)
    """
    now = datetime.utcnow().isoformat()
    
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM invites WHERE token = ? AND used_at IS NULL", (token,)
        )
        invite = cur.fetchone()
        
        if not invite:
            raise ValueError("Token inválido o ya usado")
        
        if invite["expires_at"] and invite["expires_at"] < now:
            raise ValueError("Token expirado")
        
        # Verificar email si la invitación es específica
        if invite["email"] and invite["email"].lower() != email.lower():
            raise ValueError("Este token es para otro email")
        
        user = get_user_by_email(email)
        
        if user:
            # Usuario existe - elevar rol
            conn.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (invite["role"], user["id"])
            )
        else:
            # Usuario nuevo - requiere password
            if not password:
                raise ValueError("Se requiere contraseña para crear usuario nuevo")
            create_user(email=email, password=password, role=invite["role"])
        
        # Marcar invitación como usada
        conn.execute(
            "UPDATE invites SET used_at = ? WHERE id = ?",
            (now, invite["id"])
        )
        
        return {"success": True, "role": invite["role"], "is_new_user": user is None}

def list_invites(include_used: bool = False):
    with get_conn() as conn:
        if include_used:
            cur = conn.execute("SELECT * FROM invites ORDER BY created_at DESC")
        else:
            cur = conn.execute(
                "SELECT * FROM invites WHERE used_at IS NULL ORDER BY created_at DESC"
            )
        return [dict(row) for row in cur.fetchall()]

def revoke_invite(token: str):
    """Revoca una invitación pendiente"""
    with get_conn() as conn:
        conn.execute("DELETE FROM invites WHERE token = ? AND used_at IS NULL", (token,))
```

### 5. Crear Adaptador para Streamlit (`backend/auth_adapter.py`)

```python
import streamlit_authenticator as stauth
from auth_service import list_users, get_user_by_email

def build_credentials_dict():
    """Construye el dict de credenciales desde SQLite para streamlit-authenticator"""
    creds = {"usernames": {}}
    
    for u in list_users():
        user_full = get_user_by_email(u["email"])
        if user_full:
            # Usar email como username para simplicidad
            creds["usernames"][u["email"]] = {
                "email": u["email"],
                "name": u["email"].split("@")[0].title(),
                "password": user_full["password_hash"],
                "role": u["role"]
            }
    
    return creds

def get_authenticator(cookie_name="lankamar_auth", key="lankamar_secret_key_2024"):
    credentials = build_credentials_dict()
    
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        key,
        cookie_expiry_days=30,
    )
    return authenticator, credentials
```

### 6. Crear Script de Migración (`backend/migrate_from_yaml.py`)

```python
"""
Script de migración de config.yaml a SQLite
Ejecutar UNA VEZ: python migrate_from_yaml.py
"""
import yaml
from pathlib import Path
from db import init_db, get_conn
from auth_service import create_user_with_hash, get_user_by_email

def migrate_config_yaml():
    config_path = Path(__file__).resolve().parent / "config.yaml"
    
    if not config_path.exists():
        print("❌ No se encontró config.yaml")
        return
    
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    users = data.get("credentials", {}).get("usernames", {})
    
    print(f"📦 Encontrados {len(users)} usuarios para migrar...")
    
    migrated = 0
    skipped = 0
    
    for username, user_data in users.items():
        email = user_data.get("email", f"{username}@migrated.local")
        password_hash = user_data.get("password")
        role = user_data.get("role", "usuario")
        
        # Verificar si ya existe
        if get_user_by_email(email):
            print(f"  ⏭️  {email} ya existe, saltando...")
            skipped += 1
            continue
        
        # Migrar con hash existente
        create_user_with_hash(email=email, password_hash=password_hash, role=role)
        print(f"  ✅ Migrado: {email} (rol: {role})")
        migrated += 1
    
    print(f"\n🎉 Migración completada: {migrated} usuarios migrados, {skipped} saltados")

if __name__ == "__main__":
    print("🚀 Inicializando base de datos SQLite...")
    init_db()
    print("📂 Migrando usuarios desde config.yaml...")
    migrate_from_yaml()
    print("\n✅ ¡Listo! La base de datos auth.db está lista para usar.")
```

### 7. Modificar admin_dashboard.py

**Cambios requeridos en `backend/admin_dashboard.py`:**

```python
# REEMPLAZAR las líneas 8-11 con:
import streamlit as st
from pathlib import Path
import json
from datetime import datetime

# Nuevos imports para auth SQLite
from auth_adapter import get_authenticator
from auth_service import list_users, update_user_role
from invites_service import create_invite, list_invites, revoke_invite

# REEMPLAZAR la función main() (líneas 75-138) con:
def main():
    # Obtener autenticador desde SQLite
    authenticator, credentials = get_authenticator()
    
    # Login
    authenticator.login()
    
    if st.session_state.get("authentication_status"):
        # Usuario logueado
        username = st.session_state["username"]  # Ahora es el email
        user_creds = credentials['usernames'].get(username, {})
        role = user_creds.get('role', 'usuario')
        
        # [resto del código igual pero usar 'role' obtenido de credentials]
        # ...
```

**Agregar nueva sección de gestión de usuarios (solo para rol CEO):**

```python
def render_users_section():
    """Sección de gestión de usuarios - Solo CEO"""
    st.header("👥 Gestión de Usuarios")
    
    tab1, tab2, tab3 = st.tabs(["Usuarios", "Crear Invitación", "Invitaciones Pendientes"])
    
    with tab1:
        st.subheader("Usuarios Registrados")
        users = list_users()
        
        for user in users:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{user['email']}**")
                st.caption(f"Último login: {user.get('last_login_at', 'Nunca')}")
            with col2:
                st.badge(user['role'])
            with col3:
                if user['role'] != 'ceo':  # No permitir cambiar al CEO
                    new_role = st.selectbox(
                        "Rol",
                        ["usuario", "jefe_servicio", "director"],
                        key=f"role_{user['id']}"
                    )
                    if st.button("Cambiar", key=f"btn_{user['id']}"):
                        update_user_role(user['id'], new_role)
                        st.rerun()
    
    with tab2:
        st.subheader("Crear Invitación")
        
        with st.form("invite_form"):
            inv_role = st.selectbox("Rol a otorgar", ["usuario", "jefe_servicio", "director", "ceo"])
            inv_email = st.text_input("Email específico (opcional)")
            inv_hours = st.number_input("Válido por (horas)", value=72, min_value=1, max_value=720)
            
            if st.form_submit_button("🎫 Generar Token"):
                token = create_invite(inv_role, email=inv_email or None, hours_valid=inv_hours)
                st.success("¡Invitación creada!")
                st.code(token, language=None)
                st.info("Comparte este token con el invitado. Podrá usarlo para registrarse o elevar su rol.")
    
    with tab3:
        st.subheader("Invitaciones Pendientes")
        invites = list_invites(include_used=False)
        
        if not invites:
            st.info("No hay invitaciones pendientes")
        else:
            for inv in invites:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**Rol:** {inv['role']} | **Expira:** {inv['expires_at'][:10]}")
                    st.code(inv['token'][:20] + "...", language=None)
                with col2:
                    if st.button("❌ Revocar", key=f"rev_{inv['id']}"):
                        revoke_invite(inv['token'])
                        st.rerun()
```

---

## 📝 INSTRUCCIONES DE IMPLEMENTACIÓN

### Paso 1: Crear los archivos
```bash
cd backend/
# Crear los 5 archivos nuevos:
# - schema.sql
# - db.py
# - auth_service.py
# - invites_service.py
# - auth_adapter.py
# - migrate_from_yaml.py
```

### Paso 2: Inicializar y migrar
```bash
cd backend/
python db.py              # Crea auth.db
python migrate_from_yaml.py  # Migra usuarios desde config.yaml
```

### Paso 3: Actualizar admin_dashboard.py
- Cambiar imports
- Usar `get_authenticator()` en vez de cargar YAML
- Agregar sección de usuarios (render_users_section)
- Agregar al menú del CEO la opción "👥 Usuarios"

### Paso 4: Probar
```bash
streamlit run admin_dashboard.py
# Iniciar sesión con: lankamar@gmail.com / password123
```

---

## 🔐 ROLES Y PERMISOS

| Rol | Permisos |
|-----|----------|
| `ceo` | TODO: Buscar, Videos, Stats, Validación, Exportar, Usuarios |
| `director` | Buscar, Videos, Stats, Validación, Exportar |
| `jefe_servicio` | Buscar, Stats, Validación |
| `usuario` | Solo Buscar Errores |

---

## ⚠️ NOTAS IMPORTANTES

1. **Mantener config.yaml** como backup hasta verificar que SQLite funciona
2. **auth.db** se crea en `/backend/auth.db`
3. Los passwords actuales son hashes bcrypt válidos (password: `password123`)
4. El sistema de invitaciones genera tokens de 24 bytes (base64url)
5. Las invitaciones expiran por defecto en 72 horas

---

## 🔗 REPOSITORIO

**GitHub:** [pendiente de confirmar URL del repo]

Para clonar:
```bash
git clone https://github.com/[usuario]/simulador-bic-lankamar.git
cd simulador-bic-lankamar
pip install -r requirements.txt  # si existe
cd backend
streamlit run admin_dashboard.py
```

---

## 📞 CONTACTO

**Propietario:** Marcelo Lancry (Lankamar)  
**Email:** lankamar@gmail.com  

---

*Documento generado automáticamente por Antigravity el 2025-12-07*
