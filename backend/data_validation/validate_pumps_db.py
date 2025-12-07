"""
Script de Validación de pumps_db.json
Detecta campos faltantes, inconsistencias y genera reporte

Ejecutar: python validate_pumps_db.py
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any

# Ruta al archivo de datos
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "pumps_db.json"


def load_pumps_db() -> List[Dict]:
    """Carga el archivo JSON de bombas"""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo {DATA_PATH}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: JSON inválido - {e}")
        return []


def validate_required_fields(pump: Dict) -> List[str]:
    """Valida que existan todos los campos obligatorios"""
    issues = []
    required = {
        "root": ["id", "marca", "modelo", "tipo", "prevalencia_arg", 
                 "specs_tecnicas", "interfaz", "errores_y_alarmas"],
        "specs_tecnicas": ["rango_flujo", "volumen_max", "tipo_set", "bateria"],
        "interfaz": ["pantalla", "teclado", "navegacion"]
    }
    
    pump_name = f"{pump.get('marca', '?')} {pump.get('modelo', '?')}"
    
    # Campos raíz
    for field in required["root"]:
        if field not in pump:
            issues.append(f"[{pump_name}] Falta campo obligatorio: `{field}`")
    
    # Specs técnicas
    specs = pump.get("specs_tecnicas", {})
    for field in required["specs_tecnicas"]:
        if field not in specs:
            issues.append(f"[{pump_name}] Falta spec técnica: `{field}`")
    
    # Interfaz
    interfaz = pump.get("interfaz", {})
    for field in required["interfaz"]:
        if field not in interfaz:
            issues.append(f"[{pump_name}] Falta campo de interfaz: `{field}`")
    
    return issues


def validate_flow_range(pump: Dict) -> List[str]:
    """Valida que el rango de flujo sea parseable"""
    issues = []
    pump_name = f"{pump.get('marca', '?')} {pump.get('modelo', '?')}"
    
    rango_flujo = pump.get("specs_tecnicas", {}).get("rango_flujo", "")
    
    # Patrón esperado: "0.5 - 999 ml/h"
    pattern = r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*ml/h"
    match = re.match(pattern, rango_flujo, re.IGNORECASE)
    
    if not match:
        issues.append(
            f"[{pump_name}] Formato de rango_flujo inválido: '{rango_flujo}' "
            f"(esperado: 'X - Y ml/h')"
        )
    else:
        min_flow = float(match.group(1))
        max_flow = float(match.group(2))
        
        if min_flow >= max_flow:
            issues.append(
                f"[{pump_name}] Rango de flujo ilógico: min ({min_flow}) >= max ({max_flow})"
            )
        
        if max_flow > 2000:
            issues.append(
                f"[{pump_name}] ⚠️ Flujo máximo muy alto ({max_flow} ml/h) - verificar"
            )
    
    return issues


def validate_errors(pump: Dict) -> List[str]:
    """Valida la estructura de errores y alarmas"""
    issues = []
    pump_name = f"{pump.get('marca', '?')} {pump.get('modelo', '?')}"
    
    errores = pump.get("errores_y_alarmas", [])
    
    if not errores:
        issues.append(f"[{pump_name}] ⚠️ No tiene errores documentados")
        return issues
    
    video_tags = set()
    
    for i, error in enumerate(errores):
        error_id = error.get("codigo_pantalla", f"Error #{i}")
        
        # Campos obligatorios de error
        required = ["codigo_pantalla", "significado", "accion_correctiva", "video_tag"]
        for field in required:
            if field not in error or not error[field]:
                issues.append(f"[{pump_name}] Error '{error_id}' - falta: `{field}`")
        
        # Video tag único
        video_tag = error.get("video_tag", "")
        if video_tag in video_tags:
            issues.append(
                f"[{pump_name}] Video tag duplicado: '{video_tag}'"
            )
        video_tags.add(video_tag)
        
        # Longitud de acción correctiva
        accion = error.get("accion_correctiva", "")
        if len(accion) < 10:
            issues.append(
                f"[{pump_name}] Error '{error_id}' - acción correctiva muy corta"
            )
    
    return issues


def validate_missing_clinical_fields(pump: Dict) -> List[str]:
    """Detecta campos clínicos que podrían faltar para simulación completa"""
    issues = []
    pump_name = f"{pump.get('marca', '?')} {pump.get('modelo', '?')}"
    
    # Campos clínicos sugeridos (no obligatorios pero útiles)
    specs = pump.get("specs_tecnicas", {})
    
    suggested_specs = {
        "presion_max": "Presión máxima de oclusión (ej: '300 mmHg')",
        "precision_flujo": "Precisión del flujo (ej: '+/- 5%')",
        "sensibilidad_aire": "Sensibilidad del detector de aire (ej: '50 µl')"
    }
    
    for field, description in suggested_specs.items():
        if field not in specs:
            issues.append(
                f"[{pump_name}] 💡 Campo sugerido faltante: `{field}` - {description}"
            )
    
    return issues


def generate_report(pumps: List[Dict]) -> Tuple[List[str], List[str], List[str]]:
    """Genera reporte completo de validación"""
    errors = []      # Problemas críticos
    warnings = []    # Advertencias
    suggestions = [] # Sugerencias
    
    for pump in pumps:
        # Campos obligatorios
        field_issues = validate_required_fields(pump)
        errors.extend(field_issues)
        
        # Rango de flujo
        flow_issues = validate_flow_range(pump)
        errors.extend([i for i in flow_issues if "inválido" in i or "ilógico" in i])
        warnings.extend([i for i in flow_issues if "⚠️" in i])
        
        # Errores y alarmas
        error_issues = validate_errors(pump)
        errors.extend([i for i in error_issues if "falta" in i.lower()])
        warnings.extend([i for i in error_issues if "⚠️" in i])
        
        # Campos clínicos sugeridos
        clinical_issues = validate_missing_clinical_fields(pump)
        suggestions.extend(clinical_issues)
    
    return errors, warnings, suggestions


def main():
    print("=" * 60)
    print("🔬 VALIDACIÓN DE pumps_db.json - Simulador BIC Lankamar")
    print("=" * 60)
    print()
    
    pumps = load_pumps_db()
    
    if not pumps:
        print("No se pudieron cargar los datos.")
        return 1
    
    print(f"📦 Cargadas {len(pumps)} bombas de infusión")
    print()
    
    errors, warnings, suggestions = generate_report(pumps)
    
    # Mostrar errores
    if errors:
        print("❌ ERRORES CRÍTICOS:")
        print("-" * 40)
        for e in errors:
            print(f"  • {e}")
        print()
    
    # Mostrar advertencias
    if warnings:
        print("⚠️ ADVERTENCIAS:")
        print("-" * 40)
        for w in warnings:
            print(f"  • {w}")
        print()
    
    # Mostrar sugerencias
    if suggestions:
        print("💡 SUGERENCIAS (campos opcionales faltantes):")
        print("-" * 40)
        for s in suggestions:
            print(f"  • {s}")
        print()
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN:")
    print(f"   Errores críticos: {len(errors)}")
    print(f"   Advertencias:     {len(warnings)}")
    print(f"   Sugerencias:      {len(suggestions)}")
    print("=" * 60)
    
    if errors:
        print("\n🚨 HAY ERRORES CRÍTICOS - El JSON necesita corrección")
        return 1
    elif warnings:
        print("\n⚠️ Sin errores críticos pero hay advertencias a revisar")
        return 0
    else:
        print("\n✅ VALIDACIÓN EXITOSA - Datos completos")
        return 0


if __name__ == "__main__":
    exit(main())
