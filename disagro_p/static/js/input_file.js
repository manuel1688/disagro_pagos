import { envio_archivo,evaluar_campo_blanco,envio_objeto,evaluar_instruccion,peticion,crear_elemento,obtener_arreglo_para_tabla,cargar_datos_filtros,ocultar_loading } from "/static/js/operaciones_dom.js";
import { getTimezoneForRequest } from "/static/js/timezone_utils.js";

class InputFile {
    constructor() {
        this._selector = null;
        this._label_file_name = null;
        this._url = null;
        this._tipo_peticion = null;
        this._campo_siguiente = null;
        this._campos_a_enviar = null;
        this._contenedor_resultado = null;
        this._boton_ver_datos = null;
        this._tabla = null;
        this._boton_limpiar_datos = null;
        this._boton_enviar = null;
        this._permite_campo_en_blanco = null;
        this._redirigir = false;
        this._url_redireccion = null;
        if (this._selector) {
            this.change();
        }
      }
    
    set url_redireccion(valor){
        this._url_redireccion = valor;
    }

    set redirigir(valor){
        this._redirigir = valor;
    }

    set selector(selector) {
        this._selector = selector;
    }

    set label_file_name(label_file_name) {
        this._label_file_name = label_file_name;
        this.change();
    }

    set url(url) {
        this._url = url;
    }

    set tipo_peticion(tipo_peticion) {
        this._tipo_peticion = tipo_peticion;
    }

    set campo_siguiente(campo_siguiente) {
        this._campo_siguiente = campo_siguiente;
    }

    set campos_a_enviar(campos_a_enviar) {
        this._campos_a_enviar = campos_a_enviar;
    }

    set contenedor_resultado(contenedor_resultado) {
        this._contenedor_resultado = contenedor_resultado;
    }

    set boton_ver_datos(boton_ver_datos) {
        this._boton_ver_datos = boton_ver_datos;
    }

    set boton_enviar(boton_enviar) {
        this._boton_enviar = boton_enviar;
        this.click_enviar();
    }

    set tabla(tabla) {
        this._tabla = tabla;
    }

    set boton_limpiar_datos(boton_limpiar_datos) {
        this._boton_limpiar_datos= boton_limpiar_datos;
        this.click_limpiar();
    }

    set permite_campo_en_blanco(permite_campo_en_blanco) {
        this._permite_campo_en_blanco = permite_campo_en_blanco;
    }

    change() {
        if (this._selector) {
            this._selector.addEventListener("change", (event) => {
                let file_name = event.target.files[0].name;
                this._label_file_name.textContent = file_name;
                this._boton_enviar.disabled = false;
            });
        }
    }

    click_enviar() {
        if (this._boton_enviar) {
            this._boton_enviar.addEventListener("click", (event) => {
                let archivo = this._selector.files[0];
                if(!archivo){
                    alert("Seleccione un archivo");
                    this._selector.classList.add("is-invalid");
                    return;
                }

                let formData = new FormData();
                // Attach the plan name if the page provides an input with id 'input_planificacion_nombre'
                const nombreEl = document.getElementById('input_planificacion_nombre');
                if (nombreEl) {
                    const nombreVal = nombreEl.value ? nombreEl.value.trim() : '';
                    // Append even if empty; backend will validate presence if required
                    formData.append('nombre', nombreVal);
                }

                const correlativoEl = document.getElementById('input_correlativo_base');
                if (correlativoEl) {
                    correlativoEl.classList.remove('is-invalid');
                    let correlativoVal = correlativoEl.value ? correlativoEl.value.trim() : '';
                    correlativoVal = correlativoVal.toUpperCase().replace(/\s+/g, '-');
                    correlativoEl.value = correlativoVal;
                    if (!correlativoVal) {
                        correlativoEl.classList.add('is-invalid');
                        alert('Ingresa un identificador de correlativo válido.');
                        return;
                    }
                    if (!/^[A-Z0-9-]+$/.test(correlativoVal) || !/[A-Z]/.test(correlativoVal)) {
                        correlativoEl.classList.add('is-invalid');
                        alert('El identificador del correlativo debe contener al menos una letra y solo puede incluir letras, números o guiones.');
                        return;
                    }
                    formData.append('correlativo_base', correlativoVal);
                }

                const tipoCorrelativoEl = document.getElementById('select_tipo_correlativo');
                if (tipoCorrelativoEl) {
                    formData.append('tipo_correlativo', tipoCorrelativoEl.value || '');
                }

                formData.append("archivo", archivo);
                
                // Agregar zona horaria del navegador del usuario para planificaciones
                formData.append('timezone', getTimezoneForRequest());
                
                const texto_boton = this._boton_enviar.textContent.trim();
                this._boton_enviar.innerHTML = 'Enviando ... <span class="spinner-border"></span>';
                this._boton_enviar.disabled = true;
                envio_archivo(formData, this._url, this._tipo_peticion)
                .then((data) => {
                  if (!data.error) {
                    this._boton_enviar.innerHTML = `${texto_boton} <span class="fa fa-upload"></span>`;
                    this._boton_ver_datos.classList.remove('d-none');
                    const today = new Date();
                    let formattedDate = this._formatDate(today);
                    this._contenedor_resultado.innerHTML = "Actualizado: " + formattedDate;
                    this._contenedor_resultado.classList.add('d-block');
                    if (this._boton_limpiar_datos) {
                        this._boton_limpiar_datos.classList.remove('d-none');
                        this._boton_limpiar_datos.disabled = false;
                    }
                    const mensajeCorrelativo = data.correlativo ? ` (Correlativo: ${data.correlativo})` : '';
                    alert(`${data.mensaje}${mensajeCorrelativo}`);
                    console.log(data.id);
                    let url = `${this._url_redireccion}/${data.id}`;
                    console.log(url);
                    if(data.id && this._redirigir){
                        console.log("redirigir");
                        window.location.href = `${this._url_redireccion}/${data.id}`;
                    }
                    else if (this._redirigir){
                        window.location.href = this._url_redireccion;
                    }
                  } else {
                      alert(`ERROR: ${data.mensaje}`);
                      this._boton_enviar.innerHTML = `${texto_boton} <span class="fa fa-upload"></span>`;
                      this._boton_enviar.disabled = false;
                  }
              }).catch((error) => {
                // Manejo de errores inesperados
                console.error("Error inesperado:", error);
                alert("Ocurrió un error inesperado. Por favor, revisar privilegios o inténtelo de nuevo más tarde.");
                this._boton_enviar.innerHTML = `${texto_boton} <span class="fa fa-upload"></span>`;
                this._boton_enviar.disabled = false;
              });

            });
        }
    }

    click_limpiar() {
        if (this._boton_limpiar_datos && this._tabla) {
            this._boton_limpiar_datos.addEventListener("click", (event) => {
                const confirmacion = confirm("¿Desea limpiar los datos?");
                if (confirmacion) {
                    let body = null;
                    if (this._tabla === "EXISTENCIAS") {
                        body = JSON.stringify({TABLA:'EXISTENCIAS'})
                    }else if (this._tabla === "ARTICULOS") {
                        body = JSON.stringify({TABLA:'ARTICULOS'});
                    }
                    envio_objeto(body,"/admin/upload/limpiar","DELETE").then((data) => {
                        console.log(data);
                        if (!data.error) {
                            alert(data.mensaje);
                            window.location.reload();
                        } else {
                            alert(`ERROR: ${data.mensaje}`);
                        }
                    });
                }
            });
        }
    }

    _formatDate(date) {
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
  }
}

export { InputFile };
