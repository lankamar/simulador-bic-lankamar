# 🌐 ACCESO PÚBLICO - SiBIC - Simulador de Bombas de Infusión Continua

## URLs de Acceso

### Desktop (Completo)
https://simulador-bic-lankamar-mhua3wowwbhztwwbbcdwyq.streamlit.app

### Mobile (Optimizado para celular)
https://simulador-bic-lankamar-mhua3wowwbhztwwbbcdwyq.streamlit.app?mobile=true

## Características por dispositivo

**Desktop:**
- Dashboard completo con sidebar
- Búsqueda de errores
- Gráficos y estadísticas
- Gestión de videos
- Administración de usuarios e invitaciones

**Mobile:**
- Interfaz simplificada (tabs en lugar de sidebar)
- Búsqueda de errores con resultados táctiles
- Listado de bombas con botones grandes
- Compartir enlace con `?mobile=true`

## Tokens de Acceso

Ver sección "Invitaciones" en el dashboard para generar tokens.

## Detección automática de dispositivos

El dashboard detecta automáticamente el User-Agent del navegador y recarga con `?mobile=true` para mostrar la UI táctil en celulares. No hace falta que los usuarios modifiquen la URL; el script está integrado en la carga de la página.

## Nota técnica

La detección mobile se implementa con un script que revisa el User-Agent y recarga la URL con `?mobile=true` cuando reconoce un dispositivo táctil. De esta manera, los usuarios no necesitan cambiar manualmente la dirección.

Ver `docs/DISTRIBUCION_PUBLICA.md` para conocer la forma planificada de compartir enlaces y tokens.
