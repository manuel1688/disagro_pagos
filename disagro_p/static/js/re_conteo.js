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

const datalist_articulos = document.querySelector("#articulos");
const datalist_estados = document.querySelector("#estados");

const aplicarEstadoVencido = setupEstadoVencidoAuto({
  inputFechaExpiracion: input_fecha_de_expiracion,
  inputEstado: input_estado,
  datalistEstados: datalist_estados,
  inputFechaActual: input_fecha,
});
aplicarEstadoVencido();

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
  campo_articulo.url = `/inventario/articulo`;
  campo_articulo.campo_resultado = input_descripcion;
  // campo_articulo.requeridos_para_datalist = [input_ubicacion,input_almacen];
  //Los campos adicionales son los que cargan datalist con opciones de campos relacionados a la captura
  // campo_articulo.requridos_para_adicionales = [input_ubicacion,input_almacen];
  // campo_articulo.campo_adicional = [{campo:datalist_lotes, tipo:"DATA_LIST",codigo:"LOTES"},
  //                                   {campo:datalist_fechas_de_expiracion, tipo:"DATA_LIST", codigo:"FECHAS_EXPIRACION"},
  //                                   {campo:datalist_almacenes, tipo:"DATA_LIST", codigo:"ALMACEN"}];
  campo_articulo.campos_siguiente = [input_ubicacion];
  campo_articulo.tipo_resultado = "CAMPO";
  campo_articulo.key_up();
  campo_articulo.accion = "MOSTRAR";
  input_articulo.focus();

  const data_list_articulos = new Datalist();
  data_list_articulos.selector = datalist_articulos;
  data_list_articulos.url_de_dato = `/inventario/articulos`;
  data_list_articulos.tipo_peticion = "GET";
  data_list_articulos.tipo = "ARTICULOS";
  data_list_articulos.accion = "MOSTRAR";
  data_list_articulos.object_store = "arts_conteo_fisico";
  data_list_articulos.cargar_datos_ls();


// ===================================================================================
// -----  2. UBICACION: campo_ubicacion: para agregar el lote  -----------

let campo_ubicacion = new InputTexto();
campo_ubicacion.selector = input_ubicacion;
campo_ubicacion.url = `/inventario/ubicacion`;
campo_ubicacion.tipo_resultado = "DATA_LIST";
campo_ubicacion.requeridos_para_datalist = [input_articulo,input_ubicacion];
campo_ubicacion.campos_datalist = [{campo:datalist_almacenes, tipo:"DATA_LIST", codigo:"ALMACEN"}];
campo_ubicacion.campos_siguiente = [input_almacen];
campo_ubicacion.accion = "MOSTRAR";
campo_ubicacion.key_up();

// ===================================================================================
// ----- 3. ALMACEN: campo_almacen: para agregar el lote  -----------

let campo_almacen = new InputTexto();
campo_almacen.selector = input_almacen;
campo_almacen.url = `/inventario/almacen`;
campo_almacen.tipo_resultado = "DATA_LIST";
campo_almacen.requeridos_para_datalist = [input_ubicacion,input_articulo,input_almacen];
campo_almacen.campos_datalist = [
  {campo:datalist_lotes, tipo:"DATA_LIST",codigo:"LOTES"},
  {campo:datalist_fechas_de_expiracion, tipo:"DATA_LIST", codigo:"FECHAS_EXPIRACION"}];
campo_almacen.campos_siguiente = [input_lote,input_fecha_de_expiracion,input_cantidad];
campo_almacen.accion = "MOSTRAR";
campo_almacen.contenedor_estado = contenedor_estado;
campo_almacen.key_up();


// =================================================================
// -----  4. LOTE: campo_lote: para agregar el lote  ------------------------

  let campo_lote = new InputTexto();
  campo_lote.selector = input_lote;
  campo_lote.url = `/inventario/lote`;
  campo_lote.tipo_resultado = "CAMPO";
  campo_lote.campos_siguiente = [input_fecha_de_expiracion];
  campo_lote.accion = "IGNORAR";
  campo_lote.key_up();

// ===================================================================================
// ----- 5. FECHA_DE_EXPIRACION: campo_fecha_de_expiracion: para agregar el lote  -----------

  let campo_fecha_de_expiracion = new InputTexto();
  campo_fecha_de_expiracion.selector = input_fecha_de_expiracion;
  campo_fecha_de_expiracion.url = `/inventario/fecha_de_expiracion`;
  campo_fecha_de_expiracion.tipo_resultado = "CAMPO";
  campo_fecha_de_expiracion.campos_siguiente = [input_cantidad];
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


// ===================================================================================
// --------- 6. CANTIDAD: campo_cantidad: Actvia el evento de inserción de captura  --------------

//Este campo se habilita hasta que ubicacion revise almacen
let campo_cantidad = new InputTexto();
campo_cantidad.selector = input_cantidad;
campo_cantidad.url = `/inventario/captacion`;
campo_cantidad.tipo_resultado = "LISTA";
campo_cantidad.lista_resultado = lista_de_capturas;
campo_cantidad.campos_siguiente = [input_articulo];
campo_cantidad.campos_a_enviar = [input_articulo,input_descripcion,input_cantidad,input_ubicacion,input_usuario,
  input_fecha,input_fecha_de_expiracion,input_lote,input_almacen,input_estado,input_adjunto_estado];
campo_cantidad.campos_a_limpiar = [input_articulo,input_descripcion,input_almacen,input_lote,input_fecha_de_expiracion,input_cantidad];
campo_cantidad.campos_dehabilitar = [input_cantidad,input_fecha_de_expiracion,input_lote,input_almacen];
// campo_cantidad.es_nuevo = [{input_lote, datalist_lotes},{input_fecha_de_expiracion, datalist_fechas_de_expiracion}];
campo_cantidad.boton_enviar = boton_enviar_captura;
campo_cantidad.accion = "ENVIAR";
campo_cantidad.campos_focus = input_articulo;
campo_cantidad.key_up();
campo_cantidad.click_enviar(); 


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

