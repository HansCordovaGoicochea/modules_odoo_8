openerp.vrcontadores = function (instance) {

    instance.web.list.columns.add('field.my_widget', 'instance.vrcontadores.my_widget');

    instance.vrcontadores.my_widget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = res;
            if (amount == 'Deudor'){
                return "<font color='#ff0000'>"+(amount)+"</font>";
            }else if (amount == 'Pagó'){
                return "<font color='#00ff00'>"+(amount)+"</font>";
            }else{
                return "<font color='#ffd700'>"+(amount)+"</font>";
            }
        }
    });

    instance.web.list.columns.add('field.estado', 'instance.vrcontadores.estado');

    instance.vrcontadores.estado = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = res;
            return "<font color='#00b050'>"+(amount)+"</font>";
        }
    });

    instance.web.list.columns.add('field.condicion', 'instance.vrcontadores.condicion');

    instance.vrcontadores.condicion = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = res;
            return "<font color='#cc6600'>"+(amount)+"</font>";
        }
    });

    instance.web.list.columns.add('field.declaracion', 'instance.vrcontadores.declaracion');

    instance.vrcontadores.declaracion = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = res;
            if (amount == 'Declarado desfasado'){
                return "<font color='#ff0000'>"+(amount)+"</font>";
            }else if (amount == 'Declarado a tiempo'){
                return "<font color='#00ff00'>"+(amount)+"</font>";
            }else{
                return "<font color='#ffd700'>"+(amount)+"</font>";
            }
        }
    });

    instance.web.list.columns.add('field.impuestos', 'instance.vrcontadores.impuestos');

    instance.vrcontadores.impuestos = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = res;
            if (amount == 'No Deuda'){
                return "<font color='#00ff00'>"+(amount)+"</font>";
            }else{
                return "<font color='#ff0000'>"+(amount)+"</font>";
            }
        }
    });

    instance.web.list.columns.add('field.documentos', 'instance.vrcontadores.documentos');
    instance.vrcontadores.documentos = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = res;
            if (amount == 'Pendiente'){
                return "<font color='#ff0000'>"+(amount)+"</font>";
            }else if (amount == 'Recibido'){
                return "<font color='#00ff00'>"+(amount)+"</font>";
            }else{
                return "<font color='#ffd700'>"+(amount)+"</font>";
            }
        }
    });
    //alert(instance.vrcontadores.documentos);

    // $('.your-Class').click(function(){
    //  alert('sssss');
    // });
//     alert('dfdfd');
// var calenderView = require('web_calendar.CalendarView');
//     calenderView.include({
//     open_quick_create: function(){
//     if (this.model != 'vrcontadores') {
//         this._super();
//     }
// }
// });

//
// openerp.define('vrcontadores.vrcontadores', function (require) {
// "use strict";
//
// });


};