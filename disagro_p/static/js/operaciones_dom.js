export let enlace_condicion = (codigo,descripcion,input,input_focus) => {
  let selecionar_condicion = (parametro) => input.value = parametro.dataset.valor;
  let enlace = document.createElement("a");
  enlace.classList = "dropdown-item condicion-item";
  enlace.setAttribute("data-valor",codigo);
  enlace.innerHTML = `${codigo} - ${descripcion}`
  enlace.onclick = function() {
    selecionar_condicion(this);
    input_focus.focus();
  }
  return enlace;
}

export let fila = (valor) => {
  let td = td_centrado();
  td.innerHTML = valor;
  return td;
}

export let fila_con_elemento = (valor) => {
  let td = td_centrado();
  td.appendChild(valor);
  return td;
}

let td_centrado = () => {
  let td = document.createElement("td");
  td.classList.add("centrado_vertical");
  return td;
}

export let crear_enlace_accion = (texto,href,documento) => {
  let enlace = document.createElement("a");
  enlace.classList = "dropdown-item enalce_pedido";
  enlace.setAttribute("id",documento);
  enlace.innerHTML = texto;
  enlace.href = `/${href}/${documento}`;
  return enlace;
}

export let agregar_clases = (clases,elemento) => {
  clases.forEach(async function(i) { 
    elemento.classList.add(i);
  });
}

export let remover_clases = (clases,elemento) => {
  clases.forEach(async function(i) { 
    elemento.classList.remove(i);
  });
}

export let agregar_atributos = (atributos,elemento) => {
  for (const valor in atributos) {
    elemento.setAttribute(`${valor}`,`${atributos[valor]}`);
  }
}

export let agregar_dataset = (datasets,elemento) => {
  for (const data in datasets) {
    elemento.setAttribute(`data-${data}`,`${datasets[data]}`);
  }
}
 
export let crear_elemento = (tag,clases,atributos,texto) => {
  // las clases debe tener el siguiente formato ["clase1","clase2"]
  // los atributos debe tener el siguiente formato {"atributo1":"valor1","atributo2":"valor2"}
  let elemento = document.createElement(tag);
  agregar_clases(clases,elemento);
  agregar_atributos(atributos,elemento);
  if(texto !== undefined)
  elemento.innerHTML = texto;
  return elemento
}

export let crear_item_captura = (captura) => {
  const normalizar = (valor) => (valor && valor !== '' ? valor : 'Sin dato');

  const li = crear_elemento(
    'li',
    ['list-group-item', 'd-flex', 'justify-content-between', 'align-items-center', 'list-group-item-info'],
    [],
    undefined
  );

  const contenedorTexto = document.createElement('div');
  contenedorTexto.classList.add('flex-grow-1', 'mr-3');

  const encabezadoTexto = [captura.ARTICULO, captura.DESCRIPCION]
    .filter((valor) => valor && valor !== '')
    .join(' - ') || 'Sin descripcion';

  const encabezado = crear_elemento('div', ['font-weight-bold'], [], encabezadoTexto);
  contenedorTexto.appendChild(encabezado);

  const detalle = crear_elemento(
    'div',
    ['mt-1'],
    [],
    `Ubicación: ${normalizar(captura.UBICACION)} · Almacén: ${normalizar(captura.ALMACEN)} · Lote: ${normalizar(captura.LOTE)} · Serie: ${normalizar(captura.SERIE)} · Modelo: ${normalizar(captura.MODELO)}`
  );
  detalle.style.color = '#495057'; // Color más oscuro para mejor legibilidad
  detalle.style.fontSize = '0.9rem'; // Tamaño de fuente más grande
  detalle.style.fontWeight = '500'; // Peso medio para mejor legibilidad
  contenedorTexto.appendChild(detalle);

  li.appendChild(contenedorTexto);

  const badge = crear_elemento('span', ['badge', 'badge-primary', 'badge-pill'], [], captura.CANTIDAD || '0');
  li.appendChild(badge);

  return li;
}

export let agregar_hijos = (padre,hijos) => {
  hijos.forEach(async function(h) { 
    padre.appendChild(h);
  });
}

export let limpiar_campos = (campos) => {
  campos.forEach(async function(c) { 
    c.value = "";
  });
}

export let mostrar_campo = (input) => {
  input.classList.remove("d-none");
  input.disabled = false;
  input.focus();
}

export let ocultar_campos = (inputs) => {
  inputs.forEach(async function(i) { 
    i.classList.add("d-none");
  });
}

export let mostrar_elementos = (elementos) => {
  for (var i = 0; i < elementos.length; i++){
    elementos[i].classList.remove("d-none");
  }
}

export let ocultar_elementos = (elementos) => {
  for (var i = 0; i < elementos.length; i++){
    elementos[i].classList.add("d-none");
  }
}

export async function peticion(url){
  return fetch(url,{
    method: 'GET',
    mode: 'cors', 
    cache: 'no-cache',
    credentials: 'same-origin', 
    headers:{
    'Content-Type': 'application/json'
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    }).then(function(response) {
      if (!response.ok) {
        alert("ERROR INTERNO: CONTACTAR AL ADMINISTRADOR ("+ response.status + "|"+ response.statusText +")");
      } else {
        return response.json();
      }
    })
    .catch(function(err) {
      console.log(err);
    });
}

export async function envio_objeto(objeto,url,metodo){
  return fetch(url,{
    method: metodo,
    body: objeto
    })
    .then(function (response) {
      // console.log(response);
      return response.json();
    })
    .then(function (data) {
      if (data && data.redirect) {
        window.location.href = data.redirect;
      }
      return data;
    })
    .catch(function (err) {
      // console.log(err);
      alert(err);
    });
}

export async function envio_objeto_json(objeto,url,metodo){
  return fetch(url,{
    method: metodo,
    body: objeto,
    headers:{
      'Content-Type': 'application/json'
    }
    })
    .then(function (response) {
      // console.log(response);
      return response.json();
    })
    .then(function (data) {
      if (data && data.redirect) {
        window.location.href = data.redirect;
      }
      return data;
    })
    .catch(function (err) {
      console.log(err);
      alert(err);
    });
}

export async function envio_archivo(objeto, url, metodo) {
  return fetch(url, {
    method: metodo,
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body: objeto
  })
  .then(function (response) {
      // console.log(response);
      return response.json();
  })
  .catch(function (err) {
    console.log(err);
  });
}

export let evaluar_instruccion = (codigo,valor) => {
  if((codigo === "Enter" || codigo === "NumpadEnter") && valor.length > 0)
    return true;
  return false;
}

export let evaluar_campo_blanco = (codigo) => {
  if((codigo === "Enter" || codigo === "NumpadEnter"))
    return true;
  return false;
}

export let remover_contenedor = (contenedor) => {
  if(contenedor !== null){
    contenedor.remove();
  }
}

export let agregar_opciones_datalist = (elementos,datalist) => {
  // console.log("elementos");
  // console.log(elementos);
  // console.log("datalist");
  // console.log(datalist);
  elementos.forEach(async function(e) {
    let option = document.createElement("option");
    option.classList.add("opciones");
    let {CODIGO,DESCRIPCION} = e;
    agregar_atributos({"value":CODIGO,"label":DESCRIPCION},option);
    datalist.appendChild(option);
  });
}

export let limpiar_opciones_datalist = (elementos, datalist) => {
  while (datalist.firstChild) {
    datalist.removeChild(datalist.firstChild);
  }
}

export let obtener_cuentas = (categoria_cliente) => {
  let cuentas_ls = JSON.parse(localStorage.getItem('cuentas'));
    for(var x=0;x<=cuentas_ls.length;x++){
      if(cuentas_ls[x].CATEGORIA_CLIENTE === categoria_cliente){
        return cuentas_ls[x];
      }
    }
}

export let obtener_categoria = (cliente) => {
  if(isNaN(cliente)){
    return cliente.substring(0, 1);
  }
  return cliente;
}

export let configuracion_completa = () =>{
  let codigo_tienda = localStorage.getItem('codigo_tienda');
  let codigo_caja = localStorage.getItem('codigo_caja');
  let bodega = localStorage.getItem('bodega');
  let descripcion_tienda = localStorage.getItem('descripcion_tienda');
  let descripcion_caja = localStorage.getItem('descripcion_caja');
  let centro_costo = localStorage.getItem('centro_costo');
  let lista_precio = localStorage.getItem('lista_precio');
  
  if(codigo_tienda != null && codigo_caja != null && codigo_caja != null
   && descripcion_tienda != null && descripcion_caja != null && centro_costo != null 
   && lista_precio != null){
    return true;
  }else{
    return false;
  }
}

export let obtener_arreglo_para_tabla = (objeto) => {
  let arreglo = [];
  for (const valor in objeto) {
    // console.log(`${valor}`,`${objeto[valor]}`);
    arreglo.push(objeto[valor]);
  }
  return arreglo;
}

export let arreglo_con_orden = (orden,data) => {
  let arreglo = [];
  orden.forEach(async function(e) { 
    if(data[e] == undefined || data[e] === ""){
      arreglo.push("-");
    }if(data[e] === "0E-8"){
      arreglo.push(parseFloat(data[e]));
    }else{
      arreglo.push(data[e]);
    }
  });
  return arreglo;
}

export let ocultar_loading = (btn,btn_loading) => {
  btn.classList.remove("d-none");
  btn_loading.classList.add("d-none");
}

export let cargar_datos_filtros = (data,grid_de_venta,orden_tabla) => {
  for (const valor in data.DATOS){
    let objeto = data.DATOS[valor]
    let {U_CODIGO,U_ARTICULO} = objeto;

    if(true){
      // console.log(U_ARTICULO);
      delete objeto.U_CODIGO;
    let arreglo_ordenado = arreglo_con_orden(orden_tabla,objeto);
    // console.log(arreglo_con_orden);
    
    let row = grid_de_venta.row.add(arreglo_ordenado).draw(false);
    row.nodes().to$().attr('id',U_CODIGO);
    row.nodes().to$().attr('class','fila_captura');
    document.querySelectorAll(".fila_captura").forEach(async function(e){ 
      e.onclick = function(){
        // console.log(e.getAttribute("id"));
        // console.log(e.querySelector("td:first-child"));
        input_id_transaccion.value = e.getAttribute("id");
        input_articulo_editar.value = e.querySelector("td:first-child").innerHTML;
        input_descripcion_editar.value = e.querySelector("td:nth-child(2)").innerHTML;
        document.getElementById("modal_editar").click();
      }
    });
    }
  }
}
