import { cargar_fecha } from "/static/js/fecha_hora.js";
import { input_texto } from "/static/js/input_texto.js";
import { peticion } from "/static/js/operaciones_dom.js";
import { data_list } from "./data_list.js";

const datalist_areas = document.querySelector("#areas");
const datalist_comcodes = document.querySelector("#comcodes");
const datalist_usuarios = document.querySelector("#usuarios");
const datalist_bodegas = document.querySelector("#bodegas");

cargar_fecha(input_fecha);

idioma["emptyTable"] = "No hay elementos agregados.";
let grid_de_venta = $('#grid_venta').DataTable({
  "scrollCollapse": false,
  "paging": false,
  "responsive": true,
  "pageLength": 8,
  "language": idioma,
  dom: 'Bfrtip',
  buttons: [
      'copy', {
          extend: 'excel',
          messageTop: 'Información referente a las capturas realizadas por el usuario'
      }
  ],
  "searching": true,
  "scrollCollapse": false, 
  "drawCallback": function( settings ){
    $("#contenedor").removeClass('d-none');
    $("#cargando").addClass('d-none');
  },
  'title': 'default title',
  'select': 'multi',
  'order': [[1, 'asc']]
});

let obtener_capturas = () => {
  peticion(`/inventario/capturas`).then(function(data){
    if(data.RESPUESTA == "OK"){
      for (const valor in data.DATOS){
        let {U_ARTICULO,U_BODEGA, U_CANT_CAPTURADA, U_DESCRIPCION,U_USUARIO_CAPTURA} = data.DATOS[valor];
        grid_de_venta.row.add([U_ARTICULO,U_DESCRIPCION,U_BODEGA, U_CANT_CAPTURADA,U_USUARIO_CAPTURA,"-","-","-"]).draw(false);
      }
    }else if(data.RESPUESTA == "BAD"){
      alert(data.MENSAJE);
    }
  });
}

// let capturas = obtener_capturas();

// ===================================================================================
// -------------------  Filtro de área en reporte transaccional  ---------------------

let campo_area = input_texto({
  "SELECTOR":input_area,
  "URL":`/inventario/area`,
  "TIPO_PETICION":"GET",
  "CAMPO_SIGUIENTE": input_comcode,
  "TIPO_RESULTADO":"TABLA",
  "PERMITE_CAMPO_EN_BLANCO":true
});

let data_list_areas = data_list({
  "SELECTOR":datalist_areas,
  "URL":`/inventario/areas`,
  "TIPO_PETICION":"GET",
  "TIPO": "AREAS"
});

data_list_areas.cargar_datos();
campo_area.key_up();
campo_area.focus();


// ===================================================================================
// -------------------  Filtro de Comcode en reporte transaccional  ------------------

let campo_comcode = input_texto({
  "SELECTOR":input_comcode,
  "URL":`/inventario/comcode`,
  "TIPO_PETICION":"GET",
  "CAMPO_SIGUIENTE": input_usuario,
  "CAMPO_FOCUS":input_bodega,
  "PERMITE_CAMPO_EN_BLANCO":true
});

let data_list_comcodes = data_list({
  "SELECTOR":datalist_comcodes,
  "URL":`/inventario/comcodes`,
  "TIPO_PETICION":"GET",
  "TIPO": "BODEGAS"
});

campo_comcode.key_up();
data_list_comcodes.cargar_datos_ls('comcodes_conteo_fisico');

// ===================================================================================
// -------------------  Filtro de Usuario en reporte transaccional  ------------------

let campo_usuario = input_texto({
  "SELECTOR":input_usuario,
  "URL":`/inventario/usuario`,
  "TIPO_PETICION":"GET",
  "CAMPO_SIGUIENTE": input_bodega,
  "PERMITE_CAMPO_EN_BLANCO":true
});

let data_list_usuarios = data_list({
  "SELECTOR":datalist_usuarios,
  "URL":`/inventario/usuarios`,
  "TIPO_PETICION":"GET",
  "TIPO": "USUARIOS"
});

campo_usuario.key_up();
data_list_usuarios.cargar_datos();

// ===================================================================================
// -------------------  Filtro de Bodega en reporte transaccional  -------------------

let campo_bodega = input_texto({
  "SELECTOR":input_bodega,
  "URL":`/inventario/bodega`,
  "TIPO_PETICION":"GET",
  "CAMPO_SIGUIENTE": input_seccion,
  "PERMITE_CAMPO_EN_BLANCO":true
});

let data_list_bodegas = data_list({
  "SELECTOR":datalist_bodegas,
  "URL":`/inventario/bodegas`,
  "TIPO_PETICION":"GET",
  "TIPO": "BODEGAS"
});

campo_bodega.key_up();
data_list_bodegas.cargar_datos_ls('bodegas_conteo_fisico');

// ===================================================================================
// -------------------  Filtro de Bodega en reporte transaccional  -------------------

let campo_seccion = input_texto({
  "SELECTOR":input_seccion,
  "URL":`/inventario/filtro`,
  "TIPO_PETICION":"GET",
  "TIPO_RESULTADO":"TABLA",
  "FILTRO":true,
  "TABLA_RESULTADO":grid_de_venta,
  "CAMPOS_A_FILTRAR": [input_area,input_comcode,input_usuario,input_bodega,input_seccion],
  "PERMITE_CAMPO_EN_BLANCO":true,
  "BOTON_ENVIAR": boton_enviar_filtro,
  "BOTON_ENVIAR_LOADING": boton_enviar_filtro_loading,
  "CAMPO_FOCUS":input_seccion,
  "ORDEN_TABLA":["U_ARTICULO","U_DESCRIPCION","U_BODEGA","CLASIFICACION_1","U_CANT_CAPTURADA","U_USUARIO_CAPTURA","U_AREA","U_SECCION"]
});
 
campo_seccion.key_up();
campo_seccion.click_enviar();




