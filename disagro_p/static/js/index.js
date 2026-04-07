
import {configuracion_completa} from "/static/js/operaciones_dom.js";
const londing = document.getElementById("cargando");
const cerrar_sesion = document.getElementById("cerrar_sesion");

let ocultar_londing = () =>{
  londing.classList.add("d-none");
}

if(cerrar_sesion  !== null){ 
  cerrar_sesion.onclick = function(){ 
    // Limpiar todas las claves definidas en localStorage
    for (let i = 0; i < localStorage.length; i++) {
      let key = localStorage.key(i);
      localStorage.removeItem(key);
    }

    if (localStorage.length === 0) {
      console.log("El localStorage está vacío");
    } else {
      console.log("El localStorage no está vacío");
    }
    alert("Sesión cerrada");
    window.location.replace("/auth/logout");
  }
}

if(!configuracion_completa()){
  let elementos = document.getElementsByClassName("opcion_usuario"); 
  for(var i = 0; i < elementos.length; i++){
    elementos[i].classList.add("d-none");
  }
}else{

  let enlace_re_imprimir_factura = document.getElementById("enlace_re_imprimir_factura");
  if(enlace_re_imprimir_factura != null){
    enlace_re_imprimir_factura.href = `/factura/${localStorage.getItem("lista_precio")}/re_imprimir`;
  }

  let boton_cierre_de_caja = document.getElementById("boton_cierre_de_caja");
  if(boton_cierre_de_caja != null){
    boton_cierre_de_caja.href = `/caja/cierre_de_caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("codigo_caja")}`;
  }
  
  let boton_reportes_cierre = document.getElementById("boton_reportes_cierre");
  if(boton_reportes_cierre != null){
    boton_reportes_cierre.href = `/caja/reportes/${localStorage.getItem("lista_precio")}/${localStorage.getItem("codigo_caja")}`;
  }

  let enalce_nuevo_pedido = document.getElementById("enalce_nuevo_pedido");
  if(enalce_nuevo_pedido != null){
    enalce_nuevo_pedido.href = `/pedido/${localStorage.getItem('lista_precio')}/nuevo`;
  }

  let enlace_caja = document.getElementById("enlace_caja");
  if(enlace_caja != null){
    enlace_caja.href = `/caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/${localStorage.getItem("codigo_caja")}/pedidos`;
  }

  let ver_desglose = document.getElementById("ver_desgloses");
  if(ver_desglose != null){
  ver_desglose.href = `/caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/${localStorage.getItem("codigo_caja")}/desgloses`;
  }

  let ver_pedidos = document.getElementById("ver_pedidos");
  if(ver_pedidos != null){
  ver_pedidos.href = `/caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/${localStorage.getItem("codigo_caja")}/pedidos`;
  }

  let ver_notas_de_credito = document.getElementById("ver_notas_de_credito");
  if(ver_notas_de_credito != null){
    ver_notas_de_credito.href = `/caja/${localStorage.getItem("lista_precio")}/notas_de_credito`;
  }

  let cierre_caja = document.getElementById("enlace_cierre_caja");
  if(cierre_caja != null){
    cierre_caja.href = `/caja/cierre/${localStorage.getItem("lista_precio")}/${localStorage.getItem("codigo_caja")}`;
  } 
  
  let boton_cargar_pedidos = document.getElementById("boton_cargar_pedidos");
  if(boton_cargar_pedidos != null){
    boton_cargar_pedidos.href = `/caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/${localStorage.getItem("codigo_caja")}/pedidos`;
  } 

  let boton_cargar_pendientes = document.getElementById("boton_cargar_pendientes");
  if(boton_cargar_pendientes != null){
    boton_cargar_pendientes.href = `/despacho/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/facturas`;
  }
  
  let boton_despacho = document.getElementById("enlace_despacho");
  if(boton_despacho != null){
    boton_despacho.href = `/despacho/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/facturas`;
  }

  let boton_limpiar_nota_de_credito = document.getElementById("boton_limpiar_nota_de_credito");
  if(boton_limpiar_nota_de_credito != null){
    boton_limpiar_nota_de_credito.href = `/cxc/${localStorage.getItem("lista_precio")}/nota/credito/fiscal`;
  }
  
  let enlace_nota_fiscal = document.getElementById("enlace_nota_fiscal");
  if(enlace_nota_fiscal != null){
    enlace_nota_fiscal.href = `/cxc/${localStorage.getItem("lista_precio")}/nota/credito/fiscal`;
  }

  let enalce_reporte_mayor = document.getElementById("enalce_reporte_mayor");
  console.log(enalce_reporte_mayor);
  if(enalce_reporte_mayor != null){
    enalce_reporte_mayor.href = `/finanza/estado/resultado`;
  }


  if(configuracion_completa()){
    let ver_desglose = document.getElementById("ver_desgloses");
    if(ver_desglose != null){
      ver_desglose.href = `/caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/${localStorage.getItem("codigo_caja")}/desgloses`;
    }
    let ver_pedidos = document.getElementById("ver_pedidos");
    if(ver_pedidos != null){
      ver_pedidos.href = `/caja/${localStorage.getItem("lista_precio")}/${localStorage.getItem("bodega")}/${localStorage.getItem("codigo_caja")}/pedidos`;
    }
    let enlace_buscador_factura = document.getElementById("enlace_buscador_factura");
    if(enlace_buscador_factura != null){
      enlace_buscador_factura.href = `/factura/${localStorage.getItem("lista_precio")}/buscador`;
    }
    let formulario_buscador_factura = document.getElementById("formulario_buscador_factura");
    if(formulario_buscador_factura != null){
      formulario_buscador_factura.action = `/factura/${localStorage.getItem("lista_precio")}/filtro`;
    }
  }
}

ocultar_londing();