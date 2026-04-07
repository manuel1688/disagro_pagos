import { envio_objeto_json} from "/static/js/operaciones_dom.js";
import { InputCheck } from "/static/js/input_check.js";
import { getTimezoneForRequest } from "/static/js/timezone_utils.js";

// ===================================================================================
// -----  Input check Categoria 1: campo para agregar filtros para la categoria 1  ---

const input_check_categoria_1 = new InputCheck();
input_check_categoria_1.selector = document.querySelector("#input_categoria_1");
input_check_categoria_1.datalist = document.querySelector("#datalist_categorias_1");
input_check_categoria_1.lista_check = document.querySelector("#lista_check_categoria_1");

// ===================================================================================
// -----  Input check Categoria 2: campo para agregar filtros para la categoria 2  ---
const input_check_categoria_2 = new InputCheck();
input_check_categoria_2.selector = document.querySelector("#input_categoria_2");
input_check_categoria_2.datalist = document.querySelector("#datalist_categorias_2");
input_check_categoria_2.lista_check = document.querySelector("#lista_check_categoria_2");

// ===================================================================================
// ----- Inpur check Ubicacion: campo para agregar filtros para la ubicacion  --------
const input_check_ubicacion = new InputCheck();
input_check_ubicacion.selector = document.querySelector("#input_ubicacion");
input_check_ubicacion.datalist = document.querySelector("#datalist_ubicaciones");
input_check_ubicacion.lista_check = document.querySelector("#lista_check_ubicaciones");

// ===================================================================================
// ----- Inpur check Almacen: campo para agregar filtros para el almacen  ------------
const input_check_almacen = new InputCheck();
input_check_almacen.selector = document.querySelector("#input_almacen");
input_check_almacen.datalist = document.querySelector("#datalist_almacenes");
input_check_almacen.lista_check = document.querySelector("#lista_check_almacenes");

// ===================================================================================
// -----  Inpur check Usuario:  usuario hace click para filtrar los datos  ---------------

const input_check_usuario = new InputCheck();
input_check_usuario.selector = document.querySelector("#input_usuario");
input_check_usuario.datalist = document.querySelector("#datalist_usuarios");
input_check_usuario.lista_check = document.querySelector("#lista_check_usuarios");

// ===================================================================================
// -----  Input check Articulo:  usuario hace click para filtrar los datos  ---------------
const input_check_articulo = new InputCheck();
input_check_articulo.selector = document.querySelector("#input_articulo");
input_check_articulo.datalist = document.querySelector("#datalist_articulos");
input_check_articulo.lista_check = document.querySelector("#lista_check_articulos");


$( function(){

        // ===================================================================================
        // -----  DataTable:  tabla para mostrar los datos de la planificacion  ------------
        idioma["emptyTable"] = "No hay resultados.";
        $("#cargando").removeClass('d-none');
        const grid_de_venta = $('#grid_planificacion').DataTable({
            "paging": true,
            "responsive": true,
            "language": idioma,
            "searching": true,
            "drawCallback": function(settings) {
                $("#contenedor").removeClass('d-none');
                $("#cargando").addClass('d-none');
            },
            'select': 'multi',
            'order': [[1, 'asc']]
        }); 
        

        // ===================================================================================
        // -----  Boton Filtrar:  usuario hace click para filtrar los datos  -----------------
        // Filtrar no deberia registrar una nueva planificacion, solo filtrar los datos
        ensureDefaultSelections();

        const botonFiltrar = document.querySelector("#boton_filtrar");
        botonFiltrar.addEventListener("click", function() {
            ensureDefaultSelections();
            const filtros = [];
            agregarFiltro_categoria("lista_check_categoria_1", "CATEGORIA", "1",filtros);
            agregarFiltro_categoria("lista_check_categoria_2", "CATEGORIA", "2",filtros);
            agregarFiltro("lista_check_ubicaciones", "UBICACION", filtros);
            agregarFiltro("lista_check_almacenes", "ALMACEN", filtros);
            agregarFiltro("lista_check_usuarios", "USUARIO", filtros);
            
            const filtrosString = JSON.stringify(filtros);
            const planificacionId = document.querySelector("#input_planificacion_id").value;
            envio_objeto_json(filtrosString,"/planificacion/filtrar/"+planificacionId,"POST").then((data) => {
                if (!data.error) {
                    // console.log(data);
                    // console.log(data.articulos_filtrados);
                    const datalistArticulos = document.querySelector("#datalist_articulos");
                    datalistArticulos.innerHTML = "";
                    data.articulos_filtrados.forEach(articulo => {
                        // console.log(articulo);
                        const option = document.createElement("option");
                        // console.log(articulo[0]);
                        option.setAttribute("data-codigo", articulo[0]);
                        option.value = articulo[0];
                        option.setAttribute("data-descripcion",articulo[1]);
                        option.textContent = articulo[1];
                        // console.log(articulo[1]);
                        datalistArticulos.appendChild(option);
                    });
                    alert(data.mensaje);
                    grid_de_venta.clear().draw();
                    grid_de_venta.rows.add(data.articulos_filtrados).draw();
                } else {
                    alert(`ERROR: ${data.mensaje}`);
                }
            });
        });


        // ===================================================================================
        // -----  Boton Planificar:  usuario hace click para planificar los datos  -----------
        const botonPlanificar = document.querySelector("#boton_planificar");
        const id = document.querySelector("#input_planificacion_id").value;
        botonPlanificar.addEventListener("click", function() {

            ensureDefaultSelections();
            const listaCheckUsuarios = document.querySelector("#lista_check_usuarios");
            const checkboxes = listaCheckUsuarios.querySelectorAll("input[type='checkbox']");
            const selected = Array.from(checkboxes).filter(cb => cb.checked);
            
            if (selected.length === 0) {
                if (confirm('No hay usuarios definidos, en este caso se asignarán todos los usuarios, ¿Desea continuar con la planificación?.')) {
                    // Continuar
                } else {
                    // Cancelar
                    return;
                }
            }

            if(confirm('¿Está seguro que desea planificar los datos seleccionados?')) {
                // Continuar
            }
            else {
                // Cancelar
                return;
            }

            const filtros = [];
            agregarFiltro_categoria("lista_check_categoria_1", "CATEGORIA", "1",filtros);
            agregarFiltro_categoria("lista_check_categoria_2", "CATEGORIA", "2",filtros);
            agregarFiltro("lista_check_ubicaciones", "UBICACION", filtros);
            agregarFiltro("lista_check_almacenes", "ALMACEN", filtros);
            agregarFiltro("lista_check_usuarios", "USUARIO", filtros);
            agregarFiltro("lista_check_articulos", "ARTICULO", filtros);
            
            // Crear el objeto con filtros y timezone
            const payload = {
                filtros: filtros,
                timezone: getTimezoneForRequest()
            };
            
            const payloadString = JSON.stringify(payload);
            envio_objeto_json(payloadString,`/planificacion/planificar/${id}`,"POST").then((data) => {
                if (!data.error) {
                    alert(data.mensaje);
                    // window.location.reload();
                } else {
                    alert(`ERROR: ${data.mensaje}`);
                }
            });
        });
        
    });    

// ===================================================================================
// -----  FUNCIÓN: agregarFiltro:  agrega los filtros seleccionados por el usuario  --
function agregarFiltro(listaCheckId, tabla, filtros) {
    const divs = document.querySelectorAll(`#${listaCheckId} .custom-checkbox`);
    // console.log(divs);
    const ids = Array.from(divs).map(div => {
        const checkbox = div.querySelector("input");
        return checkbox.getAttribute('data-codigo') || checkbox.id;
    });
    filtros.push({
        "TABLA": tabla,
        "FILTRO": ids
    });
}


// ===================================================================================
// -----  FUNCIÓN: agregarFiltro_categoria:  agrega los filtros de categoria 1 y 2  ----
function agregarFiltro_categoria(listaCheckId, tabla, agrupacion,filtros) {
    const divs = document.querySelectorAll(`#${listaCheckId} .custom-checkbox`);
    const ids = Array.from(divs).map(div => {
        const checkbox = div.querySelector("input");
        return checkbox.getAttribute('data-codigo') || checkbox.id;
    });
    filtros.push({
        "TABLA": tabla,
        "AGRUPACION": agrupacion,
        "FILTRO": ids
    });
}


function ensureDefaultSelections() {
    ensureDefaultForList('lista_check_categoria_1', {
        checkboxId: 'TODAS_1_CATEGORIA_1',
        label: 'TODAS',
        dataCodigo: 'TODAS_1'
    });
    ensureDefaultForList('lista_check_categoria_2', {
        checkboxId: 'TODAS_2_CATEGORIA_2',
        label: 'TODAS',
        dataCodigo: 'TODAS_2'
    });
    ensureDefaultForUbicaciones();
    ensureDefaultForAlmacenes();
    ensureDefaultForList('lista_check_usuarios', {
        checkboxId: 'TODAS_USUARIO',
        label: 'TODAS',
        dataCodigo: 'TODAS'
    });
}

function ensureDefaultForUbicaciones() {
    const lista = document.querySelector('#lista_check_ubicaciones');
    if (!lista) {
        return;
    }
    ensureDefaultForList('lista_check_ubicaciones', {
        checkboxId: 'TODAS_UBICACION_AUTO',
        label: 'TODAS',
        dataCodigo: 'TODAS'
    });
}

function ensureDefaultForAlmacenes() {
    const lista = document.querySelector('#lista_check_almacenes');
    if (!lista) {
        return;
    }
    ensureDefaultForList('lista_check_almacenes', {
        checkboxId: 'TODAS_ALMACEN_AUTO',
        label: 'TODAS',
        dataCodigo: 'TODAS'
    });
}

function ensureDefaultForList(listaCheckId, config) {
    const lista = document.querySelector(`#${listaCheckId}`);
    if (!lista) {
        return;
    }
    const tieneElementos = lista.querySelector('input.custom-control-input');
    if (tieneElementos) {
        return;
    }

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.classList.add('custom-control-input');
    checkbox.id = config.checkboxId;
    checkbox.checked = true;
    if (config.dataCodigo) {
        checkbox.setAttribute('data-codigo', config.dataCodigo);
    }

    const label = document.createElement('label');
    label.classList.add('custom-control-label');
    label.setAttribute('for', config.checkboxId);
    label.textContent = (config.label || 'TODAS');

    const contenedor = document.createElement('div');
    contenedor.classList.add('custom-control', 'custom-checkbox');
    contenedor.appendChild(checkbox);
    contenedor.appendChild(label);

    checkbox.addEventListener('change', (event) => {
        if (!event.target.checked) {
            contenedor.remove();
        }
    });

    lista.appendChild(contenedor);
}
