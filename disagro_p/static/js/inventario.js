 import { cargar_fecha } from "/static/js/fecha_hora.js";
import { InputTexto } from "/static/js/input_texto.js";
import { crear_item_captura } from "/static/js/operaciones_dom.js";
import { Datalist } from "./data_list.js"; 
import { setupEstadoVencidoAuto } from "./estado_vencido.js"; 

const input_articulo = document.getElementById("input_articulo");

const input_descripcion = document.getElementById("input_descripcion");
const input_fecha_de_expiracion = document.getElementById("input_fecha_expiracion");
const input_lote = document.getElementById("input_lote");
const input_almacen = document.getElementById("input_almacen");
const input_cantidad = document.getElementById("input_cantidad");
const input_ubicacion = document.getElementById("input_ubicacion");
const input_usuario = document.getElementById("input_usuario");
const input_fecha = document.getElementById("input_fecha");
const input_estado = document.getElementById("input_estado");
const input_adjunto_estado = document.getElementById("input_adjunto_estado");
const input_planificacion_activa = document.getElementById("input_planificacion_activa");
const input_planificacion_version = document.getElementById("input_planificacion_version");
const input_tipo_de_captura = document.getElementById("input_tipo_de_captura");
const input_diferencia = document.getElementById("input_diferencia");
const input_tipo_diferencia = document.getElementById("input_tipo_diferencia");
const input_observacion = document.getElementById("input_observacion");
const input_serie = document.getElementById("input_serie");
const input_modelo = document.getElementById("input_modelo");
const input_en_transito = document.getElementById("input_en_transito");
const check_input_limpiar = document.getElementById("check_input_limpiar");
const datalist_articulos = document.querySelector("#articulos");
const datalist_estados = document.querySelector("#estados");
const boton_limpiar_campos = document.getElementById("boton_limpiar_campos");
const boton_enter = document.getElementById("boton_enter");

const aplicarEstadoVencido = setupEstadoVencidoAuto({
  inputFechaExpiracion: input_fecha_de_expiracion,
  inputEstado: input_estado,
  datalistEstados: datalist_estados,
  inputFechaActual: input_fecha,
});
aplicarEstadoVencido();

input_adjunto_estado.addEventListener("change", (event) => {
  const file = input_adjunto_estado.files[0];
  if (!file) return;

  // Validar que el archivo sea una imagen y menor a 25MB
  if (!file.type.startsWith("image/") || file.size > 25 * 1024 * 1024) {
    alert("Solo se permiten imágenes de menos de 25MB.");
    input_adjunto_estado.value = "";
    // Reinicia el texto del label asociado si existe
    const label = document.querySelector("label[for='input_adjunto_estado']");
    if (label) {
      label.textContent = "Selecciona un archivo";
    }
    return;
  }

  // Truncar el nombre del archivo si es muy largo
const label = document.querySelector("label[for='input_adjunto_estado']");
if (label) {
  const maxLength = 20; // Máximo número de caracteres visibles
  const fileName = file.name;
  const fileExtension = fileName.substring(fileName.lastIndexOf('.')); // Obtener la extensión
  const baseName = fileName.substring(0, fileName.lastIndexOf('.')); // Nombre sin extensión

  let truncatedName;
  if (baseName.length > maxLength) {
    const words = baseName.split(' '); // Dividir el nombre en palabras
    const firstTwoWords = words.slice(0, 2).join(' '); // Obtener las dos primeras palabras
    truncatedName = `${firstTwoWords}...${fileExtension}`; // Combinar con puntos suspensivos y extensión
  } else {
    truncatedName = fileName; // Si no es muy largo, usar el nombre completo
  }

  label.textContent = truncatedName;
}
});

boton_enter.addEventListener('mousedown', function() {
  const focusedElement = document.activeElement; // Get the currently focused element
  if (focusedElement && focusedElement.tagName === 'INPUT') {
      console.log(`Focused input ID: ${focusedElement.id}`); // Log the ID of the focused input
      
      // Simulate a "keyup" event with the Enter key
      const enterEvent = new KeyboardEvent('keyup', {
          key: 'Enter',
          keyCode: 13, // Key code for Enter
          code: 'Enter',
          which: 13,
          bubbles: true, // Ensure the event bubbles up
          cancelable: true // Allow the event to be canceled
      });
      
      // Dispatch the event
      const eventDispatched = focusedElement.dispatchEvent(enterEvent);
      if (!eventDispatched) {
          console.log('The Enter event was canceled or not handled.');
      }
  } else {
      console.log('No input field is currently focused');
  }
});

//Estos data lista se cargan a través de la petición de los campo de articulo, ubicación y almacen
// si es a través de la petición de los campos de articulo debe validarse que ubicación y almacen estén llenos
// si es a través de la petición de los campos de ubicación y almacen debe validarse que articulo y almacen estén llenos
// si es a través de la petición de los campos de almacen y articulo debe validarse que ubicación y articulo estén llenos
const datalist_lotes = document.querySelector("#lotes");
const datalist_fechas_de_expiracion = document.querySelector("#fechas_de_expiracion");
const datalist_almacenes = document.querySelector("#almacenes");

const contenedor_estado = document.getElementById("contenedor-estado");
const lista_de_capturas = document.getElementById("lista_de_capturas");
const boton_enviar_captura = document.getElementById("boton_enviar_captura");

const etiqueta_area = document.getElementById("etiqueta_area");
const boton_enviar_captura_loading = document.getElementById("boton_enviar_captura_loading");
const datalist_bodegas = document.querySelector("#bodegas");
const datalist_areas = document.querySelector("#areas");

cargar_fecha(input_fecha);

// ===================================================================================
// ----- 1. ARTICULO: Campo_articulo y data_list_articulo: muestras artículos disponibles  -------

  let campo_articulo = new InputTexto();
  campo_articulo.selector = input_articulo;
  campo_articulo.filtros_campo = [input_articulo];
  if(input_tipo_de_captura.value === "nuevo"){
    campo_articulo.url = `/inventario/articulo/nuevo`;
  }else{
    campo_articulo.url = `/inventario/articulo`;
  }
  campo_articulo.campo_resultado = input_descripcion;
  campo_articulo.campos_siguiente = [input_ubicacion];
  campo_articulo.tipo_resultado = "CAMPO";
  campo_articulo.key_up();
  campo_articulo.accion = "MOSTRAR";
  input_articulo.focus();

  //TODO 
  
  if (input_tipo_de_captura.value !== "nuevo") {
    const data_list_articulos = new Datalist();
    data_list_articulos.selector = datalist_articulos;
    data_list_articulos.url_de_dato = `/inventario/articulos/${input_planificacion_activa.value}`;
    data_list_articulos.tipo_peticion = "GET";
    data_list_articulos.tipo = "ARTICULOS";
    data_list_articulos.accion = "MOSTRAR";
    const planId = input_planificacion_activa.value || '';
    const planVersion = input_planificacion_version ? (input_planificacion_version.value || '') : '';
    data_list_articulos.object_store = planId ? `arts_conteo_fisico_${planId}` : "arts_conteo_fisico";
    data_list_articulos.version = planVersion;
    data_list_articulos.cargar_datos_ls();
  }
  // const data_list_articulos = new Datalist();
  // data_list_articulos.selector = datalist_articulos;
  // data_list_articulos.url_de_dato = `/inventario/articulos/${input_planificacion_activa.value}`;
  // data_list_articulos.tipo_peticion = "GET";
  // data_list_articulos.tipo = "ARTICULOS";
  // data_list_articulos.accion = "MOSTRAR";
  // data_list_articulos.object_store = "arts_conteo_fisico";
  // data_list_articulos.cargar_datos_ls();


// ===================================================================================
// -----  2. UBICACION: campo_ubicacion: para agregar el lote  -----------
// TODO REVISAR EN BACKEND QUE SE USE LAS UBICACIONES PLANIFICADAS, YA QUE AL SE UN CAMPO DE 
// TEXTO PODRIA UNVENTAR UN VALOR QUE CONINDA CON EL NOMBRE DE UNA UBICACION QUE NO SEA LA PLANIFICADA
let campo_ubicacion = new InputTexto();
campo_ubicacion.selector = input_ubicacion;
campo_ubicacion.url = `/inventario/ubicacion`;
campo_ubicacion.campos_siguiente = [input_almacen];
campo_ubicacion.accion = "IGNORAR";
campo_ubicacion.key_up();

// ===================================================================================
// ----- 3. ALMACEN: campo_almacen: para agregar el lote  -----------

let campo_almacen = new InputTexto();
campo_almacen.selector = input_almacen;
campo_almacen.url = `/inventario/almacen`;
campo_almacen.tipo_resultado = "DATA_LIST";
campo_almacen.requeridos_para_datalist = [input_ubicacion,input_articulo,input_almacen];
campo_almacen.campos_datalist = [
  {campo:datalist_lotes, tipo:"DATA_LIST",codigo:"LOTES"}];

//Los campos siguientes se desactivan una vez se ingresan los datos
campo_almacen.campos_siguiente = [input_lote,input_fecha_de_expiracion,input_cantidad];
campo_almacen.accion = "MOSTRAR";
campo_almacen.contenedor_estado = contenedor_estado;
campo_almacen.key_up();


// =================================================================
// -----  4. LOTE: campo_lote: para agregar el lote  ------------------------

  let campo_lote = new InputTexto();
  campo_lote.selector = input_lote;
  campo_lote.url = `/inventario/lote`;
  campo_lote.tipo_resultado = "DATA_LIST";
  campo_lote.requeridos_para_datalist = [input_ubicacion,input_articulo,input_almacen,input_lote];
  campo_lote.campos_datalist = [
    {campo:datalist_fechas_de_expiracion, tipo:"DATA_LIST", codigo:"FECHAS_EXPIRACION"}];
  campo_lote.campos_siguiente = [input_fecha_de_expiracion];
  campo_lote.accion = "MOSTRAR";
  campo_lote.url_id = false;
  campo_lote.key_up();

// ===================================================================================
// ----- 5. FECHA_DE_EXPIRACION: campo_fecha_de_expiracion: para agregar el lote  -----------

  let campo_fecha_de_expiracion = new InputTexto();
  campo_fecha_de_expiracion.selector = input_fecha_de_expiracion;
  campo_fecha_de_expiracion.url = `/inventario/fecha_de_expiracion`;
  campo_fecha_de_expiracion.tipo_resultado = "CAMPO";
  if(input_tipo_de_captura.value === "captura"){
    campo_fecha_de_expiracion.campos_siguiente = [input_cantidad];
  }else{
    campo_fecha_de_expiracion.campos_siguiente = [input_diferencia];
  }
  campo_fecha_de_expiracion.accion = "IGNORAR";
  campo_fecha_de_expiracion.key_up();


  const data_list_estados = new Datalist();
  data_list_estados.selector = datalist_estados;
  data_list_estados.url_de_dato = `/inventario/estados`;
  data_list_estados.tipo_peticion = "GET";
  data_list_estados.tipo = "ESTADOS";
  data_list_estados.accion = "IGNORAR";
  data_list_estados.object_store = "estados_conteo_fisico";
  data_list_estados.cargar_datos_ls();

// ====================================================================================
// -----  4. LOTE: input_diferencia: para agregar las diferencias en el reconteo  -----
let campo_diferencia = new InputTexto();
campo_diferencia.selector = input_diferencia;
// campo_diferencia.url = `/inventario/ubicacion`;
campo_diferencia.campos_siguiente = [input_tipo_diferencia];
campo_diferencia.accion = "IGNORAR";
campo_diferencia.key_up();


// ===================================================================================
// --------- 6. CANTIDAD: campo_cantidad: Actvia el evento de inserción de captura  --------------

//Este campo se habilita hasta que ubicacion revise almacen

let campo_cantidad = new InputTexto();
campo_cantidad.selector = input_cantidad;
campo_cantidad.url = `/inventario/${input_tipo_de_captura.value}/${input_planificacion_activa.value}`;
campo_cantidad.tipo_de_captura = input_tipo_de_captura;
campo_cantidad.tipo_resultado = "LISTA";
campo_cantidad.lista_resultado = lista_de_capturas;
campo_cantidad.campos_siguiente = [input_articulo];
campo_cantidad.campos_a_enviar = [input_articulo,input_descripcion,input_cantidad,input_ubicacion,input_usuario,
  input_fecha,input_fecha_de_expiracion,input_lote,input_almacen,input_estado,input_adjunto_estado,input_diferencia,input_tipo_diferencia,input_serie,input_modelo,input_observacion,input_en_transito];
campo_cantidad.campos_a_limpiar = [input_articulo,input_descripcion,input_almacen,input_lote,input_fecha_de_expiracion,input_cantidad,input_estado,input_adjunto_estado,input_serie,input_modelo,input_observacion,input_en_transito];
campo_cantidad.campos_dehabilitar = [input_cantidad,input_fecha_de_expiracion,input_lote,input_almacen];
campo_cantidad.boton_enviar = boton_enviar_captura;
campo_cantidad.accion = "ENVIAR";
campo_cantidad.campos_focus = input_articulo;
campo_cantidad.datalist_lotes = datalist_lotes;
campo_cantidad.datalist_fechas_de_expiracion = datalist_fechas_de_expiracion;
campo_cantidad.campo_lote = input_lote;
campo_cantidad.campo_fecha_de_expiracion = input_fecha_de_expiracion;
campo_cantidad.key_up();
campo_cantidad.click_enviar(); 
campo_cantidad.check_input_limpiar = check_input_limpiar;
boton_limpiar_campos.addEventListener("click", (event) => {
  event.preventDefault();
  campo_cantidad.limpiar_campos();
}
);

// ===================================================================================
// -----------------------------  tipos_diferencia

let campo_tipos_diferencia = new InputTexto();
campo_tipos_diferencia.selector = input_tipo_diferencia;
campo_tipos_diferencia.url = `/inventario/${input_tipo_de_captura.value}/${input_planificacion_activa.value}`;
campo_tipos_diferencia.tipo_de_captura = input_tipo_de_captura;
campo_tipos_diferencia.tipo_resultado = "LISTA";
campo_tipos_diferencia.lista_resultado = lista_de_capturas;
campo_tipos_diferencia.campos_siguiente = [input_articulo];
campo_tipos_diferencia.campos_a_enviar = [input_articulo,input_descripcion,input_cantidad,input_ubicacion,input_usuario,
  input_fecha,input_fecha_de_expiracion,input_lote,input_almacen,input_estado,input_adjunto_estado,input_diferencia,input_tipo_diferencia,input_serie,input_modelo,input_observacion,input_en_transito];
campo_tipos_diferencia.campos_a_limpiar = [input_articulo,input_descripcion,input_almacen,input_lote,input_fecha_de_expiracion,input_cantidad,input_diferencia,input_tipo_diferencia,input_estado,input_adjunto_estado,input_serie,input_modelo,input_observacion,input_en_transito];
campo_tipos_diferencia.campos_dehabilitar = [input_cantidad,input_fecha_de_expiracion,input_lote,input_almacen];
campo_tipos_diferencia.boton_enviar = boton_enviar_captura;
campo_tipos_diferencia.accion = "ENVIAR";
campo_tipos_diferencia.campos_focus = input_articulo;
campo_tipos_diferencia.datalist_lotes = datalist_lotes;
campo_tipos_diferencia.datalist_fechas_de_expiracion = datalist_fechas_de_expiracion;
campo_tipos_diferencia.campo_lote = input_lote;
campo_tipos_diferencia.campo_fecha_de_expiracion = input_fecha_de_expiracion;
campo_tipos_diferencia.key_up();
campo_tipos_diferencia.click_enviar();
campo_tipos_diferencia.check_input_limpiar = check_input_limpiar;
boton_limpiar_campos.addEventListener("click", (event) => {
  event.preventDefault();
  campo_tipos_diferencia.limpiar_campos();
}
); 


// ===================================================================================
// -----------------------------  Últimas 10 capturas  -------------------------------

// Migración una sola vez: mover capturas antiguas a la nueva estructura
function migrar_capturas_antiguas() {
  const planificacionId = document.getElementById("input_planificacion_activa")?.value;
  if (!planificacionId) return;
  
  const oldKey = "ultimas_capturas";
  const newKey = `ultimas_capturas_${planificacionId}`;
  const flagKey = "capturas_migradas";
  
  // Solo migrar si no se ha hecho antes
  if (localStorage.getItem(flagKey)) return;
  
  // Obtener capturas antiguas
  const capturasAntiguas = localStorage.getItem(oldKey);
  if (capturasAntiguas) {
    // Si no existen capturas en la nueva key, copiar las antiguas
    if (!localStorage.getItem(newKey)) {
      localStorage.setItem(newKey, capturasAntiguas);
      console.log(`Capturas migradas a planificación ${planificacionId}`);
    }
    // Eliminar las antiguas
    localStorage.removeItem(oldKey);
  }
  
  // Marcar como migrado
  localStorage.setItem(flagKey, "true");
}

let cargar_ultimas_capturas = () => {
  // Obtener el ID de la planificación activa
  const planificacionId = document.getElementById("input_planificacion_activa")?.value;
  if (!planificacionId) {
    console.warn("No se encontró ID de planificación activa");
    return;
  }
  
  // Usar la key específica de esta planificación
  const storageKey = `ultimas_capturas_${planificacionId}`;
  let elementos_ls = localStorage.getItem(storageKey);
  
  if(elementos_ls !== null){
    JSON.parse(elementos_ls).forEach(async function(valor) { 
      const li = crear_item_captura(valor);
      lista_de_capturas.prepend(li);
    });    
  }
}

// Ejecutar migración antes de cargar
migrar_capturas_antiguas();
cargar_ultimas_capturas();

// input_cantidad.addEventListener('focus', (event) => {
//   console.log(input_area.value);
//   etiqueta_area.innerHTML = input_area.value;
// });
