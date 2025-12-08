# 🔗 INSTRUCCIONES DE CONEXIÓN - GitHub Copilot

## Tu Repositorio
**URL:** https://github.com/lankamar/simulador-bic-lankamar

---

## 📋 PASO 1: Abrir en GitHub Copilot

### Opción A: Desde VS Code con Copilot Chat
1. Abre VS Code
2. Clona el repo: `git clone https://github.com/lankamar/simulador-bic-lankamar.git`
3. Abre la carpeta del proyecto
4. Presiona `Ctrl+Shift+I` para abrir Copilot Chat
5. Escribe: `@workspace Lee el archivo docs/COPILOT_HANDOFF.md e implementa todo el sistema de autenticación con SQLite`

### Opción B: Desde GitHub.dev (navegador)
1. Ve a https://github.com/lankamar/simulador-bic-lankamar
2. Presiona `.` (punto) para abrir VS Code en el navegador
3. Usa Copilot Chat igual que arriba

### Opción C: Desde GitHub Codespaces (recomendado para Pro)
1. Ve a tu repo en GitHub
2. Click en **Code** → **Codespaces** → **Create codespace on main**
3. Espera que se configure el entorno
4. Copilot ya estará habilitado

---

## 📋 PASO 2: Prompt para Copilot

Copia y pega esto en Copilot Chat:

```
@workspace Necesito que implementes el sistema de autenticación con SQLite según el documento docs/COPILOT_HANDOFF.md

Tareas específicas:
1. Crear backend/schema.sql con las tablas users e invites
2. Crear backend/db.py para conexión SQLite
3. Crear backend/auth_service.py con funciones de hash, login, etc
4. Crear backend/invites_service.py para tokens de invitación
5. Crear backend/auth_adapter.py para integrar con streamlit-authenticator
6. Crear backend/migrate_from_yaml.py para migrar usuarios existentes
7. Modificar backend/admin_dashboard.py para usar SQLite en vez de YAML

Lee el documento completo para ver el código exacto a implementar.
```

---

## 📋 PASO 3: Verificar implementación

Después de que Copilot genere los archivos:

```bash
cd backend
pip install -r requirements.txt
python db.py                    # Inicializar DB
python migrate_from_yaml.py     # Migrar usuarios
streamlit run admin_dashboard.py
```

---

## 📋 PASO 4: Commit y Push

```bash
git add .
git commit -m "feat: Sistema de auth con SQLite + invitaciones"
git push origin main
```

---

## 🔐 Credenciales de prueba

- **Email:** lankamar@gmail.com
- **Password:** password123
- **Rol:** CEO (acceso total)

---

## 📁 Archivos a crear

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `backend/schema.sql` | ❌ Pendiente | Esquema SQLite |
| `backend/db.py` | ❌ Pendiente | Conexión DB |
| `backend/auth_service.py` | ❌ Pendiente | Lógica de auth |
| `backend/invites_service.py` | ❌ Pendiente | Sistema invitaciones |
| `backend/auth_adapter.py` | ❌ Pendiente | Adaptador Streamlit |
| `backend/migrate_from_yaml.py` | ❌ Pendiente | Script migración |
| `backend/admin_dashboard.py` | ⚠️ Modificar | Actualizar imports |

---

## ✅ Checklist de evaluación

Después de la implementación, verificar:

- [ ] `auth.db` se crea correctamente
- [ ] Login funciona con usuarios migrados
- [ ] Roles limitan acceso según permisos
- [ ] Se pueden crear invitaciones
- [ ] Los tokens de invitación funcionan
- [ ] Las invitaciones expiran correctamente

---

*Para cualquier duda, el documento completo está en `docs/COPILOT_HANDOFF.md`*
