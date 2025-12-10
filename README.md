# 💉 SiBIC - Simulador de Bombas de Infusión Continua

**App educativa móvil SiBIC para simulación de bombas de infusión en enfermería argentina.**

> Reduciendo errores críticos en UCI mediante simulación digital.

---

## 🎯 Objetivo

Herramienta de bolsillo que permite a enfermeros/as:
1. **Identificar** el modelo de bomba mediante una foto (IA)
2. **Simular** la interfaz operativa para practicar sin riesgo
3. **Resolver** fallas mediante guías rápidas y videos

## 📱 Bombas Soportadas

### Modelos Principales (MVP)

| Marca | Modelo | Prevalencia |
|-------|--------|-------------|
| Baxter | Sigma Spectrum | Alta (Privado/UCI) |
| B. Braun | Infusomat Space | Alta (Público/Privado) |
| Innovo | MI-20 | Media (Hospitales Provinciales) |

### Modelos Adicionales

| Marca | Modelo | Prevalencia |
|-------|--------|-------------|
| Mindray | BeneFusion SP5 | Media-Alta (UCI) |
| Samtronic | ST-670 | Media (Hospitales Públicos) |
| BD | Alaris System | Alta (Privado/UCI) |
| Fresenius Kabi | Agilia VP | Baja-Media (UCI Privado) |
| Hospira | Plum A+ | Alta (Público/Privado) |
| Terumo | TE-331 | Media (Hospitales Públicos) |
| IMED | Gemini PC-2TX | Baja (Equipos Legacy) |
| Smiths Medical | CADD-Solis | Media (Oncología/Paliativos) |

**Total: 11 modelos de bombas con 136+ alarmas y errores documentados**

## 🛠️ Stack Tecnológico

- **Frontend:** Flutter (Dart)
- **Backend:** Python (FastAPI)
- **Dashboard:** Streamlit
- **Data:** JSON local (Offline-First)

## 📂 Estructura

```
├── lib/              # Flutter App
├── backend/          # Python scripts & dashboard
├── data/             # JSON databases
└── docs/             # PRD, Arquitectura, Pitch Deck
```

## 🚀 Quick Start

```bash
# Validar datos
cd backend/data_validation
python validate_pumps_db.py

# Dashboard admin
cd backend
streamlit run admin_dashboard.py

# App Flutter (requiere Flutter SDK)
flutter run
```

## 🚪 Acceso Público

- 💻 Desktop: https://simulador-bic-lankamar-mhua3wowwbhztwwbbcdwyq.streamlit.app
- 📱 Mobile (optimizado): https://simulador-bic-lankamar-mhua3wowwbhztwwbbcdwyq.streamlit.app?mobile=true

Recomendación: para usuarios en celular compartí el link con `?mobile=true`.

## 📣 Distribución pública

- La app detecta el dispositivo móvil y recarga automáticamente con la interfaz táctil; no se requiere que el usuario agregue parámetros.
- Para guiar la distribución y uso de tokens revisá `docs/DISTRIBUCION_PUBLICA.md`.

## 📘 Guía de bombas impresa

- Consulta el PDF `docs/SiBIC_BOMBAS_REFERENCIA.pdf` para tener una versión imprimible de las 7 bombas con procedimientos y tabla comparativa.
- Para regenerar el PDF usa `scripts/generate_pdf_bombas.py` (requiere `reportlab`).

## 📄 Licencia

Propietario: **Marcelo Lancry (Lankamar)** - Todos los derechos reservados.

---

*Desarrollado en Argentina 🇦🇷 para enfermería argentina.*
