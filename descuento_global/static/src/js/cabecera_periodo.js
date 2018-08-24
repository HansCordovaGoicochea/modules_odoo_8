 openerp.descuento_global = function(openerp) {

     var instance = openerp;
     var _t = instance.web._t,
         _lt = instance.web._lt;
     var QWeb = instance.web.qweb;

     instance.web.descuento_global = instance.web.descuento_global || {};

     instance.web.views.add('tree_cabecera_meses_fc_quickadd', 'instance.web.descuento_global.QuickAddListView');
     instance.web.descuento_global.QuickAddListView = instance.web.ListView.extend({
         init: function () {
                this._super.apply(this, arguments);
                this.periods = [];
                this.current_period = null;
                this.default_period = null;


         },
         start: function () {
             var tmp = this._super.apply(this, arguments);
             var self = this;
             var defs = [];
             this.$el.parent().prepend(QWeb.render("CabeceraMesesFCQuickAdd", {widget: this}));

             this.$el.parent().find('.oe_descuento_global_select_period').change(function () {
                    self.current_period = this.value === '' ? null : parseInt(this.value);
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
             });
              this.on('edit:after', this, function () {
                self.$el.parent().find('.oe_descuento_global_select_period').attr('disabled', 'disabled');
            });
            this.on('save:after cancel:after', this, function () {
                self.$el.parent().find('.oe_descuento_global_select_period').removeAttr('disabled');
            });
            var mod = new instance.web.Model("account.invoice", self.dataset.context, self.dataset.domain);
            defs.push(mod.call("default_get", [['period_id'],self.dataset.context]).then(function(result) {
                self.current_period = result['period_id'];
            }));
            defs.push(mod.call("list_periods", []).then(function(result) {
                self.periods = result;
            }));

             return $.when(tmp, defs);
         },
         do_search: function (domain, context, group_by) {
                var self = this;
                this.last_domain = domain;
                this.last_context = context;
                this.last_group_by = group_by;
                this.old_search = _.bind(this._super, this);
                var o;

            self.$el.parent().find('.oe_descuento_global_select_period').children().remove().end();
            self.$el.parent().find('.oe_descuento_global_select_period').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i][1], self.periods[i][0]);
                self.$el.parent().find('.oe_descuento_global_select_period').append(o);
            }
            self.$el.parent().find('.oe_descuento_global_select_period').val(self.current_period).attr('selected',true);
            return self.search_by_journal_period();
         },

       search_by_journal_period: function() {
            var self = this;
            var domain = [];
            if (self.current_period !== null) domain.push(["period_id", "=", self.current_period]);
            if (self.current_period === null) delete self.last_context["period_id"];
            else self.last_context["period_id"] =  self.current_period;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },
     });
 };