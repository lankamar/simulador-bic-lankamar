"""
Dashboard Admin - Simulador BIC Lankamar
Panel web para gestión de Video-Bicicleta (contenido educativo)

Ejecutar con: streamlit run admin_dashboard.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Lankamar Admin",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rutas de archivos
DATA_DIR = Path(__file__).parent.parent / "data"
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
                "significado": error["significado"]
            })
    return errors


def main():
    # Header
    st.title("💉 Lankamar Admin Dashboard")
    st.markdown("**Gestión de contenido educativo - Video-Bicicleta**")
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/200x80?text=LANKAMAR", use_container_width=True)
    st.sidebar.markdown("---")
    menu = st.sidebar.radio(
        "Navegación",
        ["📹 Videos", "📊 Estadísticas", "🔧 Validación de Datos"]
    )
    
    # Cargar datos
    pumps = load_pumps()
    manifest = load_content_manifest()
    all_errors = get_all_errors(pumps)
    
    if menu == "📹 Videos":
        render_videos_section(pumps, manifest, all_errors)
    elif menu == "📊 Estadísticas":
        render_stats_section(manifest, pumps)
    else:
        render_validation_section(pumps)


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


def render_stats_section(manifest, pumps):
    """Sección de estadísticas"""
    st.header("📊 Estadísticas de Uso")
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    total_videos = len(manifest.get("videos", []))
    total_views = sum(v.get("views_count", 0) for v in manifest.get("videos", []))
    total_pumps = len(pumps)
    total_errors = sum(len(p.get("errores_y_alarmas", [])) for p in pumps)
    
    col1.metric("Videos", total_videos)
    col2.metric("Vistas Totales", total_views)
    col3.metric("Bombas", total_pumps)
    col4.metric("Errores Documentados", total_errors)
    
    st.markdown("---")
    
    # Tabla de videos por vistas
    if manifest.get("videos"):
        st.subheader("Top Videos por Consultas")
        videos_sorted = sorted(
            manifest["videos"], 
            key=lambda x: x.get("views_count", 0), 
            reverse=True
        )
        
        for v in videos_sorted[:10]:
            st.markdown(
                f"- **{v['video_tag']}** ({v['platform']}): "
                f"`{v['views_count']}` consultas"
            )
    
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


if __name__ == "__main__":
    main()
