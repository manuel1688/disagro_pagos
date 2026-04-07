import { envio_objeto,envio_archivo} from "/static/js/operaciones_dom.js";
import { InputFile } from "/static/js/input_file.js";
 
const input_categoria_1 = document.querySelector("#input_categoria_1");
const label_input_file = document.querySelector("#label_categoria_1");
const boton_subir_categoria_1 = document.querySelector("#boton_subir_categoria_1");
const boton_ver_categoria_1 = document.querySelector("#boton_ver_categoria_1");

const input_categoria_2 = document.querySelector("#input_categoria_2");
const label_input_file_2 = document.querySelector("#label_categoria_2");
const boton_subir_categoria_2 = document.querySelector("#boton_subir_categoria_2");
const boton_ver_categoria_2 = document.querySelector("#boton_ver_categoria_2");

const input_articulo = document.querySelector("#input_articulos");
const label_input_file_articulo = document.querySelector("#label_articulos");
const boton_subir_input_articulo = document.querySelector("#boton_subir_articulos");
const boton_ver_articulos = document.querySelector("#boton_ver_articulos");
const boton_limpiar_articulos = document.querySelector("#boton_limpiar_articulos");

const input_estado = document.querySelector("#input_estado");
const label_input_file_estado = document.querySelector("#label_estado");
const boton_subir_estado = document.querySelector("#boton_subir_estado");
const boton_ver_estado = document.querySelector("#boton_ver_estado");

const input_ubicacion = document.querySelector("#input_ubicacion");
const label_ubicaion = document.querySelector("#label_ubicacion");
const boton_subir_ubicacion = document.querySelector("#boton_subir_ubicacion");
const boton_ver_ubicacion = document.querySelector("#boton_ver_ubicacion");

const input_almacen = document.querySelector("#input_almacen");
const label_almacen = document.querySelector("#label_almacen");
const boton_subir_almacen = document.querySelector("#boton_subir_almacen");
const boton_ver_almacen = document.querySelector("#boton_ver_almacen");

const input_existencias = document.querySelector("#input_existencias");
const label_existencias = document.querySelector("#label_existencias");
const boton_subir_existencias = document.querySelector("#boton_input_existencias");
const boton_ver_existencias = document.querySelector("#boton_ver_existencias");
const boton_limpiar_existencias = document.querySelector("#boton_limpiar_existencias"); 


// ===================================================================================
// -----  Input file Categoria 1: primera clasificacion de las categorias  -------

const input_file_categoria_1 = new InputFile();
input_file_categoria_1.selector = input_categoria_1;
input_file_categoria_1.label_file_name = label_input_file;
input_file_categoria_1.boton_ver_datos = boton_ver_categoria_1;
input_file_categoria_1.url = `/admin/upload/categoria/1`;
input_file_categoria_1.tipo_peticion = "POST";
input_file_categoria_1.permite_campo_en_blanco = false;
input_file_categoria_1.campos_a_enviar = [input_categoria_1];
input_file_categoria_1.contenedor_resultado = document.querySelector("#contenedor_resultado_categoria_1");
input_file_categoria_1.boton_enviar = boton_subir_categoria_1;

// ===================================================================================


// ===================================================================================
// -----  Input file Categoria 2: segunda clasificacion de las categorias  -------
const input_file_categoria_2 = new InputFile();
input_file_categoria_2.selector = input_categoria_2;
input_file_categoria_2.label_file_name = label_input_file_2;
input_file_categoria_2.boton_ver_datos = boton_ver_categoria_2;
input_file_categoria_2.url = `/admin/upload/categoria/2`;
input_file_categoria_2.tipo_peticion = "POST";
input_file_categoria_2.permite_campo_en_blanco = false;
input_file_categoria_2.campos_a_enviar = [input_categoria_2];
input_file_categoria_2.contenedor_resultado = document.querySelector("#contenedor_resultado_categoria_2");
input_file_categoria_2.boton_enviar = boton_subir_categoria_2;
// ===================================================================================

// ===================================================================================
// -----  Input file Articulos:  -------
const input_file_articulos = new InputFile();
input_file_articulos.selector = input_articulo;
input_file_articulos.label_file_name = label_input_file_articulo;
input_file_articulos.boton_ver_datos = boton_ver_articulos;
input_file_articulos.tabla = "ARTICULOS";
input_file_articulos.boton_limpiar_datos = boton_limpiar_articulos;
input_file_articulos.url = `/admin/upload/articulos`;
input_file_articulos.tipo_peticion = "POST";
input_file_articulos.permite_campo_en_blanco = false;
input_file_articulos.campos_a_enviar = [input_articulo];
input_file_articulos.contenedor_resultado = document.querySelector("#contenedor_resultado_articulos");
input_file_articulos.boton_enviar = boton_subir_input_articulo;
// ===================================================================================

// ===================================================================================
// -----  Input file Estado:  -------
const input_file_estado = new InputFile();
input_file_estado.selector = input_estado;
input_file_estado.label_file_name = label_input_file_estado;
input_file_estado.boton_ver_datos = boton_ver_estado;
input_file_estado.url = `/admin/upload/estado`;
input_file_estado.tipo_peticion = "POST";
input_file_estado.permite_campo_en_blanco = false;
input_file_estado.campos_a_enviar = [input_estado];
input_file_estado.contenedor_resultado = document.querySelector("#contenedor_resultado_estado");
input_file_estado.boton_enviar = boton_subir_estado;
// ===================================================================================

// ===================================================================================
// -----  Input file Ubicacion:  -------
const input_file_ubicacion = new InputFile();
input_file_ubicacion.selector = input_ubicacion;
input_file_ubicacion.label_file_name = label_ubicaion;
input_file_ubicacion.boton_ver_datos = boton_ver_ubicacion;
input_file_ubicacion.url = `/admin/upload/ubicacion`;
input_file_ubicacion.tipo_peticion = "POST";
input_file_ubicacion.permite_campo_en_blanco = false;
input_file_ubicacion.campos_a_enviar = [input_ubicacion];
input_file_ubicacion.contenedor_resultado = document.querySelector("#contenedor_resultado_ubicacion");
input_file_ubicacion.boton_enviar = boton_subir_ubicacion;
// ===================================================================================

// ===================================================================================
// -----  Input file Almacen:  -------
const input_file_almacen = new InputFile();
input_file_almacen.selector = input_almacen;
input_file_almacen.label_file_name = label_almacen;
input_file_almacen.boton_ver_datos = boton_ver_almacen;
input_file_almacen.url = `/admin/upload/almacen`;
input_file_almacen.tipo_peticion = "POST";
input_file_almacen.permite_campo_en_blanco = false;
input_file_almacen.campos_a_enviar = [input_almacen];
input_file_almacen.contenedor_resultado = document.querySelector("#contenedor_resultado_almacen");
input_file_almacen.boton_enviar = boton_subir_almacen;
// ===================================================================================

// ===================================================================================
// -----  Input file Existencias:  -------
const input_file_existencias = new InputFile();
input_file_existencias.selector = input_existencias;
input_file_existencias.label_file_name = label_existencias;
input_file_existencias.boton_ver_datos = boton_ver_existencias;
input_file_existencias.tabla = "EXISTENCIAS";
input_file_existencias.boton_limpiar_datos = boton_limpiar_existencias;
input_file_existencias.url = `/admin/upload/existencias`;
input_file_existencias.tipo_peticion = "POST";
input_file_existencias.permite_campo_en_blanco = false;
input_file_existencias.campos_a_enviar = [input_existencias];
input_file_existencias.contenedor_resultado = document.querySelector("#contenedor_resultado_existencias");
input_file_existencias.boton_enviar = boton_subir_existencias; 
 
// ===================================================================================
