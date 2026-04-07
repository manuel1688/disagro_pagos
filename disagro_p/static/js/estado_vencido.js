const EXPIRED_FLAG = 'vencido';

const parseFecha = (valor) => {
  if (!valor) {
    return null;
  }
  const texto = valor.trim();
  if (texto.length === 0) {
    return null;
  }

  let dia;
  let mes;
  let ano;
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(texto)) {
    const partes = texto.split('/').map(Number);
    [dia, mes, ano] = partes;
  } else if (/^\d{4}-\d{2}-\d{2}$/.test(texto)) {
    const partes = texto.split('-').map(Number);
    [ano, mes, dia] = partes;
  } else {
    return null;
  }

  const fecha = new Date(ano, mes - 1, dia);
  if (Number.isNaN(fecha.getTime())) {
    return null;
  }
  fecha.setHours(0, 0, 0, 0);
  return fecha;
};

const obtenerEstadoVencido = (datalistEstados) => {
  if (!datalistEstados) {
    return 'VENCIDO';
  }
  const opciones = Array.from(datalistEstados.querySelectorAll('option'));
  const coincidenciaExacta = opciones.find((opcion) => {
    const valor = (opcion.value || opcion.getAttribute('value') || '').trim();
    return valor.toLowerCase() === EXPIRED_FLAG;
  });
  if (coincidenciaExacta) {
    return coincidenciaExacta.value || coincidenciaExacta.getAttribute('value') || 'VENCIDO';
  }
  const coincidenciaPorEtiqueta = opciones.find((opcion) => {
    const etiqueta = (opcion.label || opcion.textContent || '').trim().toLowerCase();
    return etiqueta === EXPIRED_FLAG;
  });
  if (coincidenciaPorEtiqueta) {
    const valor = coincidenciaPorEtiqueta.value || coincidenciaPorEtiqueta.getAttribute('value');
    if (valor && valor.trim().length > 0) {
      return valor;
    }
    return coincidenciaPorEtiqueta.label || coincidenciaPorEtiqueta.textContent || 'VENCIDO';
  }
  return 'VENCIDO';
};

const obtenerFechaReferencia = (inputFechaActual) => {
  const fechaReferencia = parseFecha(inputFechaActual ? inputFechaActual.value : null);
  if (fechaReferencia) {
    return fechaReferencia;
  }
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  return hoy;
};

const notificarCambio = (input) => {
  const eventos = ['input', 'change'];
  eventos.forEach((nombre) => {
    const evento = new Event(nombre, { bubbles: true });
    input.dispatchEvent(evento);
  });
};

export function setupEstadoVencidoAuto({
  inputFechaExpiracion,
  inputEstado,
  datalistEstados,
  inputFechaActual,
}) {
  if (!inputFechaExpiracion || !inputEstado) {
    return () => {};
  }

  const aplicar = () => {
    const fechaExpiracion = parseFecha(inputFechaExpiracion.value);
    const fechaHoy = obtenerFechaReferencia(inputFechaActual);

    if (!fechaExpiracion) {
      if (inputEstado.dataset.autoEstado === EXPIRED_FLAG) {
        inputEstado.value = '';
        delete inputEstado.dataset.autoEstado;
        notificarCambio(inputEstado);
      }
      return;
    }

    if (fechaExpiracion < fechaHoy) {
      const estadoVencido = obtenerEstadoVencido(datalistEstados);
      if (estadoVencido && inputEstado.value !== estadoVencido) {
        inputEstado.value = estadoVencido;
        inputEstado.dataset.autoEstado = EXPIRED_FLAG;
        notificarCambio(inputEstado);
      }
    } else if (inputEstado.dataset.autoEstado === EXPIRED_FLAG) {
      inputEstado.value = '';
      delete inputEstado.dataset.autoEstado;
      notificarCambio(inputEstado);
    }
  };

  ['change', 'blur'].forEach((evento) => {
    inputFechaExpiracion.addEventListener(evento, aplicar);
  });

  inputFechaExpiracion.addEventListener('keyup', (event) => {
    if (event.key === 'Enter' || event.key === 'NumpadEnter') {
      aplicar();
    }
  });

  return aplicar;
}
