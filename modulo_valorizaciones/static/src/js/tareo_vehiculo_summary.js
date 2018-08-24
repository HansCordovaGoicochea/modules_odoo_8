 openerp.modulo_valorizaciones = function(openerp) {

    var _t = openerp.web._t;
    _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;

    // costos fijo widget
    openerp.modulo_valorizaciones.RoomSummary = openerp.web.form.FormWidget.extend(openerp.web.form.ReinitializeWidgetMixin, {

        display_name: _lt('Form'),
        view_type: "form",

        init: function() {
            this._super.apply(this, arguments);

           if(this.field_manager.model == "vehiculo.contrato.summary")
            {

                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }

            this.set({
                date_to: false,
                date_from: false,
                contrato: false,
                summary_header: false,
                room_summary: false,
            });
            this.summary_header = [];
            this.room_summary = [];
            this.field_manager.on("field_changed:date_from", this, function() {
                this.set({"date_from": openerp.web.str_to_date(this.field_manager.get_field_value("date_from"))});
            });
            this.field_manager.on("field_changed:date_to", this, function() {
                this.set({"date_to": openerp.web.str_to_date(this.field_manager.get_field_value("date_to"))});
            });
            this.field_manager.on("field_changed:contrato", this, function() {
                this.set({"contrato": this.field_manager.get_field_value("contrato")});
            });

            this.field_manager.on("field_changed:summary_header", this, function() {
                this.set({"summary_header": this.field_manager.get_field_value("summary_header")});
            });
            this.field_manager.on("field_changed:room_summary", this, function() {
                this.set({"room_summary":this.field_manager.get_field_value("room_summary")});
            });

        },

        initialize_field: function() {
            openerp.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_header", self, self.initialize_content);
            self.on("change:room_summary", self, self.initialize_content);
        },

      initialize_content: function() {
           var self = this;
           if (self.setting)
               return;

           if (!this.summary_header || !this.room_summary)
                return;
           // don't render anything until we have summary_header and room_summary

           this.destroy_content();

           if (this.get("summary_header")) {
            this.summary_header = py.eval(this.get("summary_header"));
           }
           if (this.get("room_summary")) {
            this.room_summary = py.eval(this.get("room_summary"));
           }

           this.renderElement();
           this.view_loading();
        },

        view_loading: function(r) {
            return this.load_form(r);
        },

        load_form: function(data) {
            self.action_manager = new openerp.web.ActionManager(self);

            // this.$el.find(".table_free").bind("click", function(event){
            //     self.action_manager.do_action({
            //             type: 'ir.actions.act_window',
            //             res_model: "quick.room.reservation",
            //             views: [[false, 'form']],
            //             target: 'new',
            //             context: {"room_id": $(this).attr("data"), 'date': $(this).attr("date")},
            //     });
            // });

        },

        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWeb.render("summaryDetails", {widget: this}));
        }
    });
    openerp.web.FormView.include({
         can_be_discarded: function() {

        if (this.$el.is('.oe_form_dirty')) {

            if (this.model === 'vehiculo.contrato.summary') {

                this.$el.removeClass('oe_form_dirty');
                return true;
            }
            if (!confirm(_t("Warning, the record has been modified, your changes will be discarded.\n\nAre you sure you want to leave this page ?"))) {
                return false;
            }
            this.$el.removeClass('oe_form_dirty');
        }
        return true;
    },
    });
    openerp.web.form.custom_widgets.add('Room_Reservation', 'openerp.modulo_valorizaciones.RoomSummary');

        // costos variables widget
    openerp.modulo_valorizaciones.RoomSummary_var = openerp.web.form.FormWidget.extend(openerp.web.form.ReinitializeWidgetMixin, {

        display_name: _lt('Form'),
        view_type: "form",

        init: function() {
            this._super.apply(this, arguments);

           if(this.field_manager.model == "vehiculo.contrato.summary")
            {

                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }
            this.set({
                date_to: false,
                date_from: false,
                contrato: false,
                summary_header_var: false,
                room_summary_var: false,
            });
            this.summary_header_var = [];
            this.room_summary_var = [];
            this.field_manager.on("field_changed:date_from", this, function() {
                this.set({"date_from": openerp.web.str_to_date(this.field_manager.get_field_value("date_from"))});
            });
            this.field_manager.on("field_changed:date_to", this, function() {
                this.set({"date_to": openerp.web.str_to_date(this.field_manager.get_field_value("date_to"))});
            });
            this.field_manager.on("field_changed:contrato", this, function() {
                this.set({"contrato": this.field_manager.get_field_value("contrato")});
            });

            this.field_manager.on("field_changed:summary_header_var", this, function() {
                this.set({"summary_header_var": this.field_manager.get_field_value("summary_header_var")});
            });
            this.field_manager.on("field_changed:room_summary_var", this, function() {
                this.set({"room_summary_var":this.field_manager.get_field_value("room_summary_var")});
            });

        },

        initialize_field: function() {
            openerp.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_header_var", self, self.initialize_content);
            self.on("change:room_summary_var", self, self.initialize_content);
        },

      initialize_content: function() {
           var self = this;
           if (self.setting)
               return;

           if (!this.summary_header_var || !this.room_summary_var)
                return;
           // don't render anything until we have summary_header and room_summary

           this.destroy_content();

           if (this.get("summary_header_var")) {
            this.summary_header_var = py.eval(this.get("summary_header_var"));
           }
           if (this.get("room_summary_var")) {
            this.room_summary_var = py.eval(this.get("room_summary_var"));
           }

           this.renderElement();
           this.view_loading();
        },

        view_loading: function(r) {
            return this.load_form(r);
        },

        load_form: function(data) {
            self.action_manager = new openerp.web.ActionManager(self);

            // this.$el.find(".table_free").bind("click", function(event){
            //     self.action_manager.do_action({
            //             type: 'ir.actions.act_window',
            //             res_model: "quick.room.reservation",
            //             views: [[false, 'form']],
            //             target: 'new',
            //             context: {"room_id": $(this).attr("data"), 'date': $(this).attr("date")},
            //     });
            // });

        },

        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWeb.render("summaryDetails_var", {widget: this}));
        }
    });
    openerp.web.form.custom_widgets.add('Room_Reservation_var', 'openerp.modulo_valorizaciones.RoomSummary_var');

    // costos adicionales widget
    openerp.modulo_valorizaciones.RoomSummary_adi = openerp.web.form.FormWidget.extend(openerp.web.form.ReinitializeWidgetMixin, {

        display_name: _lt('Form'),
        view_type: "form",

        init: function() {
            this._super.apply(this, arguments);

           if(this.field_manager.model == "vehiculo.contrato.summary")
            {

                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }
            this.set({
                date_to: false,
                date_from: false,
                contrato: false,
                summary_header_adi: false,
                room_summary_adi: false,
            });
            this.summary_header_adi = [];
            this.room_summary_adi = [];
            this.field_manager.on("field_changed:date_from", this, function() {
                this.set({"date_from": openerp.web.str_to_date(this.field_manager.get_field_value("date_from"))});
            });
            this.field_manager.on("field_changed:date_to", this, function() {
                this.set({"date_to": openerp.web.str_to_date(this.field_manager.get_field_value("date_to"))});
            });
            this.field_manager.on("field_changed:contrato", this, function() {
                this.set({"contrato": this.field_manager.get_field_value("contrato")});
            });

            this.field_manager.on("field_changed:summary_header_adi", this, function() {
                this.set({"summary_header_adi": this.field_manager.get_field_value("summary_header_adi")});
            });
            this.field_manager.on("field_changed:room_summary_adi", this, function() {
                this.set({"room_summary_adi":this.field_manager.get_field_value("room_summary_adi")});
            });

        },

        initialize_field: function() {
            openerp.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_header_adi", self, self.initialize_content);
            self.on("change:room_summary_adi", self, self.initialize_content);
        },

      initialize_content: function() {
           var self = this;
           if (self.setting)
               return;

           if (!this.summary_header_adi || !this.room_summary_adi)
                return;
           // don't render anything until we have summary_header and room_summary

           this.destroy_content();

           if (this.get("summary_header_adi")) {
            this.summary_header_adi = py.eval(this.get("summary_header_adi"));
           }
           if (this.get("room_summary_adi")) {
            this.room_summary_adi = py.eval(this.get("room_summary_adi"));
           }

           this.renderElement();
           this.view_loading();
        },

        view_loading: function(r) {
            return this.load_form(r);
        },

        load_form: function(data) {
            self.action_manager = new openerp.web.ActionManager(self);

            // this.$el.find(".table_free").bind("click", function(event){
            //     self.action_manager.do_action({
            //             type: 'ir.actions.act_window',
            //             res_model: "quick.room.reservation",
            //             views: [[false, 'form']],
            //             target: 'new',
            //             context: {"room_id": $(this).attr("data"), 'date': $(this).attr("date")},
            //     });
            // });

        },

        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWeb.render("summaryDetails_adi", {widget: this}));
        }
    });
    openerp.web.form.custom_widgets.add('Room_Reservation_adi', 'openerp.modulo_valorizaciones.RoomSummary_adi');


    // // ocultar botones de guardar y cancelar
    // openerp.modulo_valorizaciones.FormView = openerp.web.View.extend(openerp.web.form.FieldManagerMixin, {
    //     searchable: false,
    //     template: "FormView",
    //     display_name: _lt('Form'),
    //     view_type: "form",
    //
    //     init: function(parent, dataset, view_id, options) {
    //     var self = this;
    //     this._super(parent);
    //      console.log(this)
    // },
    //     view_loading: function(r) {
    //         return this.load_form(r);
    //     },
    //     ocultarbbb: function(source, options) {
    //         var self = this;
    //
    //         // if(this.get("actual_mode") !== "view" && ) {
    //         //    self.$buttons.find('.oe_form_buttons_edit').show();
    //         // }
    //     },
    // });


};

