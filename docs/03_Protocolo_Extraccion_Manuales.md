# 📚 Protocolo de Extracción desde Manuales Técnicos

**Versión:** 1.0  
**Rol:** Ingeniero Clínico + Data Engineer de Contenido

## 1. Objetivo

Procesar **manuales técnicos de bombas de infusión** (IFU, Operator's Manual, Service Manual) y generar fichas estructuradas para alimentar `pumps_db.json` y la lógica del simulador.

---

## 2. Formatos de Manuales Aceptables

Solo extraer datos técnicos de:

| Tipo de Documento | ¿Usar? | Notas |
|-------------------|--------|-------|
| Manual de Usuario / Operator's Manual / IFU | ✅ Sí | Fuente principal |
| Manual de Servicio / Service Manual | ✅ Sí | Si incluye alarmas/códigos |
| Guías de Prueba / Infusion Pump Testing Guides | ✅ Sí | Para umbrales |
| Field Safety Notices / Device Corrections | ✅ Sí | Para alarmas críticas |
| Brochure comercial / Ficha de producto | ❌ No | Marcar como "FORMATO NO TÉCNICO" |

---

## 3. Plantilla de Extracción por Bomba

### 3.1 Modelo y Marca
```json
{
  "marca": "Nombre exacto del fabricante",
  "modelo": "Modelo exacto como aparece",
  "descripcion_pantalla": "LCD/TFT/Color/Mono, tamaño, iconos relevantes"
}
```

### 3.2 Botonera
Lista de botones físicos y/o soft-keys:

| Botón/Ícono | Función |
|-------------|---------|
| START / ▶ | Iniciar infusión |
| STOP | Detener infusión |
| ... | ... |

### 3.3 Algoritmo de Uso
Pasos para:
1. **Programar infusión continua** (ml/h o mcg/kg/min)
2. **Purgado/Cebado** del sistema
3. **Programar bolus** (si aplica)

> ⚠️ Solo describir lo explícito en el manual, NO inventar.

---

## 4. 🚨 Tabla de Errores y Alarmas (PRIORIDAD MÁXIMA)

Generar usando EXCLUSIVAMENTE lo que esté en el texto:

| Mensaje en Pantalla | Significado | Acción Correctiva |
|---------------------|-------------|-------------------|
| `AIR IN LINE` | Aire detectado en tubuladura | Purgar, verificar conexiones |
| `DOWNSTREAM OCCLUSION` | Oclusión hacia el paciente | Verificar acceso venoso, clamps |
| `LOW BATTERY` | Batería < 20% | Conectar a red AC |

> ⚠️ Si el manual no trae tabla de mensajes, NO inventar.

---

## 5. Energía y Batería

### 5.1 Plantilla de Energía

```json
"energia_bateria": {
  "tipo_alimentacion": "AC 100-240V 50/60Hz",
  "tipo_bateria": "Ion-Litio / NiMH / SLA",
  "capacidad": "mAh si figura",
  "autonomia_declarada": "X horas @ Y ml/h",
  "tiempo_recarga": "X horas (0-100%)",
  "alarmas_energia": [
    "LOW BATTERY",
    "VERY LOW BATTERY", 
    "BATTERY EMPTY",
    "AC FAIL",
    "POWER FAILURE"
  ]
}
```

### 5.2 Checklist de Prueba de Batería

1. ☐ Cargar batería al 100% según manual
2. ☐ Ajustar flujo clínico típico (ej: 100 ml/h)
3. ☐ Desconectar de red AC y medir:
   - Tiempo hasta primera alarma LOW BATTERY
   - Tiempo hasta apagado / BATTERY EMPTY
4. ☐ Comparar vs valor declarado
5. ☐ Definir umbral conservador (70% de autonomía declarada)

---

## 6. Umbrales de Oclusión y Aire

### 6.1 Oclusión (Presión)

```json
"umbrales": {
  "oclusion_mmhg": "30-300 configurable (Low/Medium/High)",
  "oclusion_upstream": "Si diferenciado",
  "oclusion_downstream": "Si diferenciado"
}
```

### 6.2 Aire en Línea

```json
"umbrales": {
  "aire_ml": ">1 ml acumulado en 15 min",
  "burbuja_max": "Tamaño máximo permitido (si especifica)"
}
```

> Si NO hay valores numéricos:
> `"UMBRAL NUMÉRICO NO ESPECIFICADO EN EL DOCUMENTO PARA EL MODELO [NOMBRE]"`

---

## 7. Criterios para Marcar Modelos Incompletos

Agregar flags al array `datos_incompletos`:

| Condición | Flag a Agregar |
|-----------|----------------|
| Sin mensajes de error/alarma | `FALTAN DATOS DE ERRORES` |
| Sin descripción de botonera | `FALTAN DATOS DE BOTONERA` |
| Sin pasos de programación | `FALTAN DATOS DE ALGORITMO` |
| Sin detalles de batería | `FALTAN DATOS DE ENERGÍA/BATERÍA` |
| Documento es brochure | `FORMATO NO TÉCNICO` |
| Manual incompleto | `MANUAL_COMPLETO` |

### Ejemplo de JSON con Flags:

```json
{
  "id": "samtronic_st670",
  "marca": "Samtronic",
  "modelo": "ST-670",
  "datos_incompletos": [
    "FALTAN DATOS DE BOTONERA",
    "MANUAL_TECNICO_NO_DISPONIBLE"
  ]
}
```

---

## 8. Integración con Validación

Los flags se detectan automáticamente en:

- **`validate_pumps_db.py`**: Reporta modelos con datos faltantes
- **Dashboard Streamlit**: Muestra lista de "modelos a priorizar"

---

## 9. Fuentes de Referencia

| Recurso | URL/Ubicación |
|---------|---------------|
| Rigel Medical Guide | rigelmedical.com |
| Frank's Hospital Workshop | frankshospitalworkshop.com |
| FDA Infusion Pump Problems | fda.gov |
| IFU de fabricantes | Sitios oficiales Baxter, B.Braun, BD, Fresenius |

---

*Documento creado según el Prompt Maestro v1.0 - Simulador BIC Lankamar*
