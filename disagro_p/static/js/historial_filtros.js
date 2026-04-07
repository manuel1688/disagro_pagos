const form = document.getElementById('historialFilterForm');
const startInput = document.getElementById('start_date');
const endInput = document.getElementById('end_date');
const correlativoInput = document.getElementById('correlativo');
const nombreInput = document.getElementById('nombre_planificacion');
const quickFilterButtons = document.querySelectorAll('.quick-filter-btn');
const planificacionButtons = document.querySelectorAll('.planificacion-item');
const clearButton = document.getElementById('clearFilters');

const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const setDateRange = (rangeKey) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let startDate = new Date(today);
  let endDate = new Date(today);

  switch (rangeKey) {
    case 'today':
      // startDate y endDate ya están configurados como hoy
      break;
    case 'yesterday': {
      startDate.setDate(startDate.getDate() - 1);
      endDate = new Date(startDate);
      break;
    }
    case 'last7':
      startDate.setDate(startDate.getDate() - 6);
      break;
    case 'last30':
      startDate.setDate(startDate.getDate() - 29);
      break;
    case 'thisMonth': {
      startDate = new Date(today.getFullYear(), today.getMonth(), 1);
      break;
    }
    case 'lastMonth': {
      const firstDayPrevMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const lastDayPrevMonth = new Date(today.getFullYear(), today.getMonth(), 0);
      startDate = firstDayPrevMonth;
      endDate = lastDayPrevMonth;
      break;
    }
    default:
      return;
  }

  startInput.value = formatDate(startDate);
  endInput.value = formatDate(endDate);
};

const setActiveQuickFilter = (targetButton) => {
  quickFilterButtons.forEach((button) => button.classList.remove('active'));
  if (targetButton) {
    targetButton.classList.add('active');
  }
};

const clearPlanificacionSelection = () => {
  planificacionButtons.forEach((button) => button.classList.remove('active'));
};

quickFilterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setActiveQuickFilter(button);
    clearPlanificacionSelection();
    setDateRange(button.dataset.range);
  });
});

planificacionButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const { start, end, reportUrl } = button.dataset;
    if (reportUrl) {
      window.location.href = reportUrl;
      return;
    }

    if (start) {
      startInput.value = start;
    }
    if (end) {
      endInput.value = end;
    }
    clearPlanificacionSelection();
    button.classList.add('active');
    setActiveQuickFilter(null);
    form?.submit();
  });
});

[startInput, endInput].forEach((input) => {
  input?.addEventListener('input', () => {
    if (input.value) {
      setActiveQuickFilter(null);
      clearPlanificacionSelection();
    }
  });
});

clearButton?.addEventListener('click', () => {
  startInput.value = '';
  endInput.value = '';
  if (correlativoInput) correlativoInput.value = '';
  if (nombreInput) nombreInput.value = '';
  setActiveQuickFilter(null);
  clearPlanificacionSelection();
  startInput.focus();
});

form?.addEventListener('submit', (event) => {
  const hasStart = !!(startInput && startInput.value);
  const hasEnd = !!(endInput && endInput.value);
  const hasCorrelativo = !!(correlativoInput && correlativoInput.value.trim());
  const hasNombre = !!(nombreInput && nombreInput.value.trim());

  if (!hasStart && !hasEnd && !hasCorrelativo && !hasNombre) {
    event.preventDefault();
    if (startInput) {
      startInput.focus();
    }
  }
});
