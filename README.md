# 🚀 Sistema de Control de Reportes Diarios (V1.0)

![Python](https://shields.io)
![Google Sheets](https://shields.io)
![Google Apps Script](https://shields.io)

Ecosistema de automatización diseñado para recopilar, respaldar en almacenamiento local y cargar reportes diarios de pendientes de ingeniería hacia la nube, delegando el envío programado de correos electrónicos corporativos de forma autónoma.

## 📊 Arquitectura del Ecosistema

---

## 📖 Guía de Despliegue y Configuración en la Nube

> ⚠️ **¡LEEME ANTES DE USAR!** Cada vez que realices una modificación en el código dentro de Google Apps Script, la URL web anterior se bloqueará por seguridad. Es obligatorio generar un nuevo despliegue web siguiendo la nomenclatura de control para que el software local pueda comunicarse con la nube.

### 🔗 1. Cómo Generar e Implementar la URL Web de Producción
1. Dentro del editor de Google Apps Script, haz clic en el botón azul **Implementar** ubicado en la esquina superior derecha.
2. Selecciona **Gestionar implementaciones** del menú desplegable.
3. Haz clic en el icono del **Lápiz (Editar)** correspondiente a tu implementación activa.
4. En el apartado de **Versión**, cámbialo obligatoriamente a **Nueva versión**.
5. *(Opcional)* En el campo de descripción o notas, te sugerimos colocar el nombre **`leeeme`** o la versión actual para identificar rápidamente que es el despliegue vigente que alimenta la API.
6. Asegúrate de configurar los accesos globales:
   * **Ejecutar como:** Tú (Tu cuenta de correo corporativa/personal).
   * **Quién tiene acceso:** Cualquiera. *(Paso indispensable para que Python conecte sin credenciales)*.
7. Haz clic en **Implementar**, copia la dirección generada que termina en `/exec` y pégala en la variable `URL_APPLICACION_WEB` dentro de tu archivo local de Python.

### ⏱️ 2. Cómo Configurar los Activadores Automáticos (Triggers)
Para que el script reaccione de forma autónoma en los servidores de Google sin necesidad de mantener la computadora encendida, configura los temporizadores mediante la interfaz gráfica:

1. En el menú lateral izquierdo del editor de Apps Script, haz clic en el icono del **Reloj (Activadores)**.
2. Haz clic en el botón azul **+ Añadir activador** en la esquina inferior derecha.
3. **Configuración para el envío diario de reportes:**
   * *Selecciona qué función ejecutar:* `enviarReporteDesdeCelda`
   * *Selecciona qué despliegue se debe ejecutar:* `Principal`
   * *Selecciona la fuente del evento:* `Según tiempo`
   * *Selecciona el tipo de activador basado en el tiempo:* `Temporizador por días`
   * *Selecciona la hora del día:* Selecciona la ventana de **9:00 AM a 10:00 AM**.
   * Haz clic en **Guardar** y autoriza los permisos de tu cuenta en la ventana emergente de Google.
4. **Configuración para el borrado semanal de archivos:**
   * Haz clic de nuevo en **+ Añadir activador**.
   * *Selecciona qué función ejecutar:* `limpiarCarpetaSemanal`
   * *Selecciona la fuente del evento:* `Según tiempo`
   * *Selecciona el tipo de activador:* `Temporizador por semanas`
   * *Selecciona el día de la semana:* **Cada domingo**.
   * *Selecciona la hora del día:* De **11:00 PM a 12:00 AM** (Garantiza iniciar el lunes con almacenamiento limpio).
   * Haz clic en **Guardar**.


