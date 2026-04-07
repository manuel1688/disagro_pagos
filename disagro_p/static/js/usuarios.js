import { envio_objeto_json,envio_archivo} from "/static/js/operaciones_dom.js";
import { InputFile } from "/static/js/input_file.js";
import { InputCheck } from "/static/js/input_check.js";
 
const input_usuarios = document.querySelector("#input_usuarios");
const label_input_file = document.querySelector("#label_usuarios");
const boton_subir_usuarios = document.querySelector("#boton_subir_usuarios");
const boton_ver_usuarios = document.querySelector("#boton_ver_usuarios");
const boton_guardar = document.querySelector("#boton_guardar");
const boton_ver_input_usuarios = document.querySelector("#boton_ver_input_usuarios");

// ===================================================================================
// -----  Input file Usuarios 1: campo para adjuntar maestro de usuarios  -------

if (input_usuarios) {
    const input_file_usuarios = new InputFile();
    input_file_usuarios.selector = input_usuarios; 
    input_file_usuarios.label_file_name = label_input_file;
    input_file_usuarios.boton_ver_datos = boton_ver_input_usuarios;
    input_file_usuarios.url = `/usuario/upload/usuarios`;
    input_file_usuarios.tipo_peticion = "POST";
    input_file_usuarios.permite_campo_en_blanco = false;
    input_file_usuarios.campos_a_enviar = [input_usuarios];
    input_file_usuarios.contenedor_resultado = document.querySelector("#contenedor_resultado_input_usuarios");
    input_file_usuarios.boton_enviar = boton_subir_usuarios;
    input_file_usuarios.url_redireccion = window.location.pathname;
    input_file_usuarios.redirigir = true;
}

// ===================================================================================

// ===================================================================================
// ----- Efectos visuales para tarjetas de roles _______
document.querySelectorAll('.role-card').forEach(card => {
    const checkbox = card.querySelector('input[type="checkbox"]');
    
    // Actualizar estado visual al cargar
    if (checkbox && checkbox.checked) {
        card.classList.add('active');
    }
    
    // Toggle al hacer clic en la tarjeta
    card.addEventListener('click', function(e) {
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') {
            checkbox.checked = !checkbox.checked;
            card.classList.toggle('active', checkbox.checked);
        }
    });
    
    // Actualizar clase al cambiar checkbox
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            card.classList.toggle('active', this.checked);
        });
    }
});

// ===================================================================================
// ----- Validación de permisos _______
function validarPermisos() {
    const permisos = ['super_usuario', 'nivel_1', 'nivel_2', 'nivel_3', 'nivel_4', 'nivel_5'];
    const algunPermisoSeleccionado = permisos.some(permiso => {
        const checkbox = document.querySelector(`#${permiso}`);
        return checkbox && checkbox.checked;
    });
    
    if (!algunPermisoSeleccionado) {
        alert('⚠️ Debe seleccionar al menos un permiso para el usuario.');
        return false;
    }
    return true;
}

// ===================================================================================
// ----- Guardar cambios de usuario _______
if (boton_guardar) {
    boton_guardar.addEventListener("click", function() {
        console.log("click boton guardar");
        
        // Validar que haya al menos un permiso seleccionado
        if (!validarPermisos()) {
            return;
        }
        
        // Deshabilitar botón mientras se procesa
        boton_guardar.disabled = true;
        boton_guardar.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Guardando...';
        
        const data = {
            "nombre": document.querySelector("#nombre")?.value || '',
            "super_usuario": document.querySelector("#super_usuario")?.checked || false,
            "nivel_1": document.querySelector("#nivel_1")?.checked || false,
            "nivel_2": document.querySelector("#nivel_2")?.checked || false,
            "nivel_3": document.querySelector("#nivel_3")?.checked || false,
            "nivel_4": document.querySelector("#nivel_4")?.checked || false,
            "nivel_5": document.querySelector("#nivel_5")?.checked || false
        };
        
        const body = JSON.stringify(data);
        const usuarioInput = document.querySelector("#usuario");
        const usuario = usuarioInput?.getAttribute('data-usuario') || usuarioInput?.value;
        
        envio_objeto_json(body, `/usuario/${usuario}`, "POST")
            .then((data) => {
                console.log(data);
                if (!data.error) {
                    // Éxito
                    boton_guardar.innerHTML = '<i class="fas fa-check mr-1"></i> Guardado exitosamente';
                    boton_guardar.classList.remove('btn-info');
                    boton_guardar.classList.add('btn-success');
                    
                    // Mostrar mensaje
                    alert('✓ ' + data.mensaje);
                    
                    // Restaurar botón después de 2 segundos
                    setTimeout(() => {
                        boton_guardar.innerHTML = '<i class="fas fa-save mr-1"></i> Guardar Cambios';
                        boton_guardar.classList.remove('btn-success');
                        boton_guardar.classList.add('btn-info');
                        boton_guardar.disabled = false;
                    }, 2000);
                } else {
                    // Error
                    boton_guardar.innerHTML = '<i class="fas fa-save mr-1"></i> Guardar Cambios';
                    boton_guardar.disabled = false;
                    alert(`❌ ERROR: ${data.mensaje}`);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                boton_guardar.innerHTML = '<i class="fas fa-save mr-1"></i> Guardar Cambios';
                boton_guardar.disabled = false;
                alert('❌ ERROR: No se pudo guardar los cambios. Por favor, intenta de nuevo.');
            });
    });
}