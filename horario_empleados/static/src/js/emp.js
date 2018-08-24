 openerp.horario_empleados = function (instance) {
        instance.web.list.columns.add('field.coloreando', 'instance.horario_empleados.coloreando');

    instance.horario_empleados.coloreando = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            alert(res);
            var hora_entrada = parseFloat(res);

            var ho = hora_entrada - 0.16666666666667;
            // alert(ho);
            if (hora_entrada == 0) {
                return "<font color='#ff0000' size=6 >" + (hora_entrada) + "</font>";
            }
            return res
        }

    });
    // alert(instance.horario_empleados.coloreando);
    //       alert(res);
    //
    //here you can add more widgets if you need, as above...
    //
      instance.web.list.columns.add('field.coloreando_entrada2', 'instance.horario_empleados.coloreando_entrada2');
    instance.horario_empleados.coloreando_entrada2 = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            // alert(res);
            var segunda_hora_entrada = parseFloat(res);
            if (segunda_hora_entrada > 0) {
                return "<font color='#0066ff' size=6>" + (segunda_hora_entrada) + "</font>";
            }
            return res
        }
    });
};