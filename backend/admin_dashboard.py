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
                "significado": error["significado"],
                "prioridad": error.get("prioridad", "media"),
                "categoria": error.get("categoria", "general"),
                "accion_correctiva": error.get("accion_correctiva", "")
            })
    return errors


def main():
    # Header
    st.title("💉 Lankamar Admin Dashboard")
    st.markdown("**Gestión de contenido educativo - Video-Bicicleta**")
    
    # Sidebar
    st.sidebar.markdown("### 🏥 LANKAMAR")
    st.sidebar.markdown("*Simulador BIC*")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio(
        "Navegación",
        ["🔍 Buscar Errores", "📹 Videos", "📊 Estadísticas", "🔧 Validación de Datos", "📥 Exportar"]
    )
    
    # Cargar datos
    pumps = load_pumps()
    manifest = load_content_manifest()
    all_errors = get_all_errors(pumps)
    
    if menu == "🔍 Buscar Errores":
        render_search_section(all_errors)
    elif menu == "📹 Videos":
        render_videos_section(pumps, manifest, all_errors)
    elif menu == "📊 Estadísticas":
        render_stats_section(manifest, pumps, all_errors)
    elif menu == "📥 Exportar":
        render_export_section(pumps, all_errors)
    else:
        render_validation_section(pumps)


def render_search_section(all_errors):
    """Sección de búsqueda de errores"""
    st.header("🔍 Buscar Errores y Alarmas")
    
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
    
    # Mostrar resultados
    for error in filtered:
        priority_color = {"critica": "🔴", "alta": "🟠", "media": "🟡", "informativa": "🟢"}
        icon = priority_color.get(error["prioridad"], "⚪")
        
        with st.expander(f"{icon} {error['codigo']} - {error['pump_name']}"):
            st.markdown(f"**Significado:** {error['significado']}")
            st.markdown(f"**Acción correctiva:** {error['accion_correctiva']}")
            st.markdown(f"**Categoría:** `{error['categoria']}` | **Prioridad:** `{error['prioridad']}`")
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


if __name__ == "__main__":
    main()
