# -*- coding: utf-8 -*-

from openerp import models, fields, api

import re


class product_template(models.Model):
    _inherit = 'product.template'

    loc_rack = fields.Char('Almacen')
    loc_row = fields.Char('Pasadizo')
    loc_case = fields.Char('Fila')



    @api.model
    def create(self, vals):
        # seq = self.env['ir.sequence'].next_by_code('einvoice.resumen.diario.secue')
        # vals['identificador'] = seq
        res = super(product_template, self).create(vals)
        new_object = self.env['product.template'].browse(res.id)
        codigo_ref_interna = 'ASF'+str(new_object.id).zfill(10)
        new_object.write({'default_code':codigo_ref_interna})

        return res


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def transeferir_directo(self):
        self.wkf_confirm_order()
        self.wkf_approve_order()
        self.action_picking_create()
        # self.picking_done()
        rt = self.view_picking()
        return rt

        # self.picking_ids.do_enter_transfer_details()
        # pass


# class purchase_por_categoria(models.Model):
#     _name = 'purchase.por.categoria'
#     _rec_name = 'name'
#     _auto = False
#
#     name = fields.Char()
