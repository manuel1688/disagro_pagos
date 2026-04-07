
import { configuracion_completa,peticion } from "/static/js/operaciones_dom.js";

const londing = document.getElementById("cargando");
const pie_de_pagina = document.getElementById("pie_de_pagina");

let ocultar_londing = () =>{
  londing.classList.add("d-none");
}

if(!configuracion_completa()){

  let elementos = document.getElementsByClassName("elemento_inicio"); 
  for(var i = 0; i < elementos.length; i++){
    elementos[i].classList.add("d-none");
  }
}

if(configuracion_completa()){

  let enlace_nuevo_predido_inicio = document.getElementById("enlace_nuevo_predido_inicio");
  if(enlace_nuevo_predido_inicio != null){
    document.getElementById("enlace_nuevo_predido_inicio").href = `/pedido/${localStorage.getItem('lista_precio')}/nuevo`;
  }
}

let vendedor_a_memoria =  () => {
  let vendedor_ls = localStorage.getItem('vendedor');
  if(vendedor_ls === null){
    peticion(`/admin/vendedor`)
    .then(function(data) {
      if(data.RESPUESTA == "OK" && data.ES_VENDEDOR == "SI"){
        let vendedor = data.VENDEDOR.VENDEDOR;
        let nombre_vendedor = data.VENDEDOR.NOMBRE;
        localStorage.setItem('vendedor',vendedor);
        localStorage.setItem('nombre_vendedor',nombre_vendedor);
        pie_de_pagina.innerHTML = `Vendedor: ${vendedor} | ${nombre_vendedor}`;
      }else if(data.RESPUESTA == "BAD"){
        alert(data.MENSAJE);
      }
    }); 
  }else if(vendedor_ls !== null){
    pie_de_pagina.innerHTML = `Vendedor: ${localStorage.getItem("vendedor")} | ${localStorage.getItem("nombre_vendedor")}`;
  }
}

let cajero_a_memoria =  () => {
  let cobrador_ls = localStorage.getItem('cobrador');
  if(cobrador_ls === null){
    peticion(`/admin/cajero`)
    .then(function(data) {
      if(data.RESPUESTA == "OK" && data.ES_CAJERO == "SI"){
        let cobrador = data.CAJERO.COBRADOR;
        let nombre_cobrador = data.CAJERO.NOMBRE;
        localStorage.setItem('cobrador',cobrador);
        localStorage.setItem('nombre_cobrador',nombre_cobrador);
        pie_de_pagina.innerHTML = `Cobrador: ${cobrador} | ${nombre_cobrador}`;
      }else if(data.RESPUESTA == "BAD"){
        alert(data.MENSAJE);
      }
    }); 
  }else if(cobrador_ls !== null){
    pie_de_pagina.innerHTML = `Cobrador: ${localStorage.getItem("cobrador")} | ${localStorage.getItem("nombre_cobrador")}`;
  }
}

// vendedor_a_memoria();
// cajero_a_memoria(); 
// ocultar_londing();
