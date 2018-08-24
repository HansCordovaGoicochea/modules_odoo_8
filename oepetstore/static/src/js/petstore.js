openerp.oepetstore = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.WidgetCoordinates = instance.web.form.FormWidget.extend({
         events: {
                'click button': function () {
                    navigator.geolocation.getCurrentPosition(
                        this.proxy('received_position'));
                }
            },
        start: function() {
            var sup = this._super();
            this.field_manager.on("field_changed:provider_latitude", this, this.display_map);
            this.field_manager.on("field_changed:provider_longitude", this, this.display_map);
            this.on("change:effective_readonly", this, this.display_map);
            this.display_map();
            return sup;
        },
        display_map: function() {
            this.$el.html(QWeb.render("WidgetCoordinates", {
                "latitude": this.field_manager.get_field_value("provider_latitude") || 0,
                "longitude": this.field_manager.get_field_value("provider_longitude") || 0,
            }));
        },
        received_position: function(obj) {
            this.field_manager.set_values({
                "provider_latitude": obj.coords.latitude,
                "provider_longitude": obj.coords.longitude,
        });
    },
    });

    instance.web.form.custom_widgets.add('coordinates', 'instance.oepetstore.WidgetCoordinates');
}