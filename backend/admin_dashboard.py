"""
Dashboard Admin - Simulador BIC Lankamar
Panel web para gestión de Video-Bicicleta (contenido educativo)

Ejecutar con: streamlit run admin_dashboard.py

v2.0 - Autenticación con SQLite
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# Imports del sistema de autenticación SQLite
from auth_adapter import get_authenticator, get_user_role, get_menu_options, get_user_display_name
from auth_service import list_users, update_user_role, get_role_permissions, ROLES
from invites_service import (
    create_invite, list_invites, revoke_invite, 
    get_invite_stats, redeem_invite, cleanup_expired_invites
)
from db import get_db_stats, DB_PATH, init_db, get_conn
from auth_service import create_user, get_user_by_email
import sqlite3

# Configuración de página
st.set_page_config(
    page_title="Lankamar Admin",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Credenciales por defecto del CEO (para auto-inicialización)
DEFAULT_CEO_EMAIL = "lankamar@gmail.com"
DEFAULT_CEO_PASSWORD = "password123"
DEFAULT_CEO_ROLE = "ceo"
DEFAULT_CEO_NAME = "Marcelo (CEO)"

# Rutas de archivos (usando ruta absoluta para evitar problemas de directorio de trabajo)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PUMPS_DB_PATH = DATA_DIR / "pumps_db.json"
CONTENT_MANIFEST_PATH = DATA_DIR / "content_manifest.json"


def load_pumps():
    """Carga la base de datos de bombas"""
    try:
        with open(PUMPS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"No se encontró {PUMPS_DB_PATH}")
        return []


def load_content_manifest():
    """Carga el manifest de contenido (videos)"""
    try:
        with open(CONTENT_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"videos": [], "last_updated": None}


def save_content_manifest(manifest):
    """Guarda el manifest de contenido"""
    manifest["last_updated"] = datetime.now().isoformat()
    with open(CONTENT_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def get_all_errors(pumps):
    """Extrae todos los errores de todas las bombas"""
    errors = []
    for pump in pumps:
        for error in pump.get("errores_y_alarmas", []):
            errors.append({
                "pump_id": pump["id"],
                "pump_name": f"{pump['marca']} {pump['modelo']}",
                "codigo": error["codigo_pantalla"],
                "video_tag": error["video_tag"],
                "significado": error["significado"],
                "prioridad": error.get("prioridad", "media"),
                "categoria": error.get("categoria", "general"),
                "accion_correctiva": error.get("accion_correctiva", "")
            })
    return errors


def main():
    """Función principal del dashboard con autenticación SQLite"""
    
    # Auto-inicializar DB si no existe o está vacía
    if not DB_PATH.exists():
        init_db()
        # Crear usuario CEO por defecto
        if not get_user_by_email(DEFAULT_CEO_EMAIL):
            create_user(
                email=DEFAULT_CEO_EMAIL,
                password=DEFAULT_CEO_PASSWORD,
                role=DEFAULT_CEO_ROLE,
                name=DEFAULT_CEO_NAME
            )
    else:
        # Verificar si la DB está vacía (sin usuarios)
        try:
            with get_conn() as conn:
                user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                if user_count == 0:
                    # DB existe pero está vacía, crear usuario CEO
                    if not get_user_by_email(DEFAULT_CEO_EMAIL):
                        create_user(
                            email=DEFAULT_CEO_EMAIL,
                            password=DEFAULT_CEO_PASSWORD,
                            role=DEFAULT_CEO_ROLE,
                            name=DEFAULT_CEO_NAME
                        )
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            # Si hay error accediendo a la DB, reinicializarla
            init_db()
            if not get_user_by_email(DEFAULT_CEO_EMAIL):
                create_user(
                    email=DEFAULT_CEO_EMAIL,
                    password=DEFAULT_CEO_PASSWORD,
                    role=DEFAULT_CEO_ROLE,
                    name=DEFAULT_CEO_NAME
                )
    
    # Obtener autenticador desde SQLite
    authenticator, credentials = get_authenticator()
    
    # Login
    authenticator.login()
    
    if st.session_state.get("authentication_status"):
        # Usuario logueado
        username = st.session_state["username"]  # Es el email
        role = get_user_role(username, credentials)
        display_name = get_user_display_name(username, credentials)
        
        # Header
        st.title("💉 Lankamar Admin Dashboard")
        
        # Badge de rol con color
        role_colors = {
            "ceo": "🔴",
            "director": "🟠", 
            "jefe_servicio": "🟡",
            "usuario": "🟢"
        }
        role_badge = role_colors.get(role, "⚪")
        st.markdown(f"**Bienvenido, {display_name}** | {role_badge} Rol: `{role.upper()}`")
        
        # Sidebar con logout y navegación
        with st.sidebar:
            authenticator.logout("🚪 Cerrar Sesión")
            st.markdown("---")
            
            # Info de sesión
            st.caption(f"📧 {username}")
            
            # Menú dinámico según rol
            opciones = get_menu_options(role)
            menu = st.radio("📋 Navegación", opciones)
            
            # Stats rápidos para CEO
            if role == "ceo":
                st.markdown("---")
                st.caption("📊 Quick Stats")
                db_stats = get_db_stats()
                st.metric("Usuarios", db_stats["users"])
                inv_stats = get_invite_stats()
                st.metric("Invitaciones pendientes", inv_stats["pendientes"])
        
        # Cargar datos
        pumps = load_pumps()
        manifest = load_content_manifest()
        all_errors = get_all_errors(pumps)
        
        # Routing según menú
        if menu == "🔍 Buscar Errores":
            render_search_section(all_errors)
        elif menu == "📹 Videos":
            render_videos_section(pumps, manifest, all_errors)
        elif menu == "📊 Estadísticas":
            render_stats_section(manifest, pumps, all_errors)
        elif menu == "📥 Exportar":
            render_export_section(pumps, all_errors)
        elif menu == "🔧 Validación":
            render_validation_section(pumps)
        elif menu == "👥 Usuarios":
            render_users_section()
        elif menu == "🎫 Invitaciones":
            render_invites_section()
    
    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Usuario o contraseña incorrectos")
        st.info("💡 Si tenés un token de invitación, usalo abajo para registrarte")
        render_invite_redemption()
    else:
        st.info("👆 Ingresá tu email y contraseña para acceder")
        st.markdown("---")
        st.markdown("### ¿Tenés un token de invitación?")
        render_invite_redemption()


def render_search_section(all_errors):
    """Sección de búsqueda de errores"""
    st.header("🔍 Buscar Errores y Alarmas")
    
    # Sistema de iconos y colores por CATEGORÍA (basado en UX/gamificación)
    CATEGORY_STYLE = {
        "oclusion": {"icon": "🚫", "color": "#E53935", "nombre": "Oclusión"},
        "aire": {"icon": "🫧", "color": "#90CAF9", "nombre": "Aire en Línea"},
        "flujo": {"icon": "💧", "color": "#3949AB", "nombre": "Flujo"},
        "energia": {"icon": "🪫", "color": "#FFB300", "nombre": "Energía/Batería"},
        "sistema": {"icon": "⚙️", "color": "#8D6E63", "nombre": "Sistema"},
        "set": {"icon": "⚙️", "color": "#43A047", "nombre": "Configuración"},
        "medicacion": {"icon": "💊", "color": "#D81B60", "nombre": "Medicación"},
        "general": {"icon": "⚠️", "color": "#607D8B", "nombre": "General"},
        "volumen": {"icon": "📊", "color": "#5C6BC0", "nombre": "Volumen"},
        "mecanica": {"icon": "🔧", "color": "#795548", "nombre": "Mecánica"},
    }
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔎 Buscar por código o descripción", "")
    with col2:
        pumps_list = list(set(e["pump_name"] for e in all_errors))
        selected_pump = st.selectbox("Bomba", ["Todas"] + sorted(pumps_list))
    with col3:
        categories = list(set(e["categoria"] for e in all_errors))
        selected_cat = st.selectbox("Categoría", ["Todas"] + sorted(categories))
    
    # Filtrar
    filtered = all_errors
    if search_term:
        search_lower = search_term.lower()
        filtered = [e for e in filtered if search_lower in e["codigo"].lower() 
                   or search_lower in e["significado"].lower()]
    if selected_pump != "Todas":
        filtered = [e for e in filtered if e["pump_name"] == selected_pump]
    if selected_cat != "Todas":
        filtered = [e for e in filtered if e["categoria"] == selected_cat]
    
    st.markdown(f"**{len(filtered)} resultados encontrados**")
    st.markdown("---")
    
    # Agrupar por CATEGORÍA
    from collections import defaultdict
    grouped = defaultdict(list)
    for error in filtered:
        grouped[error["categoria"]].append(error)
    
    # Mostrar agrupado por categoría con iconos
    for categoria in sorted(grouped.keys()):
        errors = grouped[categoria]
        # Obtener estilo de la categoría
        style = CATEGORY_STYLE.get(categoria, CATEGORY_STYLE["general"])
        icon = style["icon"]
        color = style["color"]
        nombre = style["nombre"]
        
        # Header de categoría con color e icono
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {color}22, transparent); 
                    padding: 12px 18px; border-left: 5px solid {color}; 
                    border-radius: 0 10px 10px 0; margin: 20px 0 12px 0;
                    display: flex; align-items: center;">
            <span style="font-size: 28px; margin-right: 12px;">{icon}</span>
            <div>
                <strong style="color: {color}; font-size: 18px;">{nombre.upper()}</strong>
                <span style="color: #666; margin-left: 10px; font-size: 14px;">({len(errors)} errores)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Errores de esta categoría
        for error in errors:
            priority_icon = {"critica": "🔴", "alta": "🟠", "media": "🟡", "informativa": "🟢"}
            p_icon = priority_icon.get(error["prioridad"], "⚪")
            
            with st.expander(f"{p_icon} {error['codigo']} — {error['pump_name']}"):
                st.markdown(f"**Significado:** {error['significado']}")
                st.markdown(f"**Acción correctiva:** {error['accion_correctiva']}")
                st.markdown(f"**Bomba:** `{error['pump_name']}` | **Prioridad:** `{error['prioridad']}`")
                st.markdown(f"**Video tag:** `{error['video_tag']}`")


def render_videos_section(pumps, manifest, all_errors):
    """Sección de gestión de videos"""
    st.header("📹 Gestión de Videos")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Agregar Nuevo Video")
        
        with st.form("add_video_form"):
            # Selector de bomba
            pump_options = {f"{p['marca']} {p['modelo']}": p["id"] for p in pumps}
            selected_pump_name = st.selectbox("Bomba", list(pump_options.keys()))
            selected_pump_id = pump_options.get(selected_pump_name)
            
            # Filtrar errores de esa bomba
            pump_errors = [e for e in all_errors if e["pump_id"] == selected_pump_id]
            error_options = {f"{e['codigo']} - {e['significado'][:30]}": e["video_tag"] 
                          for e in pump_errors}
            
            if error_options:
                selected_error = st.selectbox("Error/Alarma", list(error_options.keys()))
                video_tag = error_options.get(selected_error)
            else:
                st.warning("Esta bomba no tiene errores registrados")
                video_tag = None
            
            # URL del video
            video_url = st.text_input(
                "URL del Video",
                placeholder="https://youtube.com/watch?v=... o TikTok/Instagram"
            )
            
            # Plataforma
            platform = st.selectbox("Plataforma", ["YouTube", "TikTok", "Instagram Reels"])
            
            # Notas
            notes = st.text_area("Notas (opcional)", height=80)
            
            submitted = st.form_submit_button("➕ Agregar Video", use_container_width=True)
            
            if submitted and video_url and video_tag:
                new_video = {
                    "video_tag": video_tag,
                    "pump_id": selected_pump_id,
                    "url": video_url,
                    "platform": platform,
                    "notes": notes,
                    "views_count": 0,
                    "added_at": datetime.now().isoformat()
                }
                manifest["videos"].append(new_video)
                save_content_manifest(manifest)
                st.success(f"✅ Video agregado para: {video_tag}")
                st.rerun()
    
    with col2:
        st.subheader("Videos Registrados")
        
        if manifest["videos"]:
            for i, video in enumerate(manifest["videos"]):
                with st.expander(f"🎬 {video['video_tag']} ({video['platform']})"):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**URL:** [{video['url'][:50]}...]({video['url']})")
                        st.markdown(f"**Bomba:** {video['pump_id']}")
                        st.markdown(f"**Vistas:** {video['views_count']}")
                        if video.get("notes"):
                            st.info(video["notes"])
                    with col_b:
                        if st.button("🗑️ Eliminar", key=f"del_{i}"):
                            manifest["videos"].pop(i)
                            save_content_manifest(manifest)
                            st.rerun()
        else:
            st.info("No hay videos registrados aún. Agregá uno desde el formulario.")


def render_stats_section(manifest, pumps, all_errors):
    """Sección de estadísticas con gráficos"""
    st.header("📊 Estadísticas de Uso")
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    total_videos = len(manifest.get("videos", []))
    total_views = sum(v.get("views_count", 0) for v in manifest.get("videos", []))
    total_pumps = len(pumps)
    total_errors = len(all_errors)
    
    col1.metric("Videos", total_videos)
    col2.metric("Vistas Totales", total_views)
    col3.metric("Bombas", total_pumps)
    col4.metric("Errores Documentados", total_errors)
    
    st.markdown("---")
    
    # Gráficos
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Errores por Bomba")
        pump_counts = {}
        for e in all_errors:
            pump_counts[e["pump_name"]] = pump_counts.get(e["pump_name"], 0) + 1
        st.bar_chart(pump_counts)
    
    with col_chart2:
        st.subheader("Errores por Categoría")
        cat_counts = {}
        for e in all_errors:
            cat_counts[e["categoria"]] = cat_counts.get(e["categoria"], 0) + 1
        st.bar_chart(cat_counts)
    
    st.markdown("---")
    
    # Cobertura por bomba
    st.subheader("Cobertura de Videos por Bomba")
    for pump in pumps:
        errors = pump.get("errores_y_alarmas", [])
        covered = sum(1 for e in errors 
                     if any(v["video_tag"] == e["video_tag"] for v in manifest.get("videos", [])))
        total = len(errors)
        
        progress = covered / total if total > 0 else 0
        st.markdown(f"**{pump['marca']} {pump['modelo']}**")
        st.progress(progress, f"{covered}/{total} errores con video")


def render_validation_section(pumps):
    """Sección de validación de datos"""
    st.header("🔧 Validación de Datos")
    
    issues = []
    
    for pump in pumps:
        pump_name = f"{pump['marca']} {pump['modelo']}"
        
        # Verificar campos obligatorios
        required_fields = ["id", "marca", "modelo", "tipo", "specs_tecnicas", "errores_y_alarmas"]
        for field in required_fields:
            if field not in pump:
                issues.append(f"❌ **{pump_name}**: Falta campo `{field}`")
        
        # Verificar specs técnicas
        specs = pump.get("specs_tecnicas", {})
        required_specs = ["rango_flujo", "volumen_max", "tipo_set", "bateria"]
        for spec in required_specs:
            if spec not in specs:
                issues.append(f"⚠️ **{pump_name}**: Falta spec `{spec}`")
        
        # Verificar errores
        for error in pump.get("errores_y_alarmas", []):
            if not error.get("video_tag"):
                issues.append(
                    f"⚠️ **{pump_name}**: Error `{error.get('codigo_pantalla')}` sin video_tag"
                )
    
    if issues:
        st.warning(f"Se encontraron {len(issues)} problemas:")
        for issue in issues:
            st.markdown(issue)
    else:
        st.success("✅ Todos los datos están completos y validados")
    
    # Mostrar estructura JSON
    st.subheader("Vista de Datos")
    selected_pump = st.selectbox(
        "Ver datos de bomba:",
        [f"{p['marca']} {p['modelo']}" for p in pumps]
    )
    idx = [f"{p['marca']} {p['modelo']}" for p in pumps].index(selected_pump)
    st.json(pumps[idx])


def render_validation_section(pumps):
    """Sección de validación de datos"""
    st.header("🔧 Validación de Datos")
    
    issues = []
    
    for pump in pumps:
        pump_name = f"{pump['marca']} {pump['modelo']}"
        
        # Verificar campos obligatorios
        required_fields = ["id", "marca", "modelo", "tipo", "specs_tecnicas", "errores_y_alarmas"]
        for field in required_fields:
            if field not in pump:
                issues.append(f"❌ **{pump_name}**: Falta campo `{field}`")
        
        # Verificar specs técnicas
        specs = pump.get("specs_tecnicas", {})
        required_specs = ["rango_flujo", "volumen_max", "tipo_set", "bateria"]
        for spec in required_specs:
            if spec not in specs:
                issues.append(f"⚠️ **{pump_name}**: Falta spec `{spec}`")
        
        # Verificar errores
        for error in pump.get("errores_y_alarmas", []):
            if not error.get("video_tag"):
                issues.append(
                    f"⚠️ **{pump_name}**: Error `{error.get('codigo_pantalla')}` sin video_tag"
                )
    
    if issues:
        st.warning(f"Se encontraron {len(issues)} problemas:")
        for issue in issues:
            st.markdown(issue)
    else:
        st.success("✅ Todos los datos están completos y validados")
    
    # Mostrar estructura JSON
    st.subheader("Vista de Datos")
    selected_pump = st.selectbox(
        "Ver datos de bomba:",
        [f"{p['marca']} {p['modelo']}" for p in pumps]
    )
    idx = [f"{p['marca']} {p['modelo']}" for p in pumps].index(selected_pump)
    st.json(pumps[idx])


def render_export_section(pumps, all_errors):
    """Sección de exportación de datos"""
    st.header("📥 Exportar Datos")
    
    st.markdown("Descargá los datos en formato CSV para análisis externo.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Errores y Alarmas")
        # Crear CSV de errores
        csv_errors = "Bomba,Código,Significado,Categoría,Prioridad,Acción Correctiva,Video Tag\n"
        for e in all_errors:
            csv_errors += f'"{e["pump_name"]}","{e["codigo"]}","{e["significado"]}","{e["categoria"]}","{e["prioridad"]}","{e["accion_correctiva"]}","{e["video_tag"]}"\n'
        
        st.download_button(
            label="📥 Descargar Errores (CSV)",
            data=csv_errors,
            file_name="lankamar_errores.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption(f"{len(all_errors)} errores en total")
    
    with col2:
        st.subheader("Datos de Bombas")
        # Crear CSV de bombas
        csv_pumps = "ID,Marca,Modelo,Tipo,Rango Flujo,Batería,Cantidad Errores\n"
        for p in pumps:
            specs = p.get("specs_tecnicas", {})
            n_errors = len(p.get("errores_y_alarmas", []))
            csv_pumps += f'"{p["id"]}","{p["marca"]}","{p["modelo"]}","{p["tipo"]}","{specs.get("rango_flujo", "")}","{specs.get("bateria", "")}",{n_errors}\n'
        
        st.download_button(
            label="📥 Descargar Bombas (CSV)",
            data=csv_pumps,
            file_name="lankamar_bombas.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption(f"{len(pumps)} bombas en total")
    
    st.markdown("---")
    st.subheader("JSON Completo")
    
    import json as json_module
    st.download_button(
        label="📥 Descargar Base de Datos Completa (JSON)",
        data=json_module.dumps(pumps, indent=2, ensure_ascii=False),
        file_name="pumps_db_export.json",
        mime="application/json",
        use_container_width=True
    )


# ============================================================
# SECCIONES DE GESTIÓN DE USUARIOS E INVITACIONES (Solo CEO)
# ============================================================

def render_users_section():
    """Sección de gestión de usuarios - Solo CEO"""
    st.header("👥 Gestión de Usuarios")
    
    users = list_users()
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Usuarios", len(users))
    
    role_counts = {}
    for u in users:
        role_counts[u["role"]] = role_counts.get(u["role"], 0) + 1
    
    col2.metric("CEOs", role_counts.get("ceo", 0))
    col3.metric("Directores", role_counts.get("director", 0))
    col4.metric("Usuarios", role_counts.get("usuario", 0))
    
    st.markdown("---")
    
    # Tabla de usuarios
    st.subheader("📋 Lista de Usuarios")
    
    for user in users:
        role_icons = {
            "ceo": "🔴",
            "director": "🟠",
            "jefe_servicio": "🟡",
            "usuario": "🟢"
        }
        icon = role_icons.get(user["role"], "⚪")
        
        with st.expander(f"{icon} {user['email']} — {user.get('name', 'Sin nombre')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Email:** {user['email']}")
                st.markdown(f"**Rol actual:** `{user['role']}`")
                st.markdown(f"**Último login:** {user.get('last_login_at', 'Nunca')}")
                st.markdown(f"**Creado:** {user.get('created_at', 'N/A')[:10]}")
            
            with col2:
                if user["role"] != "ceo":  # No permitir cambiar al CEO
                    new_role = st.selectbox(
                        "Cambiar rol a:",
                        ["usuario", "jefe_servicio", "director"],
                        key=f"role_select_{user['id']}"
                    )
                    if st.button("✅ Aplicar cambio", key=f"role_btn_{user['id']}"):
                        update_user_role(user["id"], new_role)
                        st.success(f"Rol actualizado a: {new_role}")
                        st.rerun()
                else:
                    st.info("🔒 CEO no editable")


def render_invites_section():
    """Sección de gestión de invitaciones - Solo CEO"""
    st.header("🎫 Sistema de Invitaciones")
    
    tab1, tab2, tab3 = st.tabs(["➕ Crear Nueva", "📋 Pendientes", "📜 Historial"])
    
    with tab1:
        st.subheader("Crear Nueva Invitación")
        
        st.markdown("""
        Las invitaciones permiten:
        - 🆕 **Usuarios nuevos**: Se registran con el rol asignado
        - 🔼 **Usuarios existentes**: Elevan su rol al especificado
        """)
        
        with st.form("create_invite_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                inv_role = st.selectbox(
                    "Rol a otorgar",
                    list(ROLES.keys()),
                    format_func=lambda x: f"{ROLES[x]['nombre']} (nivel {ROLES[x]['nivel']})"
                )
            
            with col2:
                inv_hours = st.number_input(
                    "Validez (horas)",
                    min_value=1,
                    max_value=720,  # 30 días
                    value=72  # 3 días
                )
            
            inv_email = st.text_input(
                "Email específico (opcional)",
                placeholder="Dejar vacío para invitación abierta"
            )
            
            st.caption("💡 Si especificás un email, solo esa persona podrá usar el token")
            
            submitted = st.form_submit_button("🎫 Generar Token de Invitación", use_container_width=True)
            
            if submitted:
                try:
                    token = create_invite(
                        role=inv_role,
                        email=inv_email.strip() if inv_email.strip() else None,
                        hours_valid=inv_hours
                    )
                    st.success("✅ ¡Invitación creada exitosamente!")
                    st.code(token, language=None)
                    st.info(f"""
                    📧 Compartí este token con el invitado.
                    
                    **Instrucciones para el invitado:**
                    1. Ir a la página de login
                    2. Pegar el token en "¿Tenés un token de invitación?"
                    3. Ingresar email y contraseña
                    4. ¡Listo! Tendrá rol de **{inv_role.upper()}**
                    """)
                except ValueError as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Invitaciones Pendientes")
        
        # Limpiar expiradas
        if st.button("🧹 Limpiar expiradas"):
            cleaned = cleanup_expired_invites()
            st.success(f"Se eliminaron {cleaned} invitaciones expiradas")
            st.rerun()
        
        invites = list_invites(include_used=False)
        
        if not invites:
            st.info("No hay invitaciones pendientes")
        else:
            for inv in invites:
                status_icon = {"pendiente": "🟡", "usado": "✅", "expirado": "⏰"}
                icon = status_icon.get(inv.get("status", "pendiente"), "⚪")
                
                role_name = ROLES.get(inv["role"], {}).get("nombre", inv["role"])
                
                with st.expander(f"{icon} Token para **{role_name}** — {inv.get('status', 'pendiente')}"):
                    st.code(inv["token"], language=None)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Rol:** {role_name}")
                        if inv["email"]:
                            st.markdown(f"**Para:** {inv['email']}")
                        else:
                            st.markdown("**Para:** Cualquiera (abierta)")
                    
                    with col2:
                        st.markdown(f"**Expira:** {inv['expires_at'][:16] if inv['expires_at'] else 'Nunca'}")
                        st.markdown(f"**Creada:** {inv['created_at'][:16]}")
                    
                    if st.button("❌ Revocar", key=f"revoke_{inv['id']}"):
                        revoke_invite(inv["token"])
                        st.success("Invitación revocada")
                        st.rerun()
    
    with tab3:
        st.subheader("Historial Completo")
        
        all_invites = list_invites(include_used=True, include_expired=True)
        
        if not all_invites:
            st.info("No hay invitaciones en el historial")
        else:
            # Stats
            stats = get_invite_stats()
            cols = st.columns(4)
            cols[0].metric("Total", stats["total"])
            cols[1].metric("Pendientes", stats["pendientes"])
            cols[2].metric("Usadas", stats["usadas"])
            cols[3].metric("Expiradas", stats["expiradas"])
            
            st.markdown("---")
            
            for inv in all_invites:
                status = inv.get("status", "pendiente")
                status_colors = {"pendiente": "🟡", "usado": "✅", "expirado": "⏰"}
                
                st.markdown(f"""
                {status_colors.get(status, '⚪')} `{inv['token'][:20]}...` → **{inv['role']}** 
                | Estado: {status} | {inv['created_at'][:10]}
                """)


def render_invite_redemption():
    """Formulario para canjear una invitación (visible en login)"""
    
    with st.expander("🎫 Canjear Token de Invitación", expanded=False):
        st.markdown("""
        Si recibiste un token de invitación, usalo aquí para:
        - **Crear tu cuenta** con un rol especial
        - **Elevar tu rol** si ya tenés cuenta
        """)
        
        with st.form("redeem_invite_form"):
            token = st.text_input("Token de invitación", placeholder="Pegá tu token aquí")
            email = st.text_input("Tu email", placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password", 
                                    placeholder="Solo si sos usuario nuevo")
            
            st.caption("⚠️ La contraseña solo es requerida para usuarios nuevos")
            
            submitted = st.form_submit_button("🚀 Canjear Invitación", use_container_width=True)
            
            if submitted:
                if not token or not email:
                    st.error("Token y email son requeridos")
                else:
                    try:
                        result = redeem_invite(
                            token=token.strip(),
                            email=email.strip(),
                            password=password if password else None
                        )
                        st.success(f"✅ {result['message']}")
                        if result["is_new_user"]:
                            st.info("Ahora podés iniciar sesión con tu email y contraseña")
                        else:
                            st.info("Tu rol ha sido actualizado. Cerrá sesión y volvé a entrar para ver los cambios.")
                        st.balloons()
                    except ValueError as e:
                        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()

