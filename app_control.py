# IBMarcoDominguez
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import requests
import os
import base64

# -----------------------------------------------------------------------------
# CONFIGURACIÓN: Tu URL de la aplicación web de Google
# -----------------------------------------------------------------------------
URL_APPLICACION_WEB = "https://script.google.com/macros/s/AKfycbySzN7McjEIfJJ_z-ftTpi3c9g9zmXula71oFzgcqMowA92scgd9oZPNeu3QWCVsfXzvQ/exec"

# CONFIGURACIÓN LOCAL: Nombre del archivo de respaldo de texto
ARCHIVO_RESPALDO_LOCAL = "ultimo_reporte.txt"

# LÍMITE DE PESO: 10 MB en bytes (10 * 1024 * 1024)
LIMITE_PESO_BYTES = 10485760

estado_editable = True
texto_respaldo = ""
ruta_archivo_adjunto = ""

# -----------------------------------------------------------------------------
# FUNCIONES DE MEMORIA LOCAL (.TXT)
# -----------------------------------------------------------------------------
def cargar_ultimo_reporte_local():
    """Busca el archivo TXT local. Si existe, carga su contenido en el recuadro."""
    if os.path.exists(ARCHIVO_RESPALDO_LOCAL):
        try:
            with open(ARCHIVO_RESPALDO_LOCAL, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
            if contenido:
                texto_reporte.delete("1.0", tk.END)
                texto_reporte.insert("1.0", contenido)
                texto_reporte.config(fg="#ffffff") # Forzamos color de texto activo
        except Exception as e:
            print(f"No se pudo leer el archivo de respaldo local: {e}")

def guardar_reporte_local(nuevo_texto):
    """Borra el contenido del TXT anterior y escribe el nuevo reporte."""
    try:
        with open(ARCHIVO_RESPALDO_LOCAL, "w", encoding="utf-8") as f:
            f.write(nuevo_texto)
    except Exception as e:
        print(f"No se pudo guardar el archivo de respaldo local: {e}")


# -----------------------------------------------------------------------------
# FUNCIONES DE LA INTERFAZ
# -----------------------------------------------------------------------------
def alternar_estado():
    global estado_editable, texto_respaldo, ruta_archivo_adjunto
    if estado_editable:
        estado_editable = False
        texto_respaldo = texto_reporte.get("1.0", tk.END).strip()
        texto_reporte.config(state=tk.NORMAL)
        texto_reporte.delete("1.0", tk.END)
        texto_reporte.insert("1.0", "Sin pendientes")
        texto_reporte.config(state=tk.DISABLED, bg="#402020")
        ruta_archivo_adjunto = ""
        etiqueta_archivo.config(text="Ningún archivo seleccionado", fg="#888888")
        boton_adjuntar.config(state=tk.DISABLED)
        boton_switch.config(text="🔴 SIN PENDIENTES (BLOQUEADO)", bg="#d9534f")
    else:
        estado_editable = True
        texto_reporte.config(state=tk.NORMAL, bg="#2d2d2d")
        texto_reporte.delete("1.0", tk.END)
        if texto_respaldo and texto_respaldo != "Sin pendientes":
            texto_reporte.insert("1.0", texto_respaldo)
        else:
            # Si no hay respaldo en memoria de ejecución, intenta jalar del TXT de nuevo
            if os.path.exists(ARCHIVO_RESPALDO_LOCAL):
                cargar_ultimo_reporte_local()
            else:
                texto_reporte.insert("1.0", "Escribe tus pendientes aquí organizados por líneas...")
        boton_adjuntar.config(state=tk.NORMAL)
        boton_switch.config(text="🟢 PERMITIR EDICIÓN", bg="#5cb85c")

def seleccionar_archivo():
    """Abre el explorador de archivos y valida que no supere el límite de peso."""
    global ruta_archivo_adjunto
    tipos_archivos = [
        ('Archivos de Oficina', '*.pdf *.docx *.xlsx *.xls *.doc'),
        ('Todos los archivos', '*.*')
    ]
    
    ruta = filedialog.askopenfilename(title="Seleccionar documento adjunto", filetypes=tipos_archivos)
    
    if ruta:
        peso_archivo = os.path.getsize(ruta)
        if peso_archivo > LIMITE_PESO_BYTES:
            peso_en_mb = peso_archivo / (1024 * 1024)
            messagebox.showerror(
                "Archivo muy pesado", 
                f"Sabes que no puedes subir este archivo.\n\n"
                f"El archivo pesa {peso_en_mb:.2f} MB, y el límite permitido por seguridad es de 10.00 MB."
            )
            return
            
        ruta_archivo_adjunto = ruta
        nombre_archivo = os.path.basename(ruta)
        etiqueta_archivo.config(text=f"📎 Adjunto: {nombre_archivo}", fg="#5cb85c")

def enviar_reporte():
    global ruta_archivo_adjunto
    estado_actual = texto_reporte.cget("state")
    texto_reporte.config(state=tk.NORMAL)
    nuevo_mensaje = texto_reporte.get("1.0", tk.END).strip()
    texto_reporte.config(state=estado_actual)
    
    if not nuevo_mensaje or nuevo_mensaje == "Escribe tus pendientes aquí organizados por líneas...":
        messagebox.showwarning("Campo vacío", "Por favor, escribe el reporte antes de actualizar.")
        return
    
    boton_actualizar.config(state=tk.DISABLED, text="Subiendo datos y archivo...")
    ventana.update()
    
    payload = {
        "mensaje": nuevo_mensaje,
        "archivo_bytes": "",
        "archivo_nombre": ""
    }
    
    if ruta_archivo_adjunto and os.path.exists(ruta_archivo_adjunto):
        try:
            with open(ruta_archivo_adjunto, "rb") as f:
                bytes_archivo = f.read()
                payload["archivo_bytes"] = base64.b64encode(bytes_archivo).decode('utf-8')
                payload["archivo_nombre"] = os.path.basename(ruta_archivo_adjunto)
        except Exception as e:
            messagebox.showerror("Error de Archivo", f"No se pudo procesar el archivo local:\n{e}")
            boton_actualizar.config(state=tk.NORMAL, text="Actualizar Reporte en la Nube")
            return

    try:
        respuesta = requests.post(URL_APPLICACION_WEB, json=payload, timeout=20)
        if respuesta.status_code == 200:
            # --- CAMBIO AQUÍ: GUARDAR EN TXT LOCAL TRAS ÉXITO EN LA NUBE ---
            guardar_reporte_local(nuevo_mensaje)
            
            messagebox.showinfo("¡Éxito!", "El estatus ha sido actualizado en la nube y guardado localmente.")
            ruta_archivo_adjunto = ""
            etiqueta_archivo.config(text="Ningún archivo seleccionado", fg="#888888")
        else:
            messagebox.showerror("Error", f"El servidor respondió con código: {respuesta.status_code}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar con la nube:\n{e}")
    finally:
        boton_actualizar.config(state=tk.NORMAL, text="Actualizar Reporte en la Nube")

def limpiar_marcador(event):
    if estado_editable and texto_reporte.get("1.0", tk.END).strip() == "Escribe tus pendientes aquí organizados por líneas...":
        texto_reporte.delete("1.0", tk.END)

# -----------------------------------------------------------------------------
# INTERFAZ GRÁFICA
# -----------------------------------------------------------------------------
ventana = tk.Tk()
ventana.title("Panel de Control - Reportes de Ingeniería")
ventana.geometry("600x640")
ventana.configure(bg="#1e1e1e")

etiqueta_titulo = tk.Label(ventana, text="CONTROL REMOTO DE REPORTES DIARIOS", font=("Arial", 12, "bold"), bg="#1e1e1e", fg="#ffffff")
etiqueta_titulo.pack(pady=15)

boton_switch = tk.Button(ventana, text="🟢 PERMITIR EDICIÓN", font=("Arial", 10, "bold"), bg="#5cb85c", fg="#ffffff", bd=0, padx=20, pady=6, command=alternar_estado)
boton_switch.pack(pady=5)

texto_reporte = tk.Text(ventana, wrap=tk.WORD, width=65, height=14, font=("Arial", 11), bg="#2d2d2d", fg="#ffffff", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#444444")
texto_reporte.pack(pady=10)
texto_reporte.insert("1.0", "Escribe tus pendientes aquí organizados por líneas...")
texto_reporte.bind("<Button-1>", limpiar_marcador)

# --- EJECUCIÓN INICIAL: Cargar memoria si existe el archivo TXT ---
cargar_ultimo_reporte_local()

boton_adjuntar = tk.Button(ventana, text="📁 Adjuntar Archivo (PDF, Word, Excel)", font=("Arial", 10, "bold"), bg="#2c3e50", fg="#ffffff", bd=0, padx=15, pady=6, command=seleccionar_archivo)
boton_adjuntar.pack(pady=5)

etiqueta_archivo = tk.Label(ventana, text="Ningún archivo seleccionado", font=("Arial", 9, "italic"), bg="#1e1e1e", fg="#888888")
etiqueta_archivo.pack(pady=2)

boton_actualizar = tk.Button(ventana, text="Actualizar Reporte en la Nube", font=("Arial", 11, "bold"), bg="#007acc", fg="#ffffff", bd=0, padx=15, pady=10, command=enviar_reporte)
boton_actualizar.pack(pady=15)

ventana.mainloop()


