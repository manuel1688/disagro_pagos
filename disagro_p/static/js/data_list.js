import {envio_objeto,evaluar_instruccion,peticion,agregar_atributos} from "/static/js/operaciones_dom.js"; 

class Datalist {

  constructor(){
    this._selector = null;
    this._url_de_datos = null;
    this._tipo_peticion = null;
    this._tipo = null;
    this._accion = null;
    this._object_store = null;
    this._cache_version = '';
  }

  set selector(selector){
    this._selector = selector;
  }

  set url_de_dato(url){
    this._url_de_datos = url;
  }

  set tipo_peticion(tipo){
    this._tipo_peticion = tipo;
  }

  set tipo(tipo_elmento){
    this._tipo = tipo_elmento;
  }

  set accion(callback){
    this._accion = callback;
  }

  set object_store(store){
    this._object_store = store;
  }

  set version(value){
    this._cache_version = value || '';
  }

  cargar_datos_ls(){
    const datalist_selector = this._selector;
    const cacheKey = this._object_store;
    let cachePayload = null;

    if (cacheKey) {
      try {
        const raw = localStorage.getItem(cacheKey);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && parsed.version === this._cache_version && Array.isArray(parsed.datos)) {
            cachePayload = parsed;
          } else {
            localStorage.removeItem(cacheKey);
          }
        }
      } catch (err) {
        localStorage.removeItem(cacheKey);
      }
    }

    if (cachePayload) {
      this.agregar_opciones_datalist(cachePayload.datos, datalist_selector);
      return;
    }

    peticion(`${this._url_de_datos}`)
    .then( (data) => {
      if(data.RESPUESTA == "OK"){
        const datos = Array.isArray(data["DATOS"]) ? data["DATOS"] : [];
        const responseVersion = data["version"] || this._cache_version || '';
        if (cacheKey) {
          try {
            localStorage.setItem(cacheKey, JSON.stringify({ version: responseVersion, datos }));
          } catch (storageError) {
            // Ignorar errores de almacenamiento (por ejemplo, cuota llena)
          }
        }
        this._cache_version = responseVersion;
        this.agregar_opciones_datalist(datos,datalist_selector);
      }else if(data.RESPUESTA == "BAD"){
        alert(data.MENSAJE);
      }
    }); 
  }

  agregar_opciones_datalist(elementos,datalist){
    if (!datalist) {
      return;
    }
    datalist.innerHTML = '';
    elementos.forEach(async function(e) {
      let option = document.createElement("option");
      option.classList.add("opciones");
      let {CODIGO,DESCRIPCION} = e;
      agregar_atributos({"value":CODIGO,"label":`${DESCRIPCION} | ${CODIGO}`},option);
      datalist.appendChild(option);
    });
  }

}


export {Datalist};



