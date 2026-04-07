function numero_con_comas(x) {
  if(parseFloat(x) > 1000)
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return x;
}

let numero_tres_decimales = (parametro) => {
  let numero = parseFloat(parametro)
  let valor = +(Math.round(numero + "e+3")  + "e-3");
  // console.log(valor);
  return valor;
}

// Mantener compatibilidad con código antiguo
let numero_dos_decimales = numero_tres_decimales;

function numero_con_comas(x) {
  if(parseFloat(x) > 1000)
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return x; 
}

let mensaje_alerta = (selector,mensaje,mensaje_strong,url_electronica) => {
  mostrar_mensaje(selector,mensaje,mensaje_strong,'alert-danger',url_electronica);
}

let mensaje_exito = (selector,mensaje,mensaje_strong,url_electronica) => {
  mostrar_mensaje(selector,mensaje,mensaje_strong,'alert-info',url_electronica);
}

let ocultar_elemento = (selector) => document.querySelector(selector).classList.add("d-none");

let mostrar_mensaje = (selector,mensaje,mensaje_strong,clase,url_electronica) => {
  let div = document.createElement('div');
  let strong = document.createElement('strong');
  let button = document.createElement('button');
  let span = document.createElement('span');
  let span_mensaje = document.createElement('span');
  div.classList.add('alert');
  div.classList.add(clase);
  div.classList.add('alert-dismissible');
  div.classList.add('fade');
  div.classList.add('show');
  strong.innerHTML = mensaje_strong + ": ";
  span_mensaje.innerHTML = mensaje;
  button.classList.add('close');
  button.dataset.dismiss = 'alert';
  button.dataset.label = 'Close';
  span.ariaHidden = 'true'
  span.innerHTML = '&times;'
  button.appendChild(span);
  div.appendChild(strong);
  div.appendChild(span_mensaje);
  div.appendChild(button);
  contenedor = document.getElementById(selector);
  
  console.log(url_electronica);
  if(url_electronica != null){
    console.log("ENTRE");
    var a = document.createElement('a');               
    var link = document.createTextNode("Imprimir fiscal"); 
    a.appendChild(link);  
    a.title = "This is Link";  
    a.style.color = "blue";
    a.style.fontStyle = "italic";
    a.style.fontWeight = "900";
    a.style.paddingLeft = "10px";
    a.href = url_electronica;  
    div.appendChild(a);
  }
  contenedor.appendChild(div);
}