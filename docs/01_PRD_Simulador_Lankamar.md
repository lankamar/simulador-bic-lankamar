# 📄 PRD: Simulador de Bombas de Infusión (BIC) "Lankamar"

**Versión:** 1.0
**Propietario:** Marcelo Lancry (Lankamar)
**Objetivo:** Desarrollar una aplicación móvil educativa para enfermería que combine reconocimiento visual (IA) y simulación interactiva de las bombas de infusión más usadas en Argentina para reducir errores críticos en UCI.

---

## 1. Resumen Ejecutivo
Existe una brecha crítica en la capacitación de enfermería respecto al uso de bombas específicas, lo que genera errores de programación y alarmas no resueltas. La solución es una herramienta de bolsillo que permita:
1.  **Identificar** el modelo de bomba mediante una foto (IA/OCR).
2.  **Simular** la interfaz operativa (botonera y pantalla) para practicar sin riesgo.
3.  **Resolver** fallas (Troubleshooting) mediante guías rápidas y una base de datos de videos cortos.

---

## 2. Alcance del MVP (Producto Mínimo Viable)
El lanzamiento inicial se limitará a los 3 modelos con mayor cuota de mercado en Argentina:
1.  **Baxter Sigma Spectrum** (Líder en sector privado/UCI).
2.  **B. Braun Infusomat Space** (Estándar en terapias intensivas).
3.  **Innovo MI-20** (Prevalente en hospitales públicos y provinciales).

---

## 3. Perfil de Usuario (User Personas)
* **Estudiante de Enfermería:** Necesita aprender la lógica básica (goteo, volumen) y perder el miedo a "tocar botones" antes de llegar a la práctica.
* **Enfermero/a UCI (Recertificación):** Se enfrenta a un equipo nuevo en una guardia y necesita saber rápido cómo purgarlo o qué significa el error "AIR" o "OCL".

---

## 4. Requerimientos Funcionales (Los Módulos)

### Módulo A: "Lankamar Vision" (Escáner IA)
* **Input:** El usuario toma una foto de la bomba real con la cámara del celular.
* **Proceso:** Un modelo de visión (IA) analiza la imagen y clasifica el dispositivo.
* **Output:** Identificación inmediata del modelo (Ej: *"Detectada: Baxter Sigma Spectrum"*).
* **Acción:** Redirección automática al menú de ese modelo específico.

### Módulo B: El Simulador (El "Fierro")
Interfaz gráfica interactiva que replica la botonera física en la pantalla del celular.

**1. Para Baxter Sigma Spectrum:**
* **UI:** Pantalla color, teclas de función laterales (Soft Keys), sin teclado numérico físico.
* **Lógica Crítica:** Simular carga de guía (Set azul específico) y uso de la "Drug Library".

**2. Para B. Braun Infusomat Space:**
* **UI:** Diseño modular vertical, navegación por flechas y teclado en pantalla.
* **Lógica Crítica:** Simular apertura de puerta mecánica y colocación de clips de seguridad del set.

**3. Para Innovo MI-20:**
* **UI:** Pantalla LCD simple monocromática, botones físicos rígidos.
* **Lógica Crítica:** Configuración manual de parámetros simples; uso de guías genéricas.

### Módulo C: Troubleshooting y Video-Bicicleta
Por cada bomba, el sistema debe ofrecer una lista de "Acciones Rápidas" vinculadas a una base de datos de videos (Youtube/TikTok/Reels):
* **Errores:** Tabla de códigos (Ej: "Oclusión", "Aire", "Batería Baja").
* **Solución:** Al tocar el error, despliega:
    1.  Explicación texto corto (Paso a paso).
    2.  Video embebido de 15-30 seg (Loop) mostrando la maniobra física (ej: golpear cámara de goteo).

---

## 5. Requerimientos Técnicos
* **Offline First:** La app debe funcionar sin internet (los manuales y simuladores básicos se descargan). Los videos pueden requerir conexión o caché inteligente.
* **Plataforma:** Android (prioridad por volumen en sector público) e iOS.
* **Arquitectura de Datos:** Base de datos JSON local con los parámetros de cada bomba (Rango de flujo, Vol max, Alarmas).

---

## 6. Criterios de Éxito (KPIs)
* **Precisión del Escáner:** >80% de aciertos al identificar el modelo.
* **Fidelidad de Simulación:** Que los pasos para programar "100 ml/h" en la app sean idénticos a la bomba real.
