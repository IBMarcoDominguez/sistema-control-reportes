// CONFIGURACIÓN GLOBAL: Tu carpeta manual de Google Drive
var ID_CARPETA_DESTINO = "Haz una carpeta en tu google drive y pega el codigo de la ruta posterior a folder/";

function doPost(e) {
  var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  try {
    // 1. Limpiamos rastros anteriores para la prueba limpia
    hoja.getRange(1, 2).setValue(""); // Limpia B1
    hoja.getRange(1, 3).setValue(""); // Limpia C1
    
    var datosRecibidos = JSON.parse(e.postData.contents);
    var mensajeDePython = datosRecibidos.mensaje;
    
    // Escribimos el texto en A1 (Se queda guardado para las 10:00 AM)
    hoja.getRange(1, 1).setValue(mensajeDePython);
    
    // 2. Procesamos el archivo forzando la validación
    if (datosRecibidos.archivo_bytes && datosRecibidos.archivo_bytes.length > 10) {
      
      var bytes = Utilities.base64Decode(datosRecibidos.archivo_bytes);
      var nombre = datosRecibidos.archivo_nombre || "adjunto_reporte.pdf";
      var blob = Utilities.newBlob(bytes, "application/octet-stream", nombre);
      
      // --- LÓGICA DE ORGANIZACIÓN POR ID ---
      var carpeta = DriveApp.getFolderById(ID_CARPETA_DESTINO);
      var archivoEnDrive = carpeta.createFile(blob);
      
      // Liberamos los accesos públicos para el enlace
      archivoEnDrive.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      
      // Estampamos de forma obligatoria el enlace en B1 (Se queda guardado para las 10:00 AM)
      hoja.getRange(1, 2).setValue(archivoEnDrive.getUrl());
      
    } else {
      hoja.getRange(1, 3).setValue("Aviso: Python no envió datos válidos de bytes del archivo.");
    }
    
    // NOTA: Se eliminó el envío de correo de aquí para que NO se mande de inmediato.
    
    return ContentService.createTextOutput(JSON.stringify({"status": "success"}))
                         .setMimeType(ContentService.MimeType.JSON);
                         
  } catch(error) {
    // ¡Si algo truena, lo estampamos de inmediato en C1 para ver qué fue!
    hoja.getRange(1, 3).setValue("Error en Drive: " + error.toString());
    return ContentService.createTextOutput(JSON.stringify({"status": "success", "debug": error.toString()}))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

// --- FUNCIÓN QUE SE EJECUTA DIARIAMENTE A LAS 10:00 AM ---
function enviarReporteDesdeCelda() {
  var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var mensajeDesdeCelda = hoja.getRange(1, 1).getValue().toString();
  var urlArchivo = hoja.getRange(1, 2).getValue().toString(); 
  
  var destinatarioPruebas = "AQUI PON EL CORREO DE TU DESTINATARIO"; 
  var asunto = "Reporte de pendientes de ingeniería Marco Antonio Domínguez González";
  
  // Si la celda está vacía, no envía nada para evitar correos basura
  if (mensajeDesdeCelda === "" || mensajeDesdeCelda === "Sin pendientes") return;
  
  var cuerpoFinal = mensajeDesdeCelda;
  if (urlArchivo !== "" && urlArchivo.startsWith("http")) {
    cuerpoFinal += "\n\n---------------------------------------------\n📎 ARCHIVO ADJUNTO RESPALDO:\n" + urlArchivo;
  }
  
  MailApp.sendEmail(destinatarioPruebas, asunto, cuerpoFinal);
}

// --- FUNCIÓN DE LIMPIEZA SEMANAL ---
function limpiarCarpetaSemanal() {
  try {
    var carpeta = DriveApp.getFolderById(ID_CARPETA_DESTINO);
    var archivos = carpeta.getFiles();
    
    while (archivos.hasNext()) {
      var archivo = archivos.next();
      archivo.setTrashed(true); 
    }
    Logger.log("Limpieza semanal completada con éxito.");
  } catch(error) {
    Logger.log("Error al intentar realizar la limpieza: " + error.toString());
  }
}



