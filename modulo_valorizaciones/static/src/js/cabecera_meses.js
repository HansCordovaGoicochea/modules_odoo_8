(function() {
    var instance = openerp;
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.modulo_valorizaciones = instance.web.modulo_valorizaciones || {};

    instance.web.views.add('tree_cabecera_meses_quickadd', 'instance.web.modulo_valorizaciones.QuickAddListView');
    instance.web.modulo_valorizaciones.QuickAddListView = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.current_anio = [];
            this.meses = [];
            this.default_mes = null;
            this.current_mes = null;


        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("CabeceraMesesQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_modulo_valorizaciones_select_period').change(function() {
                self.current_anio = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.$el.parent().find('input[name=oe_modulo_valorizaciones_check]').change(function() {

                if (parseInt(self.current_mes) === parseInt(this.value)) {
                    self.current_mes = null;
                }
                // alert(parseInt(this.value));
                // self.current_mes = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });

            var mod = new instance.web.Model("modulo_valorizaciones.tareo_mensual", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [[],self.dataset.context]).then(function(result) {

                self.current_anio = result['anio_actual'];
                self.current_mes = result['mes_actual'];

                // var table = self.$el.find('.oe_list_content').html();
                // alert(table);
                        // var $fixedColumn = table.clone().insertBefore(table).addClass('fixed-column');
                        //
                        // $fixedColumn.$el.find('th:not(:first-child),td:not(:first-child)').remove();
                        //
                        // $fixedColumn.$el.find('tr').each(function (i, elem) {
                        //     $(this).height($table.find('tr:eq(' + i + ')').height());
                        // });
            }));

            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;


            self.$el.parent().find('.oe_modulo_valorizaciones_select_period').text(self.current_anio);
      // alert(self.current_mes);

            self.$el.parent().find('input[name=oe_modulo_valorizaciones_check]').each(function(ind, elem){
         // alert($(elem).val());

                if (parseInt($(elem).val()) === parseInt(self.current_mes)){
                    $(elem).prop( "checked", true );
                }

            });

            return self.search_by_journal_period();
        },

         search_by_journal_period: function() {
            var self = this;
            var domain = [];
            var array_checks = [];
            self.$el.parent().find('input[name=oe_modulo_valorizaciones_check]:checked').each(function(ind, elem){
                array_checks.push($(elem).val());
            });



            if (array_checks !== null) domain.push(["date_month", "in", array_checks]);
            // if (array_checks !== null) domain.push(["EXTRACT('month' from fechaFacturacion)", "in", array_checks]);

            // alert(domain);
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();

            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });

    // valorizacion proveedor
    instance.web.views.add('tree_cabecera_meses_quickadd_proveedor', 'instance.web.modulo_valorizaciones.QuickAddListView1');
    instance.web.modulo_valorizaciones.QuickAddListView1 = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.current_anio = [];
            this.meses = [];
            this.default_mes = null;
            this.current_mes = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            this.$el.parent().prepend(QWeb.render("CabeceraMesesQuickAdd", {widget: this}));

            this.$el.parent().find('.oe_modulo_valorizaciones_select_period').change(function() {
                self.current_anio = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            this.$el.parent().find('input[name=oe_modulo_valorizaciones_check]').change(function() {

                if (parseInt(self.current_mes) === parseInt(this.value)) {
                    self.current_mes = null;
                }
                // alert(parseInt(this.value));
                // self.current_mes = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });

            var mod = new instance.web.Model("modulo_valorizaciones.proveedor", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [[],self.dataset.context]).then(function(result) {

                self.current_anio = result['anio_actual'];
                self.current_mes = result['mes_actual'];
            }));

            return $.when(tmp, defs);
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;


            self.$el.parent().find('.oe_modulo_valorizaciones_select_period').text(self.current_anio);
      // alert(self.current_mes);

            self.$el.parent().find('input[name=oe_modulo_valorizaciones_check]').each(function(ind, elem){
         // alert($(elem).val());

                if (parseInt($(elem).val()) === parseInt(self.current_mes)){
                    $(elem).prop( "checked", true );
                }

            });


            return self.search_by_journal_period();
        },

         search_by_journal_period: function() {
            var self = this;
            var domain = [];
            var array_checks = [];
            self.$el.parent().find('input[name=oe_modulo_valorizaciones_check]:checked').each(function(ind, elem){
                array_checks.push($(elem).val());
            });

            if (array_checks !== null) domain.push(["date_month", "in", array_checks]);
            // if (array_checks !== null) domain.push(["EXTRACT('month' from fechaFacturacion)", "in", array_checks]);

            // alert(domain);
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();

            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
    });

    // otrossssssss

    instance.web.views.add('tree_sin_botones_quickadd', 'instance.web.modulo_valorizaciones.QuickAddListView2');
    instance.web.modulo_valorizaciones.QuickAddListView2 = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            // console.log(this);
            // console.log(this.model);
            if(this.model === "fleet.documento.vehiculo")
            {

                $(".oe_view_manager_buttons").hide();
                // $(".oe_view_manager_header").hide();
            }
        },
    });
})();