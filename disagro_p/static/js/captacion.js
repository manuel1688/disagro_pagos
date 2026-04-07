 import { cargar_fecha } from "/static/js/fecha_hora.js";
import { InputTexto } from "/static/js/input_texto.js";
import { crear_elemento,envio_objeto_json } from "/static/js/operaciones_dom.js";
import { Datalist } from "./data_list.js"; 

const input_articulo = document.getElementById("input_articulo");

$( function(){
  idioma["emptyTable"] = "No hay resultados.";
  $("#cargando").removeClass('d-none');
  const grid_de_venta = $('#grid_captaciones').DataTable({
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
});  

document.addEventListener("DOMContentLoaded", () => {
  // Manejar el clic en el botón "Corregir"
  const corregirButtons = document.querySelectorAll(".corregir-btn");
  corregirButtons.forEach(button => {
    button.addEventListener("click", () => {
      const row = button.closest("tr"); // Obtener la fila de la tabla
      const captacionId = button.getAttribute("data-id");
      const cantidadActual = button.getAttribute("data-cantidad");
      const articuloCodigo = row.children[1].textContent.trim(); // Código del artículo
      const articuloDescripcion = row.children[2].textContent.trim(); // Descripción del artículo

      // Depuración: Verificar los valores obtenidos
      console.log("ID Captación:", captacionId);
      console.log("Cantidad Actual:", cantidadActual);
      console.log("Código del Artículo:", articuloCodigo);
      console.log("Descripción del Artículo:", articuloDescripcion);

      // Rellenar los campos del modal
      document.getElementById("captacion_id").value = captacionId;
      document.getElementById("articulo_id").value = articuloCodigo;
      document.getElementById("articuloDescripcion").value = articuloDescripcion;
      document.getElementById("cantidadAnterior").value = cantidadActual;
    });
  });

  // Manejar el envío del formulario
  const corregirForm = document.getElementById("corregirForm");
  corregirForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const captacion_id = document.getElementById("captacion_id").value;
    const articulo_id = document.getElementById("articulo_id").value;
    const usuario = document.getElementById("usuario").value;
    const contrasena = document.getElementById("contrasena").value;
    const nueva_cantidad = document.getElementById("nueva_cantidad").value;


    const datos = {
      captacion_id: captacion_id,
      articulo_id: articulo_id,
      usuario: usuario,
      contrasena: contrasena,
      nueva_cantidad: nueva_cantidad
    };

    const datosString = JSON.stringify(datos);

    envio_objeto_json(datosString, "/inventario/captura/corregir", "POST")
      .then((data) => {
        if (!data.error) {
          alert(data.mensaje);
          $('#corregirModal').modal('hide');
          location.reload();
        } else {
          alert(`ERROR: ${data.mensaje}`);
        }
      })
      .catch((err) => console.error(err));
  });
});

