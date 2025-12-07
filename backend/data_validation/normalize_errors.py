"""
Normalizador de Textos de Errores
Transforma códigos crípticos a texto buscable para la app

Ejecutar: python normalize_errors.py
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Ruta al archivo de datos
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "pumps_db.json"

# Diccionario de sinónimos y normalizaciones
NORMALIZATION_MAP: Dict[str, List[str]] = {
    # Aire
    "aire en línea": [
        "air", "air in line", "burbuja", "bubble", "emergencia de aire",
        "err 2: burbuja", "air detected", "aire detectado"
    ],
    # Oclusión
    "oclusión / vía tapada": [
        "occlusion", "occl", "oclusión", "oclusion", "downstream occlusion",
        "upstream occlusion", "presión arriba", "presion arriba",
        "err 1: oclusión", "err 1: oclusion", "vía tapada", "via tapada",
        "pressure", "blocked"
    ],
    # Puerta
    "puerta abierta": [
        "door", "door open", "puerta", "tapa abierta", "cover open"
    ],
    # Batería
    "batería baja": [
        "battery", "bat", "bateria", "low battery", "batería agotada"
    ],
    # Flujo
    "error de flujo": [
        "flow", "flujo", "flow error", "no flow", "sin flujo"
    ],
    # Finalizado
    "infusión completa": [
        "complete", "done", "end", "finish", "vtbi complete", 
        "volumen infundido", "infusion complete"
    ],
    # Set / Cassette
    "error de set": [
        "cassette", "set", "tubing", "tubuladura", "set error"
    ]
}


def normalize_error_text(raw_code: str) -> Tuple[str, List[str]]:
    """
    Normaliza un código de error críptico a texto buscable.
    
    Args:
        raw_code: Código tal como aparece en pantalla (ej: "AIR IN LINE")
    
    Returns:
        Tuple con (texto_normalizado, lista_de_sinónimos)
    """
    # Limpiar el texto
    cleaned = raw_code.lower().strip()
    cleaned = re.sub(r'[:\-_]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Buscar en el mapa de normalizaciones
    for normalized_text, keywords in NORMALIZATION_MAP.items():
        for keyword in keywords:
            if keyword in cleaned:
                # Retornar el texto normalizado y sinónimos relacionados
                synonyms = [k for k in keywords if k != keyword]
                return normalized_text, synonyms
    
    # Si no se encuentra, retornar el texto limpio
    return cleaned.title(), []


def build_search_index(pumps: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Construye un índice de búsqueda invertido para errores.
    
    Permite buscar por cualquier término y encontrar el error correspondiente.
    """
    index = {}
    
    for pump in pumps:
        pump_id = pump["id"]
        pump_name = f"{pump['marca']} {pump['modelo']}"
        
        for error in pump.get("errores_y_alarmas", []):
            codigo = error["codigo_pantalla"]
            normalized, synonyms = normalize_error_text(codigo)
            
            # Crear entrada del error
            error_entry = {
                "pump_id": pump_id,
                "pump_name": pump_name,
                "codigo_original": codigo,
                "codigo_normalizado": normalized,
                "significado": error["significado"],
                "accion_correctiva": error["accion_correctiva"],
                "video_tag": error["video_tag"]
            }
            
            # Agregar al índice por múltiples términos
            search_terms = [
                normalized.lower(),
                codigo.lower(),
                *[s.lower() for s in synonyms],
                *codigo.lower().split(),
                *normalized.lower().split()
            ]
            
            for term in set(search_terms):
                if term not in index:
                    index[term] = []
                index[term].append(error_entry)
    
    return index


def search_errors(index: Dict, query: str) -> List[Dict]:
    """
    Busca errores en el índice por cualquier término.
    """
    query = query.lower().strip()
    results = []
    seen = set()
    
    for term, entries in index.items():
        if query in term or term in query:
            for entry in entries:
                key = (entry["pump_id"], entry["codigo_original"])
                if key not in seen:
                    seen.add(key)
                    results.append(entry)
    
    return results


def generate_normalized_export(pumps: List[Dict]) -> List[Dict]:
    """
    Genera una versión del JSON con textos normalizados agregados.
    """
    output = []
    
    for pump in pumps:
        pump_copy = pump.copy()
        errores_normalizados = []
        
        for error in pump.get("errores_y_alarmas", []):
            error_copy = error.copy()
            normalized, synonyms = normalize_error_text(error["codigo_pantalla"])
            
            error_copy["codigo_normalizado"] = normalized
            error_copy["sinonimos"] = synonyms
            errores_normalizados.append(error_copy)
        
        pump_copy["errores_y_alarmas"] = errores_normalizados
        output.append(pump_copy)
    
    return output


def main():
    print("=" * 60)
    print("🔤 NORMALIZADOR DE ERRORES - Simulador BIC Lankamar")
    print("=" * 60)
    print()
    
    # Cargar datos
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            pumps = json.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró {DATA_PATH}")
        return 1
    
    print(f"📦 Cargadas {len(pumps)} bombas")
    print()
    
    # Mostrar normalizaciones
    print("📋 NORMALIZACIONES APLICADAS:")
    print("-" * 40)
    
    for pump in pumps:
        pump_name = f"{pump['marca']} {pump['modelo']}"
        print(f"\n{pump_name}:")
        
        for error in pump.get("errores_y_alarmas", []):
            original = error["codigo_pantalla"]
            normalized, synonyms = normalize_error_text(original)
            
            print(f"  '{original}'")
            print(f"    → {normalized}")
            if synonyms:
                print(f"    📎 Sinónimos: {', '.join(synonyms[:3])}")
    
    # Generar índice de búsqueda
    print("\n" + "=" * 60)
    print("🔍 ÍNDICE DE BÚSQUEDA GENERADO")
    print("=" * 60)
    
    index = build_search_index(pumps)
    print(f"\nTérminos indexados: {len(index)}")
    
    # Demo de búsqueda
    test_queries = ["aire", "oclusión", "door", "burbuja"]
    print("\n📌 Ejemplos de búsqueda:")
    
    for query in test_queries:
        results = search_errors(index, query)
        print(f"\n  Buscar '{query}': {len(results)} resultado(s)")
        for r in results[:2]:
            print(f"    • [{r['pump_name']}] {r['codigo_normalizado']}")
    
    # Guardar versión normalizada
    output_path = DATA_PATH.parent / "pumps_db_normalized.json"
    normalized_data = generate_normalized_export(pumps)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Archivo normalizado guardado en: {output_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
