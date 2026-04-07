import { envio_objeto_json, evaluar_campo_blanco,envio_objeto,evaluar_instruccion,peticion,crear_item_captura,obtener_arreglo_para_tabla,cargar_datos_filtros,ocultar_loading,agregar_opciones_datalist,limpiar_opciones_datalist} from "/static/js/operaciones_dom.js";
import { getTimezoneForRequest } from "/static/js/timezone_utils.js"; 

class InputTexto {

  constructor(){
    this._selector = null;
    this._url = null;
    this._tipo = null;
    this._accion = null;
    this._campo_resultado = null;
    this._campos_siguiente = null;
    this._campos_a_enviar = null;
    this._campo_focus = null;
    this._lista_resultado = null;
    this._tabla_resultado = null;
    this._tipo_resultado = null; 
    this._boton_enviar = null;
    this._boton_enviar_loading = null;
    this._filtro = null;
    this._permite_campo_en_blanco = null;
    this._campos_datalist = null;
    this._requeridos_para_datalist = null;
    this._tipo_de_campo = null;
    this._contenedor_estado = null;
    this._filtros_campo = null;
    this._campos_a_limpiar = null;
    this._campos_dehabilitar = null;
    this._datalist_lotes = null;
    this._datalist_fechas_de_expiracion  = null;
    this._campo_lote = null;
    this._campo_fecha_de_expiracion = null;
    this._url_id = true;
    this._tipo_de_captura = null;
    this._check_input_limpiar = null;
    // datalist_lotes 
    // datalist_fechas_de_expiracion 
    // this._es_nuevo = null;
  }

  set selector(selector){
    this._selector = selector;
  }

  set url(url){
    this._url = url;
  }

  set tipo(valor){
    this._tipo = valor;
  }

  set accion(accion){
    this._accion = accion;
  }

  set campo_resultado(campo){
    this._campo_resultado = campo;
  }

  set campos_datalist(campos){
    this._campos_datalist = campos;
  }

  set requeridos_para_datalist(campos){
    this._requeridos_para_datalist = campos;
  }

  set contenedor_estado(contenedor){
    this._contenedor_estado = contenedor;
  }

  set campos_siguiente(campo){
    this._campos_siguiente = campo;
  }

  set campos_a_enviar(campos){
    this._campos_a_enviar = campos;
  }

  set campos_focus(campo){
    this._campo_focus = campo;
  }

  set lista_resultado(lista){
    this._lista_resultado = lista;
  }

  set tabla_resultado(tabla){
    this._tabla_resultado = tabla;
  }

  set tipo_resultado(tipo){
    this._tipo_resultado = tipo;
  }

  set boton_enviar(boton){
    this._boton_enviar = boton;
  }

  set filtro(param){
    this._filtro = param;
  }

  set campos_a_filtrar(campos){
    this._campos_a_filtrar = campos;
  }

  set permite_campo_en_blanco(valor){
    this._permite_campo_en_blanco = valor;
  }

  set orden_tabla(valor){
    this._orden_tabla = valor;
  }

  set boton_enviar_loading(boton){
    this._boton_enviar_loading = boton;
  }

  set filtros_campo(campos){
    this._filtros_campo = campos;
  }

  set campos_a_limpiar(campos){
    this._campos_a_limpiar = campos;
  }

  set campos_dehabilitar(campos){
    this._campos_dehabilitar = campos;
  }

  set datalist_lotes(valor){
    this._datalist_lotes = valor;
  }

  set datalist_fechas_de_expiracion(valor){
    this._datalist_fechas_de_expiracion = valor;
  }

  set campo_lote(valor){
    this._campo_lote = valor;
  }

  set campo_fecha_de_expiracion(valor){
    this._campo_fecha_de_expiracion = valor;
  }

  set url_id(valor){
    this._url_id = valor;
  }

  set tipo_de_captura(valor){
    this._tipo_de_captura = valor;
  }

  set check_input_limpiar(valor){
    this._check_input_limpiar = valor;
  }
  // set es_nuevo(campos){
  //   this._es_nuevo = campos;
  // }
  
  mostar_ultimo_valor(){
    let local_storage = localStorage.getItem(this._input.dataset.ultimo_valor);
    if(local_storage !== null){
      this._input.value = local_storage;
    }
  }
  
  key_up(){
    if(this._selector)
    {
      this._selector.addEventListener("keyup", (e) => {
        let target = e.target;
        let valor = target.value;
        if(evaluar_campo_blanco(e.code)){

          if(valor.length<=0 && this._campos_siguiente !== undefined && this._accion === ""){
            parametros["campos_siguiente"].focus();
            return;
          }
          // Se debe cargar la lista de los lotes asociados al articulo 
          // y las fecha de vencimiento asociadas al articulo
          // La descripcion la obtengo del local storage
          this.operacion_segun_tipo();
        }
      });
    }
  } 

  click_enviar(){
    let permite_campo_en_blanco = this._permite_campo_en_blanco;
    let campo = this._selector;
    this._boton_enviar.addEventListener("click", () => {
      if(!permite_campo_en_blanco && campo.value.length == 0){
       return;
      }
      this.operacion_segun_tipo();
    });
  }

  operacion_segun_tipo(){
    this._campos_siguiente.forEach((campo, index) => {
      console.log(`Campo ${index}:`, campo);
    });
    if(this._accion === "MOSTRAR")
    {
      
      if(this._contenedor_estado !== null){
        const almacen = this._selector.value;
        if (almacen.endsWith("3")) {
          this._contenedor_estado.classList.remove("d-none");
          if (this._campos_siguiente.length > 0) {
            this._campos_siguiente[0].focus();
          }
        }else{
          if (this._campos_siguiente.length > 0) {
            this._campos_siguiente[0].focus();
          }
          console.log("Do nothing..");
        }
      }
      this.obtener_dato();
    }else if(this._accion === "ENVIAR")
    {
      if(this.validar_json_atributos() === false)
      {
        return;
      }
      else
      {
        this.envio_de_datos();
      }
    }else{
      console.log("No se ha definido una accion valida");
      if (this._campos_siguiente.length > 0) {
        this._campos_siguiente.forEach(campo => {
          campo.disabled = false;
        });

        // Add a small delay before applying focus
        setTimeout(() => {
          this._campos_siguiente[0].focus();
        }, 0);
      }
      console.log("Do nothing..");
    }
  }

  obtener_dato(){
    this._selector.blur();
    const data = {};
    if (this._tipo_resultado === "CAMPO") {
      const filtro = {};
      this._filtros_campo.forEach(input => {
      filtro[input.dataset.nombre] = input.value;
      });
      data["FILTRO"] = filtro;
    }
    if (this._tipo_resultado === "DATA_LIST") {
      const filtro = {};
      this._requeridos_para_datalist.forEach(input => {
      filtro[input.dataset.nombre] = input.value;
      });
      data["FILTRO"] = filtro;
    }
    
    // if (this._requeridos_para_datalist) {
    //   this._requeridos_para_datalist.forEach(campo => {
    //     data[campo.dataset.nombre] = campo.value;
    //   });
    // }
    const body = JSON.stringify(data);
    let url = '';
    if (this._url_id) {
      url = `${this._url}/${this._selector.value}`;
    } else {
      url = this._url;
    }
    envio_objeto_json(body,url,"POST").then((data) => {
      if (!data.error){
        // VERIRIFICAR LOS CAMPOS REQUERIDOS ADICIONALES
        if (this._campos_siguiente.length > 0) {
          this._campos_siguiente.forEach(campo => {
            campo.disabled = false;
          });
        }
        if(this._campos_siguiente !== undefined && this._tipo_resultado == "CAMPO"){
          this._campo_resultado.value = data.mensaje["DESCRIPCION"];
        }

        if(this._tipo_resultado === "DATA_LIST"){
          this.cargar_campos_datalist(data);
        }

        if (this._campos_siguiente.length > 0) {
          this._campos_siguiente[0].focus();
        }
      } else {
        alert(`ERROR: ${data.mensaje}`);
      }
    });
  }

  cargar_campos_datalist(data){
    if(this._campos_datalist){

      for (let i = 0; i < this._campos_datalist.length; i++) {
        if (this._campos_datalist[i].tipo === "DATA_LIST") {
          limpiar_opciones_datalist(data.mensaje[this._campos_datalist[i].codigo],this._campos_datalist[i].campo);
        }
      }

      for (let i = 0; i < this._campos_datalist.length; i++) {
        if (this._campos_datalist[i].tipo === "DATA_LIST") {
          agregar_opciones_datalist(data.mensaje[this._campos_datalist[i].codigo],this._campos_datalist[i].campo);
        }
      }
    }
  }

  validar_json_atributos(){
    const elementos = this._campos_a_enviar;
    for (var i = 0; i < elementos.length; i++){
      if(elementos[i].dataset.requerido === "true" && elementos[i].value.length === 0){
        elementos[i].classList.add('is-invalid');
        elementos[i].focus();
        return false;
      }
    }
    return true;
  }

  envio_de_datos(){
    this._selector.blur();
    this._boton_enviar.disabled = true;
    this._boton_enviar.innerHTML = 'Enviando ... <span class="spinner-border"></span>';
    
    let json = this.obtener_json_atributos();
    
    // Agregar zona horaria del navegador del usuario
    json.TIMEZONE = getTimezoneForRequest();
    
    // Crear un nuevo FormData
    const formData = new FormData();
    
    // Agregar el archivo al FormData
    const fileInput = document.getElementById('input_adjunto_estado');
    const file = fileInput.files[0];
    formData.append('file', file);

    // Agregar los datos JSON al FormData
    formData.append('json', JSON.stringify(json));

    envio_objeto(formData,`${this._url}`,"POST").then( (data) => {

      if (!data.error) {
        if(this._tipo_resultado === "LISTA"){
          const li = crear_item_captura(data.OBJETO);
          this._lista_resultado.prepend(li);
          this.actualizar_ult_capturas(data.OBJETO);

        } else if(this._tipo_resultado === "TABLA"){

          let CODIGO = data.OBJETO['U_CODIGO'];
          delete data.OBJETO.U_CODIGO;
          var row = tabla_resultado.row.add(obtener_arreglo_para_tabla(data.OBJETO)).draw(false);
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
        }
        
        const elementosParaOcultar = document.querySelectorAll('.para-ocultar');
        elementosParaOcultar.forEach(elemento => {
          elemento.classList.add('d-none');
        });

        this.actualizar_campos_historico();
        
        if (this._check_input_limpiar.checked) {
          // Limpieza normal de todos los campos definidos
          this.limpiar_campos();
          this.deshabilitar_campos();
          this._campo_focus.focus();
        } else {
          // Solo se limpia y deshabilita el campo principal
          this._selector.value = '';
        }

        
        // ocultar_loading(btn_enviar,btn_enviar_loading);
        
        this._boton_enviar.innerHTML = `Enviar`;
        this._boton_enviar.disabled = false;
        // alert(data.mensaje);
      } else {
        alert(`ERROR: ${data.mensaje}`);
        this._boton_enviar.innerHTML = `Enviar`;
        this._boton_enviar.disabled = false;
        this.ocultar_loading();
        // this._boton_enviar.innerHTML = `${texto_boton} <span class="fa fa-upload"></span>`;
        // this._boton_enviar.disabled = false;
      }
    }).catch( (err) => {
      console.log(err);
      this._boton_enviar.innerHTML = `Enviar`;
      this._boton_enviar.disabled = false;
      this.ocultar_loading();
    });
  }

  ocultar_loading(){
    console.log("ocultar_loading");
    return;
  }

  obtener_json_atributos(){
    let DATOS = {};
    const elementos = this._campos_a_enviar;
    for (var i = 0; i < elementos.length; i++){
      const nombre = elementos[i].dataset.nombre;
      if (!nombre) {
        continue;
      }

      if (elementos[i].type === 'checkbox') {
        DATOS[nombre] = elementos[i].checked;
        elementos[i].classList.remove('is-invalid');
        continue;
      }

      if(elementos[i].dataset.requerido === "false" && elementos[i].value.length === 0){
        DATOS[nombre] =  `${elementos[i].value}`;
      }else if(elementos[i].value.length > 0){
        DATOS[nombre] =  `${elementos[i].value}`;
        elementos[i].classList.remove('is-invalid');
      }
    }

    if (Object.prototype.hasOwnProperty.call(DATOS, 'TIPO_DIFERENCIA')) {
      const diferencia = DATOS['TIPO_DIFERENCIA'];
      if (typeof diferencia === 'string' && diferencia.length > 0) {
        const normalizado = diferencia.trim().toUpperCase();
        const mapaDiferencias = {
          SOBRANTE: 'POSITIVA',
          FALTANTE: 'NEGATIVA',
        };
        if (mapaDiferencias[normalizado]) {
          DATOS['TIPO_DIFERENCIA'] = mapaDiferencias[normalizado];
        } else if (normalizado === 'POSITIVA' || normalizado === 'NEGATIVA') {
          DATOS['TIPO_DIFERENCIA'] = normalizado;
        }
      }
    }
    return DATOS;
  }

  agregar_informacion_adicional(datos){

    datos['LOTE_NUEVO'] = false;
    datos['FECHA_DE_VENCIMIENTO_NUEVO'] = false;
    if (this._datalist_lotes && this._datalist_lotes.getElementsByTagName('option').length > 0) {
      console.log("Esta vacio el lote");
    }else{
      console.log("No esta vacio el lote");
    }
    if (this._datalist_fechas_de_expiracion && this._datalist_fechas_de_expiracion.getElementsByTagName('option').length > 0) {
      console.log("Esta vacio la fecha de expiracion");
    }
    else{
      console.log("No esta vacio la fecha de expiracion");
    }
    return datos;
  }

  limpiar_campos(){
    if (this._campos_a_limpiar) {
      this._campos_a_limpiar.forEach(campo => {
        if(campo.type === 'file'){
          const label = document.querySelector(`label[for="${campo.id}"]`);
          if(label){
            label.textContent = '';
          }
        }
      if (campo.type === 'checkbox') {
        campo.checked = false;
      } else {
        campo.value = '';
      }
      });
    }
  }

  deshabilitar_campos(){
    if (this._campos_dehabilitar) {
      this._campos_dehabilitar.forEach(campo => {
      campo.disabled = true;
      });
    }
  }

  actualizar_campos_historico(){
    let elementos = this._campos_a_enviar;
    for (var i = 0; i < elementos.length; i++){
      if(elementos[i].dataset.historico === "true"){
        localStorage.setItem(elementos[i].dataset.ultimo_valor,elementos[i].value);
      }
    }
    return true;
  }

  actualizar_ult_capturas(objeto){
    console.log("actualizar_ult_capturas");
    console.log(objeto);
    
    // Obtener el ID de la planificación activa
    const planificacionId = document.getElementById("input_planificacion_activa")?.value;
    if (!planificacionId) {
      console.warn("No se encontró ID de planificación activa");
      return;
    }
    
    // Usar una key específica por planificación
    const storageKey = `ultimas_capturas_${planificacionId}`;
    let elementos_ls = localStorage.getItem(storageKey);
    
    if(elementos_ls === null){
      let arreglo = [];
      arreglo.push(objeto);
      localStorage.setItem(storageKey, JSON.stringify(arreglo)); 
    }else{
      let arreglo = [];
      arreglo = JSON.parse(elementos_ls);
      if(arreglo.length > 9){
        arreglo.shift();
      }
      arreglo.push(objeto);
      localStorage.setItem(storageKey, JSON.stringify(arreglo)); 
    }
  }

}

export {InputTexto};





