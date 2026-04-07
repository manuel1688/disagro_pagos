import { envio_objeto_json, evaluar_campo_blanco,envio_objeto,evaluar_instruccion,peticion,crear_elemento,obtener_arreglo_para_tabla,cargar_datos_filtros,ocultar_loading,agregar_opciones_datalist,limpiar_opciones_datalist} from "/static/js/operaciones_dom.js";
import { getTimezoneForRequest } from "/static/js/timezone_utils.js";

document.addEventListener('DOMContentLoaded', function(){
  const planificacionInput = document.getElementById('id_planificacion');
  if (!planificacionInput) {
    return;
  }

  const approvalModal = document.getElementById('approvalModal');
  const approvalOpenTrigger = document.querySelector('[data-approval-open]');
  const approvalForm = document.getElementById('approvalForm');
  const approvalPassword = document.getElementById('approvalPassword');
  const approvalNotes = document.getElementById('approvalObservaciones');
  const approvalFeedback = approvalModal ? approvalModal.querySelector('[data-approval-feedback]') : null;
  const approvalCloseTriggers = approvalModal ? approvalModal.querySelectorAll('[data-approval-action="close"]') : [];
  const approvalButton = document.getElementById('boton_aprobar');

  const observationModal = document.getElementById('observationModal');
  const observationTrigger = document.querySelector('[data-observation-open]');
  const observationCloseTriggers = observationModal ? observationModal.querySelectorAll('[data-observation-action="close"]') : [];
  const observationDetails = observationModal ? observationModal.querySelector('[data-observation-details]') : null;
  const observationEmpty = observationModal ? observationModal.querySelector('[data-observation-empty]') : null;
  const observationTextNode = observationModal ? observationModal.querySelector('[data-observation-text]') : null;
  const observationUserNode = observationModal ? observationModal.querySelector('[data-observation-user]') : null;
  const observationDateNode = observationModal ? observationModal.querySelector('[data-observation-date]') : null;
  const observationPlanNode = observationModal ? observationModal.querySelector('[data-observation-plan]') : null;
  const observationPlanNameNode = observationModal ? observationModal.querySelector('[data-observation-plan-name]') : null;
  const observationStatusNode = observationModal ? observationModal.querySelector('[data-observation-status]') : null;
  const observationStatusValueNode = observationModal ? observationModal.querySelector('[data-observation-status-value]') : null;
  const observationDigitalNode = observationModal ? observationModal.querySelector('[data-observation-digital]') : null;
  const observationCorrelativoNode = observationModal ? observationModal.querySelector('[data-observation-correlativo]') : null;
  const observationPrintButton = observationModal ? observationModal.querySelector('[data-observation-action="print"]') : null;
  const observationPrintFullButton = observationModal ? observationModal.querySelector('[data-observation-action="print-full"]') : null;

  const getPlanificacionId = () => planificacionInput.value;

  const isModalOpen = (modal) => modal && modal.getAttribute('data-state') === 'open';

  const updateBodyModalState = () => {
    const opened = isModalOpen(approvalModal) || isModalOpen(observationModal);
    document.body.classList.toggle('approval-open', opened);
  };

  const setModalState = (modalNode, state) => {
    if (!modalNode) {
      return;
    }
    // Ensure mutual exclusivity: close other modal when opening one
    if (state === 'open') {
      if (modalNode === approvalModal && observationModal) {
        observationModal.setAttribute('data-state', 'closed');
      } else if (modalNode === observationModal && approvalModal) {
        approvalModal.setAttribute('data-state', 'closed');
      }
    }
    modalNode.setAttribute('data-state', state);
    updateBodyModalState();
  };

  const toggleObservationContent = (hasData) => {
    if (observationDetails) {
      observationDetails.hidden = !hasData;
    }
    if (observationEmpty) {
      observationEmpty.hidden = hasData;
    }
    if (observationPrintButton) {
      observationPrintButton.disabled = !hasData;
    }
    if (observationPrintFullButton) {
      observationPrintFullButton.disabled = !hasData;
    }
  };

  const renderObservation = (data) => {
    if (!observationModal) {
      return;
    }
    const hasData = Boolean(
      data && (
        data.observacion ||
        data.usuario ||
        data.fecha ||
        data.nombre_planificacion ||
        data.reporte_estado
      )
    );
    toggleObservationContent(hasData);

    if (!hasData) {
      return;
    }

    if (observationPlanNameNode && data.nombre_planificacion) {
      observationPlanNameNode.textContent = data.nombre_planificacion;
    }

    if (observationCorrelativoNode) {
      observationCorrelativoNode.textContent = data.correlativo || observationCorrelativoNode.textContent || '-';
    }

    if (observationUserNode) {
      observationUserNode.textContent = data.usuario || '-';
    }

    if (observationDateNode) {
      if (data.fecha) {
        const parsedDate = new Date(data.fecha);
        observationDateNode.textContent = parsedDate.toLocaleString();
      } else {
        observationDateNode.textContent = '-';
      }
    }

    if (observationTextNode) {
      observationTextNode.textContent = data.observacion || 'Sin detalle registrado en el acta.';
    }

    if (observationPlanNode && data.nombre_planificacion) {
      observationPlanNode.textContent = `Planificación: ${data.nombre_planificacion}`;
    }

    const reporteEstado = data.reporte_estado || data.estado_planificacion;
    if (reporteEstado) {
      if (observationStatusNode) {
        observationStatusNode.textContent = `Estado del reporte: ${reporteEstado}`;
      }
      if (observationStatusValueNode) {
        observationStatusValueNode.textContent = reporteEstado;
      }
    }

    if (observationDigitalNode) {
      observationDigitalNode.textContent = data.usuario || '-';
    }

    if (data.correlativo && observationCorrelativoNode) {
      observationCorrelativoNode.textContent = data.correlativo;
    }
  };

  const updateObservationTriggerDataset = (data = {}) => {
    if (!observationTrigger) {
      return;
    }
    observationTrigger.dataset.planificacionNombre = data.nombre_planificacion || '';
    observationTrigger.dataset.planificacionEstado = data.estado_planificacion || data.reporte_estado || '';
    observationTrigger.dataset.planificacionCorrelativo = data.correlativo || '';
    observationTrigger.dataset.hasObservation = data.observacion ? 1 : 0;
  };

  const fetchObservationData = async (planificacionId) => {
    const response = await fetch(`/historial/observaciones/${planificacionId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      credentials: 'same-origin'
    });

    if (!response.ok) {
      throw new Error('Respuesta inválida del servidor');
    }

    const payload = await response.json();

    if (payload.error) {
      throw new Error(payload.mensaje || 'No fue posible recuperar el acta.');
    }

    return payload.data || {};
  };

  const refreshObservationData = async () => {
    if (!observationTrigger) {
      return null;
    }
    try {
      const data = await fetchObservationData(getPlanificacionId());
      updateObservationTriggerDataset(data);
      renderObservation(data);
      observationTrigger.classList.remove('d-none');
      return data;
    } catch (error) {
      console.error('No se pudo actualizar el acta', error);
      return null;
    }
  };

  const handleApprovalSuccess = async () => {
    setModalState(approvalModal, 'closed');
    if (approvalOpenTrigger) {
      approvalOpenTrigger.disabled = true;
      approvalOpenTrigger.classList.add('d-none');
    }
    await refreshObservationData();
    alert('El cierre ha sido aprobado exitosamente.');
  };

  if (approvalModal && approvalForm && approvalPassword && approvalOpenTrigger) {
    const submitButton = approvalForm.querySelector('button[type="submit"]');

    const resetFeedback = () => {
      if (!approvalFeedback) {
        return;
      }
      approvalFeedback.textContent = '';
      approvalFeedback.hidden = true;
    };

    const showError = (message) => {
      if (!approvalFeedback) {
        if (message) {
          alert(message);
        }
        return;
      }
      approvalFeedback.textContent = message;
      approvalFeedback.hidden = !message;
    };

    approvalOpenTrigger.addEventListener('click', (event) => {
      event.preventDefault();
      resetFeedback();
      approvalForm.reset();
      setModalState(approvalModal, 'open');
      setTimeout(() => approvalPassword.focus(), 120);
    });

    approvalCloseTriggers.forEach((ctrl) => {
      ctrl.addEventListener('click', (event) => {
        event.preventDefault();
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.removeAttribute('data-loading');
        }
        setModalState(approvalModal, 'closed');
      });
    });

    approvalForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const password = (approvalPassword.value || '').trim();
      const observaciones = approvalNotes ? (approvalNotes.value || '').trim() : '';

      if (!password) {
        showError('Ingresa tu firma digital para continuar.');
        approvalPassword.focus();
        return;
      }

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.setAttribute('data-loading', 'true');
      }

      const idPlanificacion = getPlanificacionId();
      const payload = {
        id_planificacion: idPlanificacion,
        firma_digital: password,
        observaciones: observaciones,
        TIMEZONE: getTimezoneForRequest()
      };

      try {
        const url = `/historial/agregar/${idPlanificacion}`;
        const response = await envio_objeto_json(JSON.stringify(payload), url, 'POST');

        if (response && response.error === false) {
          await handleApprovalSuccess();
          return;
        }

        const message = response && response.mensaje ? response.mensaje : 'No se pudo completar la aprobación. Inténtalo nuevamente.';
        showError(message);
      } catch (error) {
        console.error('Error aprobando el cierre', error);
        showError('Ocurrió un error inesperado al firmar el reporte.');
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.removeAttribute('data-loading');
        }
        approvalPassword.value = '';
      }
    });
  }

  if (observationModal && observationTrigger) {
    const planNameFromDataset = observationTrigger.getAttribute('data-planificacion-nombre') || '';
    const statusFromDataset = observationTrigger.getAttribute('data-planificacion-estado') || '';
    const correlativoFromDataset = observationTrigger.getAttribute('data-planificacion-correlativo') || '';

    if (observationPlanNode && planNameFromDataset) {
      observationPlanNode.textContent = `Planificación: ${planNameFromDataset}`;
    }
    if (observationPlanNameNode && planNameFromDataset) {
      observationPlanNameNode.textContent = planNameFromDataset;
    }
    if (observationStatusNode && statusFromDataset) {
      observationStatusNode.textContent = `Estado del reporte: ${statusFromDataset}`;
    }
    if (observationStatusValueNode && statusFromDataset) {
      observationStatusValueNode.textContent = statusFromDataset;
    }
    if (observationCorrelativoNode && correlativoFromDataset) {
      observationCorrelativoNode.textContent = correlativoFromDataset;
    }

    observationCloseTriggers.forEach((ctrl) => {
      ctrl.addEventListener('click', (event) => {
        event.preventDefault();
        setModalState(observationModal, 'closed');
      });
    });

    if (observationPrintButton) {
      observationPrintButton.addEventListener('click', (event) => {
        event.preventDefault();
        window.print();
      });
    }

    if (observationPrintFullButton) {
      observationPrintFullButton.addEventListener('click', (event) => {
        event.preventDefault();
        printActaCompleta();
      });
    }

    const printActaCompleta = () => {
      // Obtener contenido del acta del modal
      const actaContent = document.querySelector('[data-observation-details]');
      if (!actaContent) {
        alert('No se puede imprimir el acta en este momento');
        return;
      }
      
      // Obtener la tabla del reporte (ajusta el selector según tu página)
      const reportTable = document.querySelector('.report-table, table.waffle, .differences-table, .transit-table, #reporte_toma_fisica table');
      
      // Obtener información del header
      const planificacionNombre = document.querySelector('[data-observation-plan-name]')?.textContent || '-';
      const correlativo = document.querySelector('[data-observation-correlativo]')?.textContent || '-';
      const fechaAprobacion = document.querySelector('[data-observation-date]')?.textContent || '-';
      const usuarioAprobacion = document.querySelector('[data-observation-user]')?.textContent || '-';
      const observacionTexto = document.querySelector('[data-observation-text]')?.textContent || 'Sin observaciones registradas.';
      const estadoReporte = document.querySelector('[data-observation-status-value]')?.textContent || '-';
      
      // Crear ventana de impresión
      const printWindow = window.open('', '', 'height=900,width=1200');
      
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Acta de Aprobación - ${planificacionNombre}</title>
          <style>
            * { box-sizing: border-box; }
            body { 
              font-family: Arial, sans-serif; 
              padding: 30px; 
              font-size: 12px;
              line-height: 1.4;
            }
            
            @media print {
              .no-print { display: none !important; }
              body { padding: 20px; }
              .page-break { page-break-after: always; }
            }
            
            .acta-header {
              text-align: center;
              margin-bottom: 30px;
              border-bottom: 3px solid #333;
              padding-bottom: 20px;
            }
            .acta-header h1 {
              margin: 0 0 10px 0;
              font-size: 24px;
              color: #333;
            }
            .acta-header p {
              margin: 5px 0;
              font-size: 13px;
            }
            
            .acta-section {
              margin-bottom: 25px;
              page-break-inside: avoid;
            }
            .acta-section h2 {
              background-color: #f0f0f0;
              padding: 10px 15px;
              margin: 20px 0 15px 0;
              border-left: 5px solid #007bff;
              font-size: 16px;
            }
            
            .acta-details {
              padding: 15px;
              background-color: #f9f9f9;
              border: 1px solid #ddd;
              border-radius: 4px;
            }
            .acta-details p {
              margin: 8px 0;
            }
            .acta-details strong {
              display: inline-block;
              min-width: 180px;
              color: #555;
            }
            
            .observaciones-box {
              background-color: #fff;
              border: 2px solid #ddd;
              padding: 15px;
              margin: 15px 0;
              white-space: pre-wrap;
              min-height: 80px;
              border-radius: 4px;
            }
            
            /* Estilos de tabla waffle - Preserva el formato original */
            .ritz .waffle a { color: inherit; }
            .ritz .waffle .s0 { background-color:#c9daf8; text-align:center; font-weight:bold; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s1 { background-color:#c9daf8; text-align:center; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s2 { background-color:#ffffff; text-align:center; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s3 { background-color:#ffffff; text-align:left; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s4 { background-color:#c9daf8; text-align:left; font-weight:bold; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s5 { background-color:#c9daf8; text-align:right; font-weight:bold; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s6 { background-color:#f3f3f3; text-align:left; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s7 { background-color:#f3f3f3; text-align:center; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s8 { background-color:#f3f3f3; text-align:left; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s9 { background-color:#ffffff; }
            .ritz .waffle .s10 { background-color:#ffffff; text-align:right; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s11 { background-color:#f3f3f3; text-align:right; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s12 { background-color:#f3f3f3; text-align:right; font-weight:bold; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s13 { background-color:#ffffff; text-align:left; font-weight:bold; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s14 { background-color:#f3f3f3; text-align:right; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s15 { background-color:#ffffff; text-align:right; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s16 { background-color:#ffffff; text-align:left; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s17 { background-color:#ffffff; text-align:right; font-weight:bold; font-style:italic; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s18 { background-color:#f3f3f3; text-align:left; font-weight:bold; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s19 { background-color:#ffffff; text-align:center; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s20 { background-color:#f3f3f3; text-align:center; color:#000000; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            .ritz .waffle .s21 { background-color:#1c4587; text-align:right; font-weight:bold; color:#ffffff; font-family:Arial; font-size:10pt; vertical-align:bottom; white-space:nowrap; direction:ltr; padding:2px 3px 2px 3px; }
            
            /* Estructura de tabla */
            .ritz { border: 1px solid #000; }
            .waffle { border-collapse: collapse; width: 100%; }
            .waffle th, .waffle td { border: 1px solid #ccc; }
            .row-headers-background { background-color: #f3f3f3; }
            
            /* Estilos adicionales para la tabla de reportes */
            table.report-table, table.differences-table, table.transit-table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 15px;
              font-size: 10px;
            }
            table.report-table th, table.report-table td,
            table.differences-table th, table.differences-table td,
            table.transit-table th, table.transit-table td {
              border: 1px solid #ddd;
              padding: 6px 8px;
            }
            
            .firmas-section {
              margin-top: 60px;
              page-break-inside: avoid;
            }
            .firma-grid {
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 50px;
              margin-top: 80px;
            }
            .firma-box {
              text-align: center;
            }
            .firma-linea {
              border-top: 2px solid #000;
              padding-top: 10px;
              margin-top: 50px;
              font-weight: bold;
            }
            .firma-rol {
              color: #666;
              font-size: 11px;
            }
            
            .print-buttons {
              position: fixed;
              top: 10px;
              right: 10px;
              z-index: 1000;
            }
            .btn {
              padding: 10px 20px;
              margin-left: 10px;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-size: 14px;
            }
            .btn-primary {
              background-color: #007bff;
              color: white;
            }
            .btn-secondary {
              background-color: #6c757d;
              color: white;
            }
            .btn:hover {
              opacity: 0.9;
            }
          </style>
        </head>
        <body>
          <div class="print-buttons no-print">
            <button class="btn btn-primary" onclick="window.print()">
              🖨️ Imprimir
            </button>
            <button class="btn btn-secondary" onclick="window.close()">
              ✖ Cerrar
            </button>
          </div>
          
          <div class="acta-header">
            <h1>ACTA DE APROBACIÓN DE INVENTARIO FÍSICO</h1>
            <p><strong>Planificación:</strong> ${planificacionNombre}</p>
            <p><strong>Correlativo:</strong> ${correlativo}</p>
            <p><strong>Fecha de generación:</strong> ${new Date().toLocaleString('es-GT', { 
              dateStyle: 'long', 
              timeStyle: 'short' 
            })}</p>
          </div>
          
          <div class="acta-section">
            <h2>📋 Información de Aprobación</h2>
            <div class="acta-details">
              <p><strong>Estado del reporte:</strong> ${estadoReporte}</p>
              <p><strong>Fecha de aprobación:</strong> ${fechaAprobacion}</p>
              <p><strong>Aprobado por:</strong> ${usuarioAprobacion}</p>
              <p><strong>Firma digital:</strong> ${usuarioAprobacion}</p>
            </div>
          </div>
          
          <div class="acta-section">
            <h2>📝 Observaciones del Cierre</h2>
            <div class="observaciones-box">${observacionTexto}</div>
          </div>
          
          <div class="page-break"></div>
          
          <div class="acta-section">
            <h2>📊 Datos del Inventario Físico</h2>
            ${reportTable ? reportTable.outerHTML : '<p>No hay datos de tabla disponibles</p>'}
          </div>
          
          <div class="page-break"></div>
          
          <div class="acta-section firmas-section">
            <h2>✍️ Firmas de Aprobación</h2>
            <p style="text-align: center; color: #666; margin-bottom: 20px;">
              Confirma la cadena de custodia asociada a esta acta de inventario físico
            </p>
            <div class="firma-grid">
              <div class="firma-box">
                <div class="firma-linea">
                  Jefe de Inventario
                </div>
                <div class="firma-rol">Responsable de coordinación</div>
              </div>
              <div class="firma-box">
                <div class="firma-linea">
                  Supervisor de Almacén
                </div>
                <div class="firma-rol">Verificación operativa</div>
              </div>
              <div class="firma-box">
                <div class="firma-linea">
                  Gerente Financiero
                </div>
                <div class="firma-rol">Aprobación contable</div>
              </div>
              <div class="firma-box">
                <div class="firma-linea">
                  Auditor Interno
                </div>
                <div class="firma-rol">Control y auditoría</div>
              </div>
            </div>
          </div>
          
          <div style="margin-top: 40px; text-align: center; color: #999; font-size: 10px; border-top: 1px solid #ddd; padding-top: 20px;">
            <p>Sistema de Gestión de Inventario DISAGRO &copy; ${new Date().getFullYear()}</p>
            <p>Documento generado electrónicamente - Válido sin firma autógrafa</p>
          </div>
        </body>
        </html>
      `);
      
      printWindow.document.close();
      printWindow.focus();
    };

    const openObservationModal = async (event) => {
      if (event) {
        event.preventDefault();
      }
      try {
        const data = await fetchObservationData(getPlanificacionId());
        renderObservation(data);
        setModalState(observationModal, 'open');
      } catch (error) {
        console.error('Error obteniendo acta de aprobación', error);
        alert('No se pudo cargar el acta de aprobación.');
      }
    };

    observationTrigger.addEventListener('click', openObservationModal);
    window.openObservationModal = openObservationModal;
  }
});
