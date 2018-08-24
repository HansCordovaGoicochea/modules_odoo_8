/*jshint plusplus: true */
/*jshint nomen: false */
/*jshint node: true */

function openerp_merge_lines(instance, module){
    // Setting Use strict
    "use strict";
    
    module.MergeLinesPosModel = module.PosModel;
    module.PosModel = module.MergeLinesPosModel.extend({
        scan_product: function(parsed_code){
            var self = this;
            var selectedOrder = this.get('selectedOrder');
            if(parsed_code.encoding === 'ean13'){
                var product = this.db.get_product_by_ean13(parsed_code.base_code);
            }else if(parsed_code.encoding === 'reference'){
                var product = this.db.get_product_by_reference(parsed_code.code);
            }

            if(!product){
                return false;
            }
            
            if(parsed_code.type === 'weight'){
                selectedOrder.addProduct(product, {quantity:parsed_code.value, merge:true});
            }else {
                module.MergeLinesPosModel.prototype.scan_product.call(self, parsed_code);
            }
            return true;
        },
    });
    
    module.MergeLinesOrder = module.Order;
    module.Order = module.MergeLinesOrder.extend({
        addProduct: function(product, options){
            var attr = JSON.parse(JSON.stringify(product));
            var self = this;
            var added = false;
            options = options || {};
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});

            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }

            // comparar las lineas de pedido del POS y poder sumar a la que quedo
            // TODO: PARA QUE NO DUPLIQUE LINEAS DE PEDIDO
            if(self.get('orderLines').at(self.get('orderLines').length -1)) {
                self.get('orderLines').each(function(orderline){
                    if(orderline && orderline.can_be_merged_with(line) && options.merge !== false) {
                        // alert(orderline);
                        // alert(orderline.can_be_merged_with(line));
                        // alert(options.merge);
                        orderline.merge(line);
                        added = true;
                        self.selectLine(orderline);
                        return;
                    }
                });
            }
            if(added){return;}
            this.get('orderLines').add(line);
            this.selectLine(this.getLastOrderline());
            
            // Added compatibility with pos_customer_display module from akretion
            // that can be found on https://code.launchpad.net/~akretion-team/openerp-pos/201407-pos-code-sprint
            if (this.pos.config.iface_customer_display == true){
                this.pos.prepare_text_customer_display('addProduct', {'product' : product, 'options' : options});
            }
        },
    });
    
    module.MergeLinesOrderline = module.Orderline;
    module.Orderline = module.MergeLinesOrderline.extend({
        // when we add an new orderline we want to merge it with other lines to see reduce the number of items
        // in the orderline. This returns true if it makes sense to merge the two
        // TODO: this function overrides default point of sale behavior on Odoo that
        // prevents merge items in other units than pieces 
        can_be_merged_with: function(orderline){
            if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
                return false;
            }else if(this.get_product_type() !== orderline.get_product_type()){
                return false;
            }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
                return false;
            }else if(this.price !== orderline.price){
                return false;
            }else{
                return true;
            }
        },        
    });
}