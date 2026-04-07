import {envio_objeto,evaluar_instruccion,peticion,agregar_atributos,obtener_arreglo_para_tabla} from "/static/js/operaciones_dom.js"; 

const tabla_obj = {
  _selector: null,
  _url_de_datos: null,
  _tipo_peticion: null,
  _tipo: null,
  _accion: null,
  set selector(selector){
    this._selector = selector;
  },
  set url_de_dato(url){
    this._url_de_datos = url;
  },
  set tipo_peticion(tipo){
    this._tipo_peticion = tipo;
  },
  set tipo(valor){
    this._tipo = valor;
  },
  cargar_datos: function(){
    let tabla = this._selector;
    let TIPO = this._tipo; 
    peticion(`${this._url_de_datos}`)
    .then(function(data) {
      console.log(data);
      if(data.RESPUESTA == "OK"){
        data.DATOS.forEach(async function(elemento) {
          let CODIGO = elemento['U_CODIGO'];
          console.log(CODIGO);
          delete elemento.U_CODIGO;
          let arreglo = obtener_arreglo_para_tabla(elemento);
          var row = tabla.row.add(arreglo).draw(false);
          row.nodes().to$().attr('id', CODIGO);
          row.nodes().to$().attr('class', "elemento_tabla");
          row.nodes().to$().attr('data-tabla', TIPO);
          document.querySelectorAll(".elemento_tabla").forEach(async function(e){ 
            e.onclick = function(){
              input_tabla_registro.value = e.dataset.tabla;
              input_id_transaccion.value = e.getAttribute("id");
              input_id_elemento.value = e.querySelector("td:first-child").innerHTML;
              input_descripcion_elemento.value = e.querySelector("td:nth-child(2)").innerHTML;
              document.getElementById("modal_editar").click();
            }
          });
        });
      }else if(data.RESPUESTA == "BAD"){
        alert(data.MENSAJE);
      }
    }); 
  }
}

export let tabla = (parametros) =>{
  let {SELECTOR,URL,TIPO_PETICION,ACCION,TIPO} = parametros;
  tabla_obj.selector = SELECTOR;
  tabla_obj.url_de_dato = URL;
  tabla_obj.tipo_peticion = TIPO_PETICION;
  tabla_obj.tipo = TIPO;
  return tabla_obj;
}






