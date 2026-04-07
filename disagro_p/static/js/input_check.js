import { envio_archivo,evaluar_campo_blanco,envio_objeto,evaluar_instruccion,peticion,crear_elemento,obtener_arreglo_para_tabla,cargar_datos_filtros,ocultar_loading } from "/static/js/operaciones_dom.js"; 

class InputCheck {
    constructor() {
        this._selector = null;
        this.lista_check = null;
    }

    set selector(selector) {
        this._selector = selector;
    }
 
    set lista_check(lista_check) {
        this._lista_check = lista_check;
        this.click_up();
        this.keyup();
    }

    set datalist(datalist) {
        this._datalist = datalist;
    }

    // ===================================================================================
    // -----  Click up:  usuario hace click para agregar un filtro  ---------------------
    click_up(){
        if(this._lista_check)
        {
            // Se obtienen los checkboxes de la lista del input check
            const checkboxes = this._lista_check.querySelectorAll('div.custom-checkbox input[type="checkbox"]')
            // Se agrega un evento a cada checkbox para que al desmarcarlo se elimine el div que lo contiene
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener("change", (e) => {
                    if (!e.target.checked) {
                        const div = e.target.parentElement;
                        div.remove();
                    }
                });
            });
        }
    }

    keyup(){
        if (this._selector) {
            this._selector.addEventListener("keyup", (e) => {
                const target = e.target;
                // El valor representa el código de la opción
                let valor = target.value;
                
                if(evaluar_instruccion(e.code,valor)){
                    const opciones = this._datalist.options;
                    let coincidencia = false;
                    // El valor es comparado con todos los códigos de las opciones para encontrar una coincidencia
                    for (let i = 0; i < opciones.length; i++) {
                        const opcion = opciones[i];
                        const descripcion = opcion.dataset.descripcion;
                        const codigo = opcion.dataset.codigo;
                        const texto = opcion.text;

                        // console.log("Descripcion de la opcion: ");
                        // console.log(descripcion);
                        // console.log("Codigo de la opcion: ");
                        // console.log(codigo);
                        // console.log("Texto de la opcion: ");
                        // console.log(texto);

                        console.log(valor.toUpperCase());
                        // Se verifica si el valor ingresado coincide con el código de la opción
                        if (codigo === valor) {
                            
                            // Primero se verifica si el valor ingresado es "TODAS" las opciones
                            // luego se verifica si el valor ingresado es "TODAS_1" o "TODAS_2"
                            // si no es todas, se verifica si el valor ya existe en la lista, solo se limpia el input
                            // luego como no existe, se limpia la opción "TODAS" en caso de que exista
                            const es_todas = valor.toUpperCase() === "TODAS" || valor.toUpperCase() === "TODAS_1" || valor.toUpperCase() === "TODAS_2";
                            if (es_todas) {
                                this._lista_check.innerHTML = "";
                                valor = "TODAS";
                            } else {
                                const existingValues = Array.from(this._lista_check.querySelectorAll("input.custom-control-input")).map(input => input.getAttribute('data-codigo'));
                                if (existingValues.includes(valor)) {
                                    console.log("El valor ya existe en la lista.");
                                    this._selector.value = ""; // SE LIMPIA EL INPUT
                                    return;
                                }
                                const divTodas = this._lista_check.querySelector('div.custom-checkbox label.custom-control-label');
                                if (divTodas && divTodas.textContent.toUpperCase() === "TODAS") {
                                    console.log("Se encontró un div con label 'TODAS'.");
                                    divTodas.parentElement.remove(); 
                                }
                            }

                            // Se optiene el codigo de la opcion
                            const codigo = opcion.dataset.codigo;
                            coincidencia = true;

                            const nombre = target.dataset.nombre;
                            const checkbox = crear_elemento("input",["custom-control-input"], { "type": "checkbox", "id": codigo + "_" + nombre, "checked": "true","data-codigo": codigo});
                            let label = null;
                            if (es_todas) {
                                label = crear_elemento("label",["custom-control-label"], { "for": codigo + "_" + nombre }, valor.toUpperCase());
                            }else 
                            {
                                label = crear_elemento("label",["custom-control-label"], { "for": codigo + "_" + nombre }, descripcion);
                            }
                            const div = crear_elemento("div",["custom-control","custom-checkbox"]);
                            div.appendChild(checkbox);
                            div.appendChild(label);
                            checkbox.addEventListener("change", (e) => {
                                if (!e.target.checked) {
                                    div.remove();
                                }
                            });
                            this._lista_check.appendChild(div);
                            
                            break;
                        }
                    }
                    
                    if (coincidencia) {
                        console.log("Se encontró una opción que coincide con el valor.");
                        // se limpia el input ya que se encontró una coincidencia
                        this._selector.value = "";
                    } else {
                        console.log("No se encontró ninguna opción que coincida con el valor.");
                    }
                }
            });
        }
    }
}

export { InputCheck };