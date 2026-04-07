(function (window, document, $) {
  function getTarget(trigger) {
    const selector = trigger.getAttribute("data-ui-target") || trigger.getAttribute("data-target");
    if (!selector) return null;
    return document.querySelector(selector);
  }

  function closeDropdowns(except) {
    document.querySelectorAll(".dropdown-menu.is-open, .app-dropdown-menu.is-open").forEach((menu) => {
      if (except && menu === except) return;
      menu.classList.remove("is-open", "show");
      const toggle = document.querySelector(`[aria-controls="${menu.id}"]`);
      if (toggle) toggle.setAttribute("aria-expanded", "false");
    });
  }

  function openModal(modal) {
    if (!modal) return;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("overflow-hidden");
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("overflow-hidden");
  }

  function toggleCollapse(target) {
    if (!target) return;
    const isOpen = !target.classList.contains("is-open");
    target.classList.toggle("is-open", isOpen);
    target.classList.toggle("show", isOpen);
    target.classList.toggle("hidden", !isOpen && !target.classList.contains("collapse"));
    target.hidden = !isOpen;
  }

  document.addEventListener("click", function (event) {
    const alertClose = event.target.closest('[data-ui-dismiss="alert"], [data-dismiss="alert"]');
    if (alertClose) {
      const alert = alertClose.closest(".alert");
      if (alert) alert.remove();
      return;
    }

    const modalClose = event.target.closest('[data-ui-dismiss="modal"], [data-dismiss="modal"]');
    if (modalClose) {
      closeModal(modalClose.closest(".modal"));
      return;
    }

    const collapseTrigger = event.target.closest('[data-ui-toggle="collapse"], [data-toggle="collapse"]');
    if (collapseTrigger) {
      event.preventDefault();
      toggleCollapse(getTarget(collapseTrigger));
      return;
    }

    const modalTrigger = event.target.closest('[data-ui-toggle="modal"], [data-toggle="modal"]');
    if (modalTrigger) {
      event.preventDefault();
      openModal(getTarget(modalTrigger));
      return;
    }

    const dropdownTrigger = event.target.closest('[data-ui-toggle="dropdown"], [data-toggle="dropdown"]');
    if (dropdownTrigger) {
      event.preventDefault();
      const menu = dropdownTrigger.parentElement.querySelector(".dropdown-menu, .app-dropdown-menu");
      if (!menu) return;
      const willOpen = !menu.classList.contains("is-open");
      closeDropdowns(menu);
      menu.classList.toggle("is-open", willOpen);
      menu.classList.toggle("show", willOpen);
      dropdownTrigger.setAttribute("aria-expanded", willOpen ? "true" : "false");
      return;
    }

    if (!event.target.closest(".app-nav-menu, .btn-group, .dropdown")) {
      closeDropdowns();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeDropdowns();
      document.querySelectorAll(".modal.is-open").forEach(closeModal);
    }
  });

  document.addEventListener("click", function (event) {
    if (event.target.classList.contains("modal")) {
      closeModal(event.target);
    }
  });

  window.AppUI = {
    openModal,
    closeModal,
    toggleCollapse,
  };

  if ($) {
    $.fn.modal = function (action) {
      return this.each(function () {
        if (action === "hide") closeModal(this);
        else openModal(this);
      });
    };

    $.fn.tooltip = function () {
      return this.each(function () {
        if (this.getAttribute("title") && !this.getAttribute("aria-label")) {
          this.setAttribute("aria-label", this.getAttribute("title"));
        }
      });
    };
  }
})(window, document, window.jQuery);
