import { envio_objeto,envio_archivo} from "/static/js/operaciones_dom.js";
import { InputFile } from "/static/js/input_file.js";
 

const input_existencias = document.querySelector("#input_existencias");
const label_existencias = document.querySelector("#label_existencias");
const boton_subir_existencias = document.querySelector("#boton_input_existencias");
const boton_ver_existencias = document.querySelector("#boton_ver_existencias");
const boton_limpiar_existencias = document.querySelector("#boton_limpiar_existencias"); 

// ===================================================================================
// -----  Input file Existencias:  -------
const input_file_existencias = new InputFile();
input_file_existencias.selector = input_existencias;
input_file_existencias.label_file_name = label_existencias;
input_file_existencias.boton_ver_datos = boton_ver_existencias;
input_file_existencias.tabla = "EXISTENCIAS";
input_file_existencias.boton_limpiar_datos = boton_limpiar_existencias;
input_file_existencias.url = `/planificacion/upload/existencias`;
input_file_existencias.tipo_peticion = "POST";
input_file_existencias.permite_campo_en_blanco = false;
input_file_existencias.campos_a_enviar = [input_existencias];
input_file_existencias.contenedor_resultado = document.querySelector("#contenedor_resultado_existencias");
input_file_existencias.boton_enviar = boton_subir_existencias; 
input_file_existencias.redirigir = true;
input_file_existencias.url_redireccion = "/planificacion/planificar";
 
// ===================================================================================
