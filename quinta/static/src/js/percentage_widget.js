openerp.web_percentage_widget = function(instance) {
    // list view
    instance.web.list.columns.add('field.percentage', 'instance.web.list.percentage');
    instance.web.list.percentage = instance.web.list.Column.extend({
        /**
         * Return a percentage format value
         *
         * @private
         */
        _format: function (row_data, options) {
            var _value = parseFloat(row_data[this.id].value);
            if (isNaN(_value)) {
                return null;
            }
            return (_value*100).toFixed(2) + '%';
        }
    });
};
