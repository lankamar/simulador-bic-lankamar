# 🏗️ Arquitectura Técnica y Stack Tecnológico: Simulador BIC Lankamar

**Versión:** 1.0
**Enfoque:** MVP (Producto Mínimo Viable) Escalable.
**Prioridad:** Offline-First (Hospitales sin señal) y Simulación Visual.

## 1. Stack Tecnológico Recomendado

* **Frontend (La App):** **Flutter (Dart)**.
    * *Razón:* Código único para Android/iOS. Excelente para dibujar interfaces personalizadas complejas (Botoneras).
* **Backend & API:** **Python (FastAPI)**.
    * *Razón:* Lenguaje nativo de IA y Data Science. Facilita la integración de scripts de validación de datos.
* **Base de Datos:** **Firebase (Firestore)**.
    * *Razón:* NoSQL (JSON), sincronización tiempo real y **persistencia offline** nativa.
* **Visión Artificial (MVP):** **Google ML Kit** (On-device) o integración API Vision.

---

## 2. Estructura del Proyecto (File Structure)

```text
/simulador-bic-lankamar
│
├── /assets                  # Archivos estáticos
│   ├── /images              # Fotos de referencia (Baxter, Braun, Innovo)
│   ├── /manuals_pdf         # Manuales técnicos descargados
│   └── /icons               # Iconos de alertas (Aire, Oclusión, Batería)
│
├── /lib (Flutter Frontend)
│   ├── /main.dart           # Punto de entrada y Configuración de Rutas
│   ├── /models              # Data Models (Pump, Error, VideoRef)
│   ├── /screens             # Pantallas (Home, ScannerView, SimulationView, LibraryView)
│   ├── /widgets             # Componentes UI (SoftKeys, PumpScreen, ErrorCard)
│   └── /services            # Lógica (PumpDataService, VisionService, VideoService)
│
├── /backend (Python Tools)
│   ├── /api                 # Endpoints (si se requiere servidor central)
│   ├── /data_validation     # Scripts para limpiar el JSON de bombas
│   └── /scrapers            # Scripts para buscar nuevos videos en redes
│
├── /data                    # La Fuente de la Verdad
│   ├── pumps_db.json        # Base de datos maestra de bombas (Specs + Errores)
│   └── content_manifest.json # Metadatos de videos y tutoriales
│
└── README.md                # Instrucciones de despliegue
```

---

## 3. Esquema de Datos (JSON Schema Reference)

El archivo `pumps_db.json` es el núcleo. Debe respetar esta estructura para que el simulador funcione:

* `id`: Identificador único (snake_case).
* `specs_tecnicas`: Datos duros para limitar la simulación (ej: no permitir programar 2000 ml/h si el max es 999).
* `interfaz`: Describe cómo dibujar la pantalla.
* `errores_y_alarmas`: Lista de objetos que vincula el Código de Error -> Solución -> Video Tag.

---

## 4. Instrucciones de Despliegue (Dev Ops)

1.  **Setup:** Instalar Flutter SDK y configurar Android Studio / VS Code.
2.  **Data Load:** Ejecutar script de Python en `/backend/data_validation` para verificar integridad de `pumps_db.json`.
3.  **Run:** `flutter run` apuntando al dispositivo físico o emulador.
