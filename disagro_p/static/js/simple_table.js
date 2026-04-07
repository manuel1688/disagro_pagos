(function (window, document, $) {
  if (!$) return;

  function compareValues(a, b) {
    const aNum = Number(a);
    const bNum = Number(b);
    if (!Number.isNaN(aNum) && !Number.isNaN(bNum)) return aNum - bNum;
    return String(a).localeCompare(String(b), "es", { numeric: true, sensitivity: "base" });
  }

  function SimpleDataTable($table, options) {
    this.$table = $table;
    this.options = $.extend(
      true,
      {
        paging: true,
        pageLength: 10,
        searching: true,
        ordering: true,
        order: [],
        language: {
          search: "Buscar",
          emptyTable: "No hay resultados.",
          previous: "Anterior",
          next: "Siguiente",
        },
      },
      options || {}
    );
    this.state = {
      page: 1,
      search: "",
      order: this.options.order[0] || null,
    };
    this.$tbody = this.$table.find("tbody").first();
    this.placeholder = null;
    this.$rows = this.$tbody.find("tr");
    this.setup();
    this.render();
  }

  SimpleDataTable.prototype.setup = function () {
    if (!this.$table.parent().hasClass("simple-table-shell")) {
      this.$table.wrap('<div class="simple-table-shell overflow-x-auto"></div>');
    }

    this.$shell = this.$table.parent();
    this.$controls = $('<div class="table-actions"></div>');
    this.$info = $('<div class="text-sm text-slate-500"></div>');
    this.$pager = $('<div class="table-pagination"></div>');

    if (this.options.searching) {
      this.$search = $('<input type="search" class="form-control table-search" />');
      this.$search.attr("placeholder", this.options.language.search || "Buscar");
      this.$search.on("input", () => {
        this.state.search = this.$search.val().toLowerCase();
        this.state.page = 1;
        this.render();
      });
      this.$controls.append(this.$search);
    } else {
      this.$controls.append('<div></div>');
    }

    this.$controls.append(this.$pager);
    this.$shell.before(this.$controls);
    this.$shell.after(this.$info);

    if (this.options.ordering) {
      this.$table.find("thead th").each((index, cell) => {
        $(cell).css("cursor", "pointer").on("click", () => {
          if (!this.state.order || this.state.order[0] !== index) {
            this.state.order = [index, "asc"];
          } else {
            this.state.order = [index, this.state.order[1] === "asc" ? "desc" : "asc"];
          }
          this.render();
        });
      });
    }
  };

  SimpleDataTable.prototype.getRows = function () {
    let rows = this.$tbody.find("tr").toArray();
    if (this.placeholder) {
      rows = rows.filter((row) => row !== this.placeholder);
    }

    if (this.state.search) {
      rows = rows.filter((row) => $(row).text().toLowerCase().includes(this.state.search));
    }

    if (this.options.ordering && this.state.order) {
      const column = this.state.order[0];
      const direction = this.state.order[1] === "desc" ? -1 : 1;
      rows = rows.slice().sort((rowA, rowB) => {
        const a = $(rowA).children().eq(column).text().trim();
        const b = $(rowB).children().eq(column).text().trim();
        return compareValues(a, b) * direction;
      });
    }

    return rows;
  };

  SimpleDataTable.prototype.render = function () {
    const rows = this.getRows();
    const total = rows.length;
    const pageLength = Number(this.options.pageLength) || 10;
    const pageCount = this.options.paging ? Math.max(1, Math.ceil(total / pageLength)) : 1;

    if (this.state.page > pageCount) this.state.page = pageCount;

    this.$tbody.children().detach();

    if (total === 0) {
      const colspan = this.$table.find("thead th").length || 1;
      this.placeholder = document.createElement("tr");
      this.placeholder.innerHTML = `<td class="table-empty" colspan="${colspan}">${this.options.language.emptyTable}</td>`;
      this.$tbody.append(this.placeholder);
    } else {
      const start = this.options.paging ? (this.state.page - 1) * pageLength : 0;
      const end = this.options.paging ? start + pageLength : total;
      rows.slice(start, end).forEach((row) => this.$tbody.append(row));
      this.placeholder = null;
    }

    this.$pager.empty();

    if (this.options.paging) {
      const $prev = $('<button type="button" class="table-page-btn"></button>')
        .text(this.options.language.previous || "Anterior")
        .prop("disabled", this.state.page <= 1)
        .on("click", () => {
          this.state.page -= 1;
          this.render();
        });

      const $next = $('<button type="button" class="table-page-btn"></button>')
        .text(this.options.language.next || "Siguiente")
        .prop("disabled", this.state.page >= pageCount)
        .on("click", () => {
          this.state.page += 1;
          this.render();
        });

      const $page = $(`<span class="text-xs font-semibold text-slate-500">Página ${this.state.page} de ${pageCount}</span>`);
      this.$pager.append($prev, $page, $next);
    }

    if (total === 0) {
      this.$info.text(this.options.language.emptyTable);
    } else if (this.options.paging) {
      const start = (this.state.page - 1) * pageLength + 1;
      const end = Math.min(this.state.page * pageLength, total);
      this.$info.text(`Mostrando ${start}-${end} de ${total} registros`);
    } else {
      this.$info.text(`Mostrando ${total} registros`);
    }

    if (typeof this.options.drawCallback === "function") {
      this.options.drawCallback({});
    }
  };

  SimpleDataTable.prototype.destroy = function () {
    this.$controls.remove();
    this.$info.remove();
    if (this.placeholder) {
      $(this.placeholder).remove();
      this.placeholder = null;
    }
    this.$table.removeData("simpleDataTable");
  };

  $.fn.DataTable = function (options) {
    if (!this.length) return null;

    const instance = this.first().data("simpleDataTable");
    if (instance) {
      if (typeof options === "string" && typeof instance[options] === "function") {
        instance[options]();
      }
      return instance;
    }

    const table = new SimpleDataTable(this.first(), options);
    this.first().data("simpleDataTable", table);
    return table;
  };

  $.fn.dataTable = $.fn.dataTable || {};
  $.fn.dataTable.version = "simple";
})(window, document, window.jQuery);
