function openerp_field_mask_widgets(instance) {
        instance.web.form.FieldMask = instance.web.form.FieldDate.extend({
        // template : "FieldMask",

        render_value: function() {

            var show_value = this.get_value();
        	var field = this;

        	if (!field.get("effective_readonly")) {

                field.$el.find('input').val(this.format_client(show_value));

                var mask = field.node.attrs.mask;

                field.$el.find('input').datepicker({
                  dateFormat: 'dd/mm/yy',
                  changeMonth: true,
                  changeYear: true
                }).inputmask(mask);

        	} else {
                this.$el.text(this.format_client(show_value));
        	}
        },


        get_value: function() {

            try {
                var val = this.get('value');
              // alert(instance.web.parse_value(val === "" ? null : val, {'widget': 'date'}));
                return instance.web.parse_value(val === "" ? null : val, {'widget': 'date'});
            } catch (e) {
                return "";
            }

        },

        format_client: function(v) {
            return instance.web.format_value(v, {"widget": "date"});
        },

    });

    instance.web.form.widgets.add('mask', 'instance.web.form.FieldMask');
}

openerp.field_mask = function(openerp) {
    openerp.field_mask = openerp.field_mask || {};
    openerp_field_mask_widgets(openerp);
}

