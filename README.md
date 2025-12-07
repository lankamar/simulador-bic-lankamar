# 💉 Simulador BIC Lankamar

**App educativa móvil para simulación de bombas de infusión en enfermería argentina.**

> Reduciendo errores críticos en UCI mediante simulación digital.

---

## 🎯 Objetivo

Herramienta de bolsillo que permite a enfermeros/as:
1. **Identificar** el modelo de bomba mediante una foto (IA)
2. **Simular** la interfaz operativa para practicar sin riesgo
3. **Resolver** fallas mediante guías rápidas y videos

## 📱 Bombas Soportadas (MVP)

| Marca | Modelo | Prevalencia |
|-------|--------|-------------|
| Baxter | Sigma Spectrum | Alta (Privado/UCI) |
| B. Braun | Infusomat Space | Alta (Público/Privado) |
| Innovo | MI-20 | Media (Hospitales Provinciales) |

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

## 📄 Licencia

Propietario: **Marcelo Lancry (Lankamar)** - Todos los derechos reservados.

---

*Desarrollado en Argentina 🇦🇷 para enfermería argentina.*
