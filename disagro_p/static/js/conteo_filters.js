const cssEscape = (value) => {
  if (window.CSS && CSS.escape) {
    return CSS.escape(value);
  }
  return value.replace(/([\.\#\[\]\(\)\{\}\+\*\^\$\:\?\!\|\=\,\s])/g, '\\$1');
};

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('conteoFilterForm');
  if (!form) {
    return;
  }

  const sections = Array.from(form.querySelectorAll('[data-filter-group]'));

  const submitForm = () => {
    form.submit();
  };

  const ensureRequiredSelection = (section, changedCheckbox) => {
    if (section.dataset.required !== 'true') {
      return true;
    }
    const checkboxes = Array.from(section.querySelectorAll('input[type="checkbox"]'));
    const checked = checkboxes.filter((cb) => cb.checked);
    if (checked.length === 0) {
      changedCheckbox.checked = true;
      changedCheckbox.focus();
      return false;
    }
    return true;
  };

  const updateChipsForGroup = (group) => {
    const section = form.querySelector(`[data-filter-group="${group}"]`);
    const chipsContainer = form.querySelector(`[data-chip-group="${group}"]`);
    if (!section || !chipsContainer) {
      return;
    }
    const checkboxes = Array.from(section.querySelectorAll('input[type="checkbox"]'));
    const selected = checkboxes.filter((cb) => cb.checked);
    const defaultChip = chipsContainer.querySelector('[data-default-chip]');

    chipsContainer.querySelectorAll('.chip[data-chip-value]').forEach((chip) => chip.remove());

    if (defaultChip) {
      if (group === 'captadores') {
        const actual = checkboxes.filter((cb) => cb.value !== 'SIN_CAPTADOR');
        const allActualChecked = actual.length > 0 && actual.every((cb) => cb.checked);
        const sinChecked = checkboxes.find((cb) => cb.value === 'SIN_CAPTADOR')?.checked;
        defaultChip.hidden = !(allActualChecked && !sinChecked);
      } else {
        defaultChip.hidden = selected.length > 0;
      }
    }

    selected.forEach((checkbox) => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.dataset.chipValue = checkbox.value;
      chip.innerHTML = `${checkbox.dataset.label || checkbox.value}<button type="button" class="chip-remove" aria-label="Quitar" data-chip-remove>&times;</button>`;
      chipsContainer.appendChild(chip);
    });
  };

  sections.forEach((section) => {
    const group = section.dataset.filterGroup;
    updateChipsForGroup(group);

    const checkboxes = section.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener('change', (event) => {
        if (!ensureRequiredSelection(section, event.target)) {
          return;
        }
        updateChipsForGroup(group);
      });
    });
  });

  form.querySelectorAll('[data-filter-action]').forEach((button) => {
    const target = button.getAttribute('data-filter-target');
    const action = button.getAttribute('data-filter-action');
    const section = form.querySelector(`[data-filter-group="${target}"]`);
    if (!section) {
      return;
    }

    button.addEventListener('click', () => {
      const checkboxes = Array.from(section.querySelectorAll('input[type="checkbox"]'));

      if (action === 'select-all') {
        checkboxes.forEach((checkbox) => {
          checkbox.checked = true;
        });
      } else if (action === 'clear') {
        checkboxes.forEach((checkbox) => {
          checkbox.checked = false;
        });
      } else if (action === 'reset') {
        checkboxes.forEach((checkbox) => {
          checkbox.checked = checkbox.value !== 'SIN_CAPTADOR';
        });
      }

      if (section.dataset.required === 'true' && !checkboxes.some((cb) => cb.checked)) {
        if (checkboxes[0]) {
          checkboxes[0].checked = true;
        }
      }

      updateChipsForGroup(target);
    });
  });

  form.querySelectorAll('[data-chip-group]').forEach((container) => {
    container.addEventListener('click', (event) => {
      const removeButton = event.target.closest('[data-chip-remove]');
      if (!removeButton) {
        return;
      }
      const chip = removeButton.closest('.chip');
      if (!chip) {
        return;
      }
      const value = chip.dataset.chipValue;
      const group = container.getAttribute('data-chip-group');
      const section = form.querySelector(`[data-filter-group="${group}"]`);
      if (!section) {
        return;
      }
      const checkbox = section.querySelector(`input[value="${cssEscape(value)}"]`);
      if (!checkbox) {
        return;
      }
      checkbox.checked = false;
      if (section.dataset.required === 'true') {
        const remaining = Array.from(section.querySelectorAll('input[type="checkbox"]')).some((cb) => cb.checked);
        if (!remaining) {
          checkbox.checked = true;
          return;
        }
      }
      updateChipsForGroup(group);
      submitForm();
    });
  });

  const resetButton = form.querySelector('[data-filter-reset]');
  if (resetButton) {
    resetButton.addEventListener('click', () => {
      sections.forEach((section) => {
        const checkboxes = Array.from(section.querySelectorAll('input[type="checkbox"]'));
        if (section.dataset.filterGroup === 'captadores') {
          checkboxes.forEach((checkbox) => {
            checkbox.checked = checkbox.value !== 'SIN_CAPTADOR';
          });
        } else {
          checkboxes.forEach((checkbox) => {
            checkbox.checked = false;
          });
        }
        updateChipsForGroup(section.dataset.filterGroup);
      });
      submitForm();
    });
  }

  form.addEventListener('submit', (event) => {
    const requiredSection = sections.find((section) => section.dataset.required === 'true');
    if (!requiredSection) {
      return;
    }
    const hasSelection = Array.from(requiredSection.querySelectorAll('input[type="checkbox"]')).some((checkbox) => checkbox.checked);
    if (!hasSelection) {
      event.preventDefault();
      const first = requiredSection.querySelector('input[type="checkbox"]');
      if (first) {
        first.focus();
      }
    }
  });
});
