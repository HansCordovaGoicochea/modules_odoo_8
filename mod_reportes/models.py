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
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from lxml import etree
from openerp.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


class purchase_reports(models.Model):
    _name = 'purchase.reports'
    _rec_name = 'name'
    _auto = False

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    name = fields.Char('Referencia')
    date_order = fields.Datetime('Fecha de Pedido')
    partner_id = fields.Many2one('res.partner', 'Proveedor')
    minimum_planned_date = fields.Date('Fecha Prevista')
    amount_untaxed = fields.Float('Monto Sin Impuesto')
    amount_total = fields.Float('Monto Total')
    categ_id = fields.Many2one('product.category', 'Categoria')
    state = fields.Selection(STATE_SELECTION,'Estado')

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'purchase_reports')
        cr.execute("""
               create or replace view purchase_reports as (
               select row_number() OVER () AS id, po.name, date_order, po.partner_id, minimum_planned_date, po.amount_untaxed, po.amount_total, po.state, ptt.categ_id
from purchase_order po INNER JOIN purchase_order_line pol
  on po.id = pol.order_id INNER JOIN product_product pt
  on pol.product_id = pt.id inner JOIN product_template ptt
  on pt.product_tmpl_id = ptt.id
  where po.state = 'approved'
  order by 1)
               """)


class products_stock_reports(models.Model):
    _name = 'products.stock.reports'
    # _rec_name = 'name'
    _auto = False

    name = fields.Char('Producto')
    categ_id = fields.Many2one('product.category', 'Categoria')
    tipo = fields.Selection([('consu', 'Consumable'), ('service', 'Service')], 'Tipo')
    stock = fields.Float(string='Cantidad')

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'products_stock_reports')
        cr.execute(""" create or replace view products_stock_reports as (
              with
  uitstock as (
    select
      t.name product, sum(product_qty) sumout, m.product_id, m.product_uom, t.categ_id, t.type, swo.product_min_qty
    from stock_move m
      left join product_product p on m.product_id = p.id
      left join product_template t on p.product_tmpl_id = t.id
      INNER JOIN stock_warehouse_orderpoint swo on p.id = swo.product_id
    where
      m.state like 'done'
      and m.location_id in (select id from stock_location where complete_name like '%Stock%')
      and m.location_dest_id not in (select id from stock_location where complete_name like '%Stock%')
    group by m.product_id, product_uom, t.name,t.categ_id, t.type, swo.product_min_qty order by t.name asc
  ),
  instock as (
    select
      t.list_price purchaseprice, t.name product, sum(product_qty) sumin, m.product_id, m.product_uom, t.categ_id, t.type, swo.product_min_qty
    from stock_move m
      left join product_product p on m.product_id = p.id
      left join product_template t on p.product_tmpl_id = t.id
       INNER JOIN stock_warehouse_orderpoint swo on p.id = swo.product_id
    where
      m.state like 'done' and m.location_id not in (select id from stock_location where complete_name like '%Stock%')
      and m.location_dest_id in (select id from stock_location where complete_name like '%Stock%')
    group by m.product_id, product_uom, t.name, t.list_price,t.categ_id, t.type, swo.product_min_qty order by t.name asc
  )
select
   row_number() OVER () AS id, i.product as name, i.categ_id, i.type as tipo, sumin-coalesce(sumout,0) AS stock
from uitstock u
  full outer join instock i on u.product = i.product
where sumin-coalesce(sumout,0) <= i.product_min_qty
               )
               """)


class products_mmvendidos_reports(models.Model):
    _name = 'products.mmvendidos.reports'
    # _rec_name = 'name'
    _order = 'cantidad desc'
    _auto = False

    product_id = fields.Many2one('product.product')
    name_template = fields.Char('Producto')
    categ_id = fields.Many2one('product.category', 'Categoria')
    loc_rack = fields.Char('Almacen')
    loc_row = fields.Char('Pasadizo')
    loc_case = fields.Char('Fila')
    venta = fields.Float('Precio Venta')
    compra = fields.Float('Precio Compra')
    cantidad = fields.Float('Cant. Vendida')
    totalvendido = fields.Float('Total Vendido')
    mes_anio = fields.Char('Mes y Año')
    fecha = fields.Datetime('Fecha de Venta')

    def init(self, cr):
        print ('entrandooooooooooooooo')
        tools.drop_view_if_exists(cr, 'products_mmvendidos_reports')
        cr.execute(""" create or replace view products_mmvendidos_reports as (
             SELECT row_number() OVER () AS id,m.product_id, p.name_template,t.categ_id,t.loc_rack,t.loc_case,t.loc_row,t.list_price as venta, cp.cost as compra, sum(qty) as cantidad, (t.list_price * sum(qty)) totalvendido, to_char((select ol.write_date from pos_order_line ol order by id desc limit 1), 'MM/YYYY') as mes_anio, (select ol.write_date from pos_order_line ol order by id desc limit 1) as fecha
FROM pos_order_line m left join (select product_template_id, cost from product_price_history order by id desc limit 1) as cp on m.product_id = cp.product_template_id
  left join product_product p on m.product_id = p.id
  left join product_template t on p.product_tmpl_id = t.id
GROUP BY product_id, p.name_template,t.categ_id,t.loc_rack,t.loc_case, t.loc_row, venta, compra
order by cantidad desc
               )
               """)


class pos_order(models.Model):
    _inherit = 'pos.order'

    lines = fields.One2many('pos.order.line', 'order_id', 'Order Lines', states={'draft': []},readonly=False, copy=True)

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(pos_order, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                            context=context, toolbar=toolbar, submenu=submenu)
        id_exi = self.pool.get('res.users').has_group(cr, uid, 'base.group_sale_salesman')

        # raise Warning(uid)
        if view_type == 'form' and id_exi and uid != 1:
            doc = etree.XML(res['arch'])
            print doc
            method_nodes = doc.xpath("//field")
            for node in method_nodes:
                node.set('readonly', "1")
                # if node.get('name', False) and node.get('name', False) not in ['name','image_medium']:  # Add fields to skip readonly
                #     setup_modifiers(node, res['fields'][node.get('name', False)])
            res['arch'] = etree.tostring(doc)
        return res
