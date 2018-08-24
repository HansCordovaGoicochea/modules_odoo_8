# -*- coding: utf-8 -*-
import pytz
import requests
from openerp import fields, models, api, _, SUPERUSER_ID, tools
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning
# from openerp.exceptions import UserError
import logging
import calendar
import time
import datetime
from datetime import date, timedelta
# from datetime import datetime as dt
import os
from lxml import etree
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class fleet_compra_vehiculos(models.Model):

    def _get_leasing(self):
        domain = [('name', '=', 'Leasing'),('category', '=', 'compra')]
        leasing_def = self.env['fleet.service.type'].search(domain, limit=1)
        return leasing_def.id and leasing_def[0] or False

    def _get_incluye_tax(self):
        domain = [('price_include', '=', True),('type_tax_use', '=', 'purchase'),('active', '=', True),('type', '=', 'percent')]
        igv_def = self.env['account.tax'].search(domain, limit=1)
        return igv_def.id and igv_def[0] or False

    _name = 'fleet.compra.vehiculos'
    _rec_name = 'vehicle_id'
    _description = 'Compra de Vehiculos'

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehículo", required=True, )
    cost_subtype_id = fields.Many2one(comodel_name="fleet.service.type", string="Tipo de Compra", required=True, default=_get_leasing)
    contado_true = fields.Boolean(string="", compute='_check_reason_code_check', store=True)
    importe_costo = fields.Float(string="Importe de Costo",  required=True, digits=(50, 2))
    frecuencia_pagos = fields.Selection(string="Frec. de Pagos", selection=[('quincenal', 'Quincenal'), ('mensual', 'Mensual'), ('semanal', 'Semanal'), ('diario', 'Diario')], default='mensual')
    partner_id = fields.Many2one(comodel_name="res.partner", string="Proveedor",)
    bank = fields.Many2one(comodel_name="res.bank", string="Banco",)
    fecha_inicio = fields.Date(string="Fecha Inicio", required=True, )
    fecha_fin = fields.Date(string="Fecha Fin", required=False, )
    nro_meses = fields.Integer(string="Nro Meses", required=False, )
    ver_boton = fields.Boolean(string="",)
    product_id = fields.Many2one(comodel_name="product.product", string="Producto", required=True, )
    tax_id = fields.Many2one(comodel_name="account.tax", string="impuesto", default=_get_incluye_tax)
    estado_pago = fields.Selection(string="Estado", selection=[('pendiente', 'Pendiente'), ('factura', 'Facturado'), ],
                                   required=False, default='pendiente')
    currency_id = fields.Many2one('res.currency', 'Tipo Moneda', default=165)
    compra_ids = fields.One2many(comodel_name="fleet.compra.vehiculo.detalle", inverse_name="compra_id", string="Compra detalle", required=False, )

    @api.onchange('nro_meses')
    def _onchange_nro_meses(self):
        if self.fecha_inicio:
            fin = (datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')) + relativedelta(months=int(self.nro_meses))
            self.fecha_fin = fin

    @api.depends('cost_subtype_id')
    def _check_reason_code_check(self):
        if self.cost_subtype_id.name == 'Al Contado':
            self.contado_true = True
        else:
            self.contado_true = False

    @api.multi
    def generar_pagos(self):
        compra_ids = []
        if self.importe_costo and self.frecuencia_pagos:
            if self.frecuencia_pagos == 'mensual' and self.fecha_inicio and self.fecha_fin:
                ds = datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
                while ds.strftime('%Y-%m-%d') < self.fecha_fin:
                    de = ds + relativedelta(months=1)
                    if de.strftime('%Y-%m-%d') > self.fecha_fin:
                        de = datetime.datetime.strptime(self.fecha_fin, '%Y-%m-%d')

                    compra_ids.append((0, 0, {
                        'fecha_pago': de.strftime('%Y-%m-%d'),
                        'importe_costo': self.importe_costo,
                        'vehicle_id': self.vehicle_id,
                        'estado_pago': 'pendiente',
                        'product_id': self.product_id
                    }))

                    ds = ds + relativedelta(months=1)
                print (compra_ids)
                # delete = "DELETE FROM fleet_compra_vehiculo_detalle"
                # self._cr.execute(delete)
                if not self.ver_boton:
                    self.compra_ids = compra_ids
            elif self.frecuencia_pagos == 'quincenal' and self.fecha_inicio and self.fecha_fin:
                ds = datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
                while ds.strftime('%Y-%m-%d') < self.fecha_fin:
                    fecha_penultima = ds - timedelta(days=1)
                    de = ds + timedelta(days=14)

                    if de.strftime('%Y-%m-%d') > self.fecha_fin:
                        de = datetime.datetime.strptime(self.fecha_fin, '%Y-%m-%d')
                    else:
                        compra_ids.append((0, 0, {
                            'fecha_pago': de.strftime('%Y-%m-%d'),
                            'importe_costo': self.importe_costo,
                            'vehicle_id': self.vehicle_id,
                            'estado_pago': 'pendiente',
                            'product_id': self.product_id
                        }))
                    ds = ds + timedelta(days=15)
                print (compra_ids)
                # delete = "DELETE FROM fleet_compra_vehiculo_detalle"
                # self._cr.execute(delete)
                if not self.ver_boton:
                    self.compra_ids = compra_ids

            elif self.frecuencia_pagos == 'semanal' and self.fecha_inicio and self.fecha_fin:
                ds = datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
                while ds.strftime('%Y-%m-%d') < self.fecha_fin:
                    de = ds + relativedelta(weeks=1)
                    if de.strftime('%Y-%m-%d') > self.fecha_fin:
                        de = datetime.datetime.strptime(self.fecha_fin, '%Y-%m-%d')
                    else:
                        compra_ids.append((0, 0, {
                            'fecha_pago': de.strftime('%Y-%m-%d'),
                            'importe_costo': self.importe_costo,
                            'vehicle_id': self.vehicle_id,
                            'estado_pago': 'pendiente',
                            'product_id': self.product_id
                        }))

                    ds = ds + relativedelta(weeks=1)
                print (compra_ids)
                # delete = "DELETE FROM fleet_compra_vehiculo_detalle"
                # self._cr.execute(delete)
                if not self.ver_boton:
                    self.compra_ids = compra_ids
            elif self.frecuencia_pagos == 'diario' and self.fecha_inicio and self.fecha_fin:
                ds = datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
                while ds.strftime('%Y-%m-%d') < self.fecha_fin:
                    de = ds + timedelta(days=1)
                    if de.strftime('%Y-%m-%d') > self.fecha_fin:
                        de = datetime.datetime.strptime(self.fecha_fin, '%Y-%m-%d')

                    compra_ids.append((0, 0, {
                        'fecha_pago': de.strftime('%Y-%m-%d'),
                        'importe_costo': self.importe_costo,
                        'vehicle_id': self.vehicle_id,
                        'estado_pago': 'pendiente',
                        'product_id': self.product_id
                    }))

                    ds = ds + timedelta(days=1)
                print (compra_ids)
                # delete = "DELETE FROM fleet_compra_vehiculo_detalle"
                # self._cr.execute(delete)
                if not self.ver_boton:
                    self.compra_ids = compra_ids
            self.ver_boton = True

    @api.multi
    def llevar_datos_factura(self, context=None):
        journal_id = self.env['account.journal'].search([('code', '=', 'DPL')])
        account_id = self.env['account.account'].search([('code', '=', '121100')])
        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('account', 'invoice_supplier_form')
        res_id = res and res[1] or False

        for fac in self:
            print fac

            vals = \
                {'partner_id': fac.partner_id.id,
                 'date_invoice': fac.fecha_inicio,
                 'date_due': fac.fecha_inicio,
                 'origin': 'Compra - ' + str(fac.vehicle_id.name),
                 'account_id': account_id.id,
                 'journal_id': journal_id.id,
                 'currency_id': fac.currency_id.id,
                 'type': 'in_invoice',
                 'tipo_factura': 2,
                 'invoice_line': [(0, 0, {'product_id': fac.product_id.id,
                                          'name': fac.product_id.name_template,
                                          'account_id': fac.product_id.property_account_expense.id,
                                          'uos_id': fac.product_id.uom_id.id,
                                          'price_unit': fac.importe_costo,
                                          'invoice_line_tax_id': [(6, 0, [x.id for x in fac.tax_id])]})],
                 # 'tax_line': self._refund_cleanup_lines(invoice.invoice_line)
                 }

            ultimo_id = self.env['account.invoice'].create(vals)

            ctx = dict(
                type='in_invoice',
                default_supplier=fac.partner_id.id,
                default_tipo='compra vehiculo'
            )
            self.estado_pago = 'factura'
            return {
                'name': _('Factura Proveedor'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.invoice',
                'context': ctx,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': ultimo_id.id or False,
                # 'res_id': inv_ids and inv_ids[0] or False,
            }

    @api.multi
    def write(self, vals):
        if self.estado_pago == 'factura':
            raise Warning('Error!', 'No puede editar por que ya fue facturado Gracias!!')

        return super(fleet_compra_vehiculos, self).write(vals)


class fleet_compra_vehiculo_detalle(models.Model):
    _name = 'fleet.compra.vehiculo.detalle'
    _rec_name = 'compra_id'

    compra_id = fields.Many2one(comodel_name="fleet.compra.vehiculos", ondelete="cascade")
    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehículo")
    fecha_pago = fields.Date(string="Fecha de Pago", required=False, )
    importe_costo = fields.Float(string="Importe de costo",  required=False, digits=(50, 2))
    estado_pago = fields.Selection(string="Estado", selection=[('pendiente', 'Pendiente'), ('factura', 'Facturado'), ], required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Producto", required=False, )

    """CREAR FACTURA AL DAR CLICK EN EL BOTON FACTURAR"""

    @api.multi
    def llevar_datos_factura2(self, context=None):
        journal_id = self.env['account.journal'].search([('code', '=', 'DPL')])
        account_id = self.env['account.account'].search([('code', '=', '121100')])
        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('account', 'invoice_supplier_form')
        res_id = res and res[1] or False

        for fac in self:
            print fac

            vals = \
                {'partner_id': fac.compra_id.partner_id.id,
                 'date_invoice': fac.fecha_pago,
                 'date_due': fac.fecha_pago,
                 'origin': 'Compra - ' + str(fac.vehicle_id.name),
                 'account_id': account_id.id,
                 'journal_id': journal_id.id,
                 'currency_id': fac.compra_id.currency_id.id,
                 'type': 'in_invoice',
                 'tipo_factura': 2,
                 'invoice_line': [(0, 0, {'product_id': fac.product_id.id,
                                          'name': fac.product_id.name_template,
                                          'account_id': fac.product_id.property_account_expense.id,
                                          'uos_id': fac.product_id.uom_id.id,
                                          'price_unit': fac.importe_costo,
                                          'invoice_line_tax_id': [(6, 0, [x.id for x in fac.compra_id.tax_id])]})],
                 # 'tax_line': self._refund_cleanup_lines(invoice.invoice_line)
                 }

            ultimo_id = self.env['account.invoice'].create(vals)

            ctx = dict(
                type='in_invoice',
                default_supplier=fac.compra_id.partner_id.id,
            )
            self.estado_pago = 'factura'
            return {
                'name': _('Factura Proveedor'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.invoice',
                'context': ctx,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': ultimo_id.id or False,
                # 'res_id': inv_ids and inv_ids[0] or False,
            }


class fleet_compra_vehiculo_report(models.Model):

    _name = 'fleet.compra.vehiculo.report'
    _description = "Report"
    _auto = False

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehículo", readonly=1)
    fecha_pago = fields.Date('Fecha de Pago', readonly=1)
    importe_costo = fields.Float('Importe de costo', readonly=1)

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'fleet_compra_vehiculo_report')
        cr.execute("""
            create or replace view fleet_compra_vehiculo_report as (
                 SELECT rank_filter.* FROM (
 SELECT  row_number() OVER () AS id,vehicle_id, fecha_pago, importe_costo,
      rank() OVER (
          PARTITION BY vehicle_id
          ORDER BY fecha_pago
      )
    FROM fleet_compra_vehiculo_detalle fc
    WHERE fc.estado_pago = 'pendiente' and fecha_pago BETWEEN (SELECT cast(date_trunc('day',current_date) +'0days' as date))
                          AND (SELECT cast(date_trunc('day',current_date) +'6days' as date))
       ) rank_filter WHERE RANK <= 5
            )""")


    @api.multi
    def pagar(self, context=None):

        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('compra_vehiculos', 'fleet_compra_vehiculos_form')
        res_id = res and res[1] or False

        ultimo_id = self.env['fleet.compra.vehiculos'].search([['vehicle_id', '=', self.vehicle_id.id]])

        return {
            'name': _('Pagar'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'fleet.compra.vehiculos',
            # 'context': ctx,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': ultimo_id.id or False,
            # 'res_id': inv_ids and inv_ids[0] or False,
        }