# Integración de Códigos de Alarma - Guía de Desarrollo

## 📋 Descripción General

Este documento explica cómo integrar los códigos de alarma de las bombas (Plum 360, Kangaroo OMNI, Flocare Infinity) en la aplicación Flutter del simulador BIC.

## 📁 Archivos de Datos

### 1. `alarms_plum360_complete.json`
- **Bombas**: ICU Medical Plum 360 (IV volumétrica)
- **Total de códigos**: 5 códigos iniciales (E301, E302, N58, DISTAL_OCCLUSION, PROXIMAL_AIR)
- **Estructura**:
  ```json
  {
    "device_id": "icu_medical_plum360",
    "device_name": "ICU Medical Plum 360",
    "alarms": [
      {
        "code": "E301",
        "display_text": "Audio alarm failure",
        "priority": "CRITICAL",
        "probable_cause": "...",
        "nurse_actions": [...],
        "requires_biotech": true
      }
    ]
  }
  ```

### 2. `alarms_kangaroo_flocare.json`
- **Bombas**: Cardinal Health Kangaroo OMNI + Nutricia Flocare Infinity+
- **Total de códigos**: 10 códigos (FEED_ERROR, FLOW_ERROR, OCCLUSION, DOOR_OPEN, LOW_BATT, NO_SET, OCC_IN, OCC_OUT, AIR, BATT)
- **Estructura**: Array de bombas enterales con sus alarmas

## 🔧 Cómo Usar en Flutter

### 1. Cargar los JSON en assets
```yaml
# pubspec.yaml
assets:
  - assets/data/alarms_plum360_complete.json
  - assets/data/alarms_kangaroo_flocare.json
```

### 2. Crear modelo en Dart
```dart
class AlarmCode {
  final String code;
  final String displayText;
  final String priority;
  final String probableCause;
  final List<String> nurseActions;
  final bool requiresBiotech;
  
  AlarmCode.fromJson(Map<String, dynamic> json)
    : code = json['code'],
      displayText = json['display_text'],
      priority = json['priority'],
      probableCause = json['probable_cause'],
      nurseActions = List<String>.from(json['nurse_actions']),
      requiresBiotech = json['requires_biotech'];
}
```

### 3. Cargar datos al iniciar
```dart
future<List<AlarmCode>> loadPlum360Alarms() async {
  final jsonString = await rootBundle.loadString('assets/data/alarms_plum360_complete.json');
  final jsonData = jsonDecode(jsonString);
  final alarms = jsonData['alarms'] as List;
  return alarms.map((a) => AlarmCode.fromJson(a)).toList();
}
```

## 🎮 Integración en Simulador

1. **Cargar alarma aleatoria**: Seleccionar un código de los JSONs
2. **Mostrar en pantalla**: Código, causa probable, impacto clínico
3. **Usuario elige acciones**: Seleccionar de la lista `nurse_actions`
4. **Scoring automático**: Validar orden y correccion
5. **Feedback**: Mostrar si fue correcto o incorrecto

## 📊 Estadísticas Actuales

| Bomba | Códigos | Año |
|-------|---------|-----|
| Plum 360 | 5 | 2025 |
| Kangaroo OMNI | 5 | 2025 |
| Flocare Infinity | 5 | 2025 |
| **Total** | **15** | - |

## ✅ Próximos Pasos

1. Expandir a 45+ códigos para Plum 360
2. Agregar 30+ códigos para bombas enterales
3. Crear escenarios de simulación complejos
4. Implementar scoring y gamificación
5. Agregar imágenes de las bombas

---

*Última actualización: Diciembre 11, 2025*
