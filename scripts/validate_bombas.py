import json
from pathlib import Path

def ensure_keys(item, required):
    missing = [k for k in required if k not in item]
    if missing:
        raise ValueError(f"Faltan llaves {missing} en {item.get('name', item.get('id'))}")


def main():
    json_path = Path(__file__).resolve().parent.parent / "data" / "bombas_especificaciones.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("El JSON debe ser una lista de bombas.")

    if len(data) != 7:
        raise ValueError(f"Esperaba 7 bombas pero encontré {len(data)}.")

    required_root_keys = ["id", "name", "manufacturer", "category", "specs", "views", "buttons", "operations"]
    required_specs = ["dimensions", "weight", "battery_type", "display"]
    required_views = ["frontal", "lateral", "trasera"]

    for bomba in data:
        ensure_keys(bomba, required_root_keys)
        ensure_keys(bomba["specs"], required_specs)
        ensure_keys(bomba["views"], required_views)

        if not isinstance(bomba["buttons"], list) or not bomba["buttons"]:
            raise ValueError(f"La bomba {bomba['name']} debe tener al menos un botón documentado.")
        if not isinstance(bomba["operations"], list) or len(bomba["operations"]) < 3:
            raise ValueError(f"La bomba {bomba['name']} debe listar los 3 procedimientos obligatorios.")
        for op in bomba["operations"]:
            ensure_keys(op, ["name", "steps", "video_url"])
            if not isinstance(op["steps"], list) or not all(isinstance(step, str) for step in op["steps"]):
                raise ValueError(f"Los pasos de {op['name']} en {bomba['name']} deben ser una lista de cadenas.")

    print("✅ JSON válido: 7 bombas completas y con todas las claves obligatorias.")


if __name__ == "__main__":
    main()
