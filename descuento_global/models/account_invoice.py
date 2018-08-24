# -*- coding: utf-8 -*-
import datetime
from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp
# from openerp.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
from lxml import etree

class GlobalDiscount(models.Model):
    _inherit = "account.invoice"

    # funcion que permite quitar los sheet al modulo
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            # print(context)
            if context.get('default_type') == 'in_invoice':
                doc = etree.XML(res['arch'])
                for sheet in doc.xpath("//sheet"):
                    parent = sheet.getparent()
                    index = parent.index(sheet)
                    for child in sheet:
                        parent.insert(index, child)
                        index += 1
                    parent.remove(sheet)
                res['arch'] = etree.tostring(doc)
        return res

    # @api.onchange('existe_percepcion','tax_line.code','monto_sin_perepcion', 'percepcion')
    # def _onchange_existe_percepcion(self):
    #     tax_line = []
    #     q = "SELECT id FROM account_account WHERE code=%s"
    #     self._cr.execute(q, ['401130'])
    #     account_id = self._cr.fetchone()[0]
    #     if self.existe_percepcion:
    #         tax_line.append((0, 0, {
    #             'name': 'Percepcion 2%',
    #             'account_id': account_id,
    #             'base':  self.monto_sin_percepcion,
    #             # 'base':  10,
    #             'base_amount':  self.monto_sin_percepcion,
    #             # 'base_amount':  10,
    #             'amount': self.percepcion,
    #             # 'amount': 10,
    #             'tax_amount': self.percepcion
    #             # 'tax_amount': 10
    #         }))
    #
    #     self.tax_line = tax_line
    #     return {'type': 'ir.actions.client', 'type': 'reload'}
    # @api.onchange('existe_detraccion_cliente','tax_line.code','detraccion_cliente', 'id_detracciones', 'amount_total','tax_line.name','tax_line.base')
    # def _onchange_existe_detraccion(self):
    #     tax_line = []
    #     q = "SELECT id FROM account_account WHERE code=%s"
    #     self._cr.execute(q, ['10711'])
    #     account_id = self._cr.fetchone()[0]
    #
    #     # current = self.env['res.currency'].search([['id','=',3]])
    #     if self.existe_detraccion_cliente:
    #         tax_line.append((0, 0, {
    #             'name': self.id_detracciones.name,
    #             'account_id': account_id,
    #             'base':  self.amount_total,
    #             # 'base':  10,
    #             'base_amount':  self.amount_total,
    #             # 'base_amount':  10,
    #             'amount': self.detraccion_cliente,
    #             # 'amount': 10,
    #             'tax_amount': self.detraccion_cliente
    #             # 'tax_amount': 10
    #         }))

        # if self.tax_line.name == 'IGV 18% Venta':
        #     self.tax_line
        # self.tax_line = tax_line

        # return {'type': 'ir.actions.client', 'type': 'reload'}
    #
    # @api.onchange('existe_detraccion_cliente','id_detracciones')
    # def _onchange_existe_detraccion_cliente(self):
    #     if self.existe_detraccion_cliente:
    #         monto_sin = (self.amount_untaxed + self.amount_tax)
    #         self.detraccion_cliente = (monto_sin * self.id_detracciones.amount) or 0.0
    #         # self.monto_sin_detraccion = (self.amount_untaxed + self.amount_tax) * 0.10
    #         # self.monto_sin_detraccion = self.amount_total - (self.amount_total * self.id_detracciones.amount)
    #
    #     return {'type': 'ir.actions.client', 'type': 'reload'}

    def _default_lista_detracciones(self):
        abc = self.env['account.tax'].search([['name', '=', 'Detracción 10%']], limit=1)
        return abc

    # global_discount = fields.Many2one('discounts', string="Seleccione Descuento Global")
    global_discount = fields.Float(string="Descuento Global",
                                   default=0.00,
                                   readonly=True,
                                   states={'draft': [('readonly', False)]})
    global_discount_type = fields.Selection([('amount', 'Monto'), ('percent', 'Porcentaje')],
                                            string="Tipo de descuento",
                                            readonly=True,
                                            states={'draft': [('readonly', False)]})
    global_discount_detail = fields.Char(string="Razón del descuento",
                                         readonly=True,
                                         states={'draft': [('readonly', False)]})
    amount_untaxed_global_discount = fields.Float(string="Descuento", default=0.00,
                                                  readonly=True,
                                                  store=True,
                                                  digits=dp.get_precision('Account'),
                                                  compute='_compute_descuento')
    monto_condescuento = fields.Float(string="Total con Desc.", default=0.00,
                                      readonly=True,
                                      store=True,
                                      digits=dp.get_precision('Account'),
                                      compute='_compute_descuento')
    descuento_porlinea_general = fields.Float(string="Total con Desc. Lineas", default=0.00,
                                              readonly=True,
                                              store=True,
                                              digits=dp.get_precision('Account'),
                                              compute='_compute_desc',
                                              track_visibility='always')

    percepcion = fields.Float(string=u"Percepción 2%",
                              default=0.00,
                              readonly=True,
                              store=True,
                              digits=dp.get_precision('Account'),
                              compute='_compute_percepcion',
                              track_visibility='always')


    monto_sin_percepcion = fields.Float(string=u"Importe",
                                        default=0.00,
                                        readonly=True,
                                        store=True,
                                        digits=dp.get_precision('Account'),
                                        compute='_compute_percepcion',
                                        track_visibility='always')

    existe_percepcion = fields.Boolean(string="¿Factura con Percepcion?")

    existe_detraccion_cliente = fields.Boolean(string=u"¿Factura con Detracción?", copy=False)
    # visible_detraccion = fields.Boolean()

    id_detracciones = fields.Many2one('account.tax', string=u"Detracciones", default=_default_lista_detracciones, copy=False)
    monto_detraccion_porcentaje = fields.Float(related='id_detracciones.amount', string="monto", store=True)

    detraccion_cliente = fields.Float(string=u"Detracción",
                              default=0.00,
                              readonly=True,
                              digits=dp.get_precision('Account'),
                              compute='_compute_detraccion',
                              track_visibility='always', copy=False,
                              store=True)

    monto_sin_detraccion = fields.Float(string=u"Monto con Detracción",
                                        default=0.00,
                                        readonly=True,
                                        digits=dp.get_precision('Account'),
                                        compute='_compute_detraccion',
                                        track_visibility='always', copy=False, store=True)

    creado_por = fields.Char(string="Factura creada por", compute='_compute_creado_por')
    ultima_upd = fields.Char(string="Ultimo usuario que modifico", compute='_compute_ultima_upd')
    enviado_sunat = fields.Boolean('Enviado Sunat', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('enviar_sunat', 'Enviar a Sunat'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
        ('anulado', 'Anulado'),
        ('error_rechazo', 'Rechazado por Sunat'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    # proveedor
    serie_factura_proveedor = fields.Char(string='N° Serie Factura', size=4, required=True,copy=False)
    correlativo_factura_proveedor = fields.Char(string='N° Correlativo Factura', size=8, required=True,copy=False)

    es_boleta = fields.Boolean('Boleta?')

    tipo_documento_ref = fields.Many2one('einvoice.catalog.01', 'Tipo de Doc. Ref.', copy=False)
    fecha_documento_ref = fields.Date('Fecha de Doc. Ref.', copy=False)

    otro_correlativo_documento_ref = fields.Char('N° Documento', copy=False)
    otra_fecha_documento_ref = fields.Date('Fecha Documento', copy=False)

    # gravada_exportacion = fields.Boolean('Oper. Gravada o Exportaciones')
    # exportacion_nograbadas = fields.Boolean('Adquis. grabadas de exp. no gravadas')
    # adquisicion_sinderecho = fields.Boolean('Adquisición sin derecho')
    # adquisicion_nograbada = fields.Boolean('Adquisición no grabada')
    estado_expostacion_gravada_adqui = fields.Selection([
        ('gravada_exportacion', 'Oper. Gravada o Exportaciones'),
        ('exportacion_nograbadas', 'Adquis. grabadas de exp. no gravadas'),
        ('adquisicion_sinderecho', 'Adquisición sin derecho'),
        ('adquisicion_nograbada', 'Adquisición no grabada'),
    ], default='gravada_exportacion', copy=False)
    estado_credito_fiscal = fields.Selection([
        ('no_credito', 'Sin derecho a Credito Fiscal'),
        ('si_credito', 'Con derecha a Credito Fiscal'),

    ], default='no_credito', copy=False)

    exportacion_nograbadas = fields.Float(string='Base Imp.Adq.Grav de exp. o no Grav', copy=False)  # B.I. B
    igv_exportacion_nograbadas = fields.Float(string='I.G.V.', copy=False)  # I.G.V. B
    adquisicion_sinderecho = fields.Float(string='Adq.Grav. sin Derecho', copy=False)  # B.I. C
    igv_adquisicion_sinderecho = fields.Float(string='I.G.V.', copy=False)  # I.G.V. C
    adquisicion_nograbada = fields.Float(string='Adquisiciónes no Grabadas', copy=False)  # A.no.G
    otros_tributos = fields.Float(string='Otros Tributos', copy=False)
    impuesto_selectivo_consumo = fields.Float(string='Impuesto Selectivo Consumo (I.S.C.)', copy=False)

    @api.multi
    def unlink(self):
        self._cr.execute(
            """DELETE FROM modulo_valorizaciones_facturas_contrato WHERE id_factura = %s;""", [self.id])
        return super(GlobalDiscount, self).unlink()

    @api.onchange('exportacion_nograbadas')
    def onchange_exportacion_nograbadas(self):
        porcentaje_igv_compra = self.env['account.tax'].search([['description', '=', 'IGVC']], limit=1).amount
        self.igv_exportacion_nograbadas = self.exportacion_nograbadas * porcentaje_igv_compra

    # @api.onchange('adquisicion_sinderecho')
    # def onchange_adquisicion_sinderecho(self):
    #     porcentaje_igv_compra = self.env['account.tax'].search([['description', '=', 'IGVC']], limit=1).amount
    #     self.igv_adquisicion_sinderecho = self.adquisicion_sinderecho * porcentaje_igv_compra

    @api.multi
    def precio_con_igv(self):
        porcentaje_igv_compra = self.env['account.tax'].search([['description', '=', 'IGVC']], limit=1).amount
        exportacion_nograbadas = self.exportacion_nograbadas / (1 + porcentaje_igv_compra)
        print(exportacion_nograbadas)
        self.exportacion_nograbadas = exportacion_nograbadas
        self.onchange_exportacion_nograbadas()
        # self.button_reset_taxes()

    @api.one
    # @api.onchange('vacaciones_ids')
    @api.constrains('serie_factura_proveedor', 'correlativo_factura_proveedor', 'partner_id')
    def _check_numeracion_proveedor(self):
        # mod_obj = self.env['ir.model.data']
        # res = mod_obj.get_object_reference('account', 'invoice_supplier_form')
        # res_id = res and res[1] or False
        obj_invoice_supplier = self.search([['serie_factura_proveedor','=',self.serie_factura_proveedor],
                                           ['correlativo_factura_proveedor','=',self.correlativo_factura_proveedor],
                                           ['serie_factura_proveedor','!=',''],
                                           ['correlativo_factura_proveedor','!=',''],
                                           ['partner_id.id','=',self.partner_id.id],])
        # raise Warning(obj_invoice_supplier)
        if len(obj_invoice_supplier) > 1:
            raise Warning('Aviso!', 'Este N° y Serie de Comprobante ya esta registrado!')
        return True

    @api.one
    @api.depends('invoice_line.price_desc')
    def _compute_desc(self):
        self.descuento_porlinea_general = sum(line.price_desc for line in self.invoice_line)

    @api.multi
    def onchange_journal_id(self, journal_id=False):
        # self.ensure_one()
        result = super(GlobalDiscount, self).onchange_journal_id(journal_id=journal_id)
        v = {}
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            if journal and journal.type != 'purchase':
                if int(journal.code) == 3:
                    result['value']['es_boleta'] =True
                else:
                    result['value']['es_boleta'] = False

        return result

    @api.one
    @api.depends('create_uid')
    def _compute_creado_por(self):
        nombre_create = self.env['res.users'].search([['id','=',self.create_uid.id]])
        self.creado_por = str(nombre_create.partner_id.name + ', ' + self.create_date)

    @api.one
    @api.depends('write_uid')
    def _compute_ultima_upd(self):
        nombre_create = self.env['res.users'].search([['id', '=', self.write_uid.id]])
        self.ultima_upd = str(nombre_create.partner_id.name + ', ' + self.write_date)

    @api.one
    @api.depends('amount_total', 'percepcion', 'amount_untaxed', 'amount_tax')
    def _compute_percepcion(self):
        if self.existe_percepcion:
            self.monto_sin_percepcion = self.amount_untaxed + self.amount_tax
            self.percepcion = (self.monto_sin_percepcion * 0.02) or 0.0

    @api.one
    @api.depends('amount_total', 'id_detracciones', 'detraccion_cliente', 'amount_untaxed', 'amount_tax')
    def _compute_detraccion(self):
        if self.existe_detraccion_cliente:
            monto_sin = (self.amount_untaxed + self.amount_tax)
            self.detraccion_cliente = (monto_sin * self.monto_detraccion_porcentaje)
            self.monto_sin_detraccion = monto_sin - self.detraccion_cliente

    @api.multi
    def _compute_amount2(self):
        # self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        # self.amount_tax = (self.amount_untaxed * 0.18) or 0.0
        # self.amount_tax = sum(line.amount for line in self.tax_line)
        if self.existe_percepcion:
            print ('entreeeeeee')
            # self.amount_total = self.amount_untaxed + self.invoice_line.tax_amount
            monto_total = self.monto_sin_percepcion + self.percepcion
            return {'value': {'amount_total': monto_total}}

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'exportacion_nograbadas', 'igv_exportacion_nograbadas', 'adquisicion_sinderecho', 'igv_adquisicion_sinderecho', 'adquisicion_nograbada', 'otros_tributos', 'impuesto_selectivo_consumo')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.exportacion_nograbadas = self.amount_untaxed
        self.igv_exportacion_nograbadas = self.amount_tax

    @api.multi
    def write(self, vals):
        vals['exportacion_nograbadas'] = self.amount_untaxed
        vals['igv_exportacion_nograbadas'] = self.amount_tax
        """ automatic compute tax then save """
        res = super(GlobalDiscount, self).write(vals)

        return res

    @api.one
    @api.depends('global_discount', 'global_discount_type', 'amount_total', 'percepcion', 'detraccion_cliente')
    def _compute_descuento(self):
        if self.global_discount > 0 and self.global_discount_type:
            _logger.info("entro compute_tax")
            discount = self.global_discount

            if self.global_discount_type in ['amount']:
                self.amount_untaxed_global_discount = discount or 0.0
                self.monto_condescuento = (self.amount_total - discount) or 0.0
                # self.monto_condescuento += self.percepcion
                _logger.info('>>>monto>>>' + str(self.amount_untaxed_global_discount))

            elif self.global_discount_type in ['percent']:
                self.amount_untaxed_global_discount = self.amount_total * ((discount / 100.0) or 0.0)
                self.monto_condescuento = self.amount_total * (1 - ((discount / 100.0) or 0.0))
                # self.monto_condescuento += self.percepcion
                _logger.info('>>>poncentaje>>>' + str(self.amount_untaxed_global_discount))

    def _compute_residual(self):
        self.residual = 0.0
        # Each partial reconciliation is considered only once for each invoice it appears into,
        # and its residual amount is divided by this number of invoices
        partial_reconciliations_done = []
        _logger.info('>>>residualresidualresidualresidualresidualresidual>>>')
        # print (self.sudo().move_id.line_id)
        for line in self.sudo().move_id.line_id:
            if line.account_id.type not in ('receivable', 'payable'):
                continue
            if line.reconcile_partial_id and line.reconcile_partial_id.id in partial_reconciliations_done:
                continue
            # Get the correct line residual amount

            if line.currency_id == self.currency_id:
                # _logger.info('>>>residualresidualresidualresidualresidualresidual>>>')
                # print (line.currency_id == self.currency_id)
                # print (line.amount_residual_currency)
                line_amount = line.currency_id and line.amount_residual_currency or line.amount_residual
            else:
                from_currency = line.company_id.currency_id.with_context(date=line.date)
                line_amount = from_currency.compute(line.amount_residual, self.currency_id)

            # For partially reconciled lines, split the residual amount
            if line.reconcile_partial_id:
                partial_reconciliation_invoices = set()
                for pline in line.reconcile_partial_id.line_partial_ids:
                    if pline.invoice and self.type == pline.invoice.type:
                        partial_reconciliation_invoices.update([pline.invoice.id])
                line_amount = self.currency_id.round(line_amount / len(partial_reconciliation_invoices))
                partial_reconciliations_done.append(line.reconcile_partial_id.id)
            self.residual += line_amount

        self.residual = max(self.residual, 0.0)
        # self.residual += self.amount_total
        # _logger.info('>>>residualresidualresidualresidualresidualresidual>>>')
        # print (self.residual)
        # yo
        # self.residual -= self.detraccion_cliente
        self.residual += self.amount_untaxed_global_discount

    @api.multi
    def invoice_pay_customer(self):
        self.ensure_one()
        res = super(GlobalDiscount, self).invoice_pay_customer()
        res['context']['default_moneda_rate_compra'] = self.currency_id.rate
        res['context']['default_currency_compra'] = self.currency_id.tc_compra
        res['context']['default_currency_venta'] = self.currency_id.tc_venta
        if self.detraccion_cliente:
            res['context']['default_detraccion_cliente'] = self.detraccion_cliente
        # print res
        return res

    @api.model
    def default_get(self, fields):
        period_obj = self.env['account.period']
        if self._context is None:
            self._context = {}
        if not self._context.get('period_id', False):
            self.with_context(period_id=self._context.get('search_default_period_id', False))
        print(self._context)
        # context = self.convert_to_period(self._context)
        print('----------')
        # print(context)
        print('----------')
        res = super(GlobalDiscount, self).default_get(fields)

        return res

    def convert_to_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        period_obj = self.pool.get('account.period')
        # check if the period_id changed in the context from client side
        if context.get('period_id', False):
            period_id = context.get('period_id')
            if type(period_id) == str:
                ids = period_obj.search(cr, uid, [('name', 'ilike', period_id)])
                context = dict(context, period_id=ids and ids[0] or False)
        return context

    def list_periods(self, cr, uid, context=None):
        ids = self.pool.get('account.period').search(cr,uid,[])
        return self.pool.get('account.period').name_get(cr, uid, ids, context=context)


class DescuentoLinea(models.Model):
    _inherit = "account.invoice.line"

    price_desc = fields.Float(string='monto descuento', digits=dp.get_precision('Account'),
                              store=True, readonly=True, compute='_compute_price', )

    price_subtotal = fields.Float(string='Amount', digits=dp.get_precision('Account'), compute='_compute_price', inverse='_inverse_price', store=True)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        # print ('>>>>>>>>>',str(price))
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id,
                                                     partner=self.invoice_id.partner_id)

        prec = self.price_unit * self.quantity
        descuento_linea = prec * ((self.discount or 0.0) / 100.0)
        montos = {'descuento': descuento_linea}
        self.price_desc = montos['descuento']
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
            round(self.price_subtotal, 2)

    @api.one
    def _inverse_price(self):
        print self.price_subtotal / self.quantity
        print (round((self.price_subtotal / self.quantity), 1))
        print (round((self.price_subtotal / self.quantity), 2))
        print (round((self.price_subtotal / self.quantity), 3))
        self.price_unit = round((self.price_subtotal / self.quantity), 2)


class Invoice_type_unit(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'product.uom'

    code = fields.Char(string="Codigo Unidad de Medida", required=True)


# class producto_unidades_medida_internacionales(models.Model):
#     _name = 'producto.unidades.medida.internacionales'
#     _rec_name = 'name'
#     # _description = 'New Description'
#
#     code = fields.Char('Codigo')
#     name_ingles = fields.Char('Nombre en Ingles')
#     name = fields.Char('Nombre')

class re_currency(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'res.currency'

    tc_compra = fields.Float(string="Compra", digits=(12, 3))
    tc_venta = fields.Float(string="Venta", digits=(12, 3))



class account_tax(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'account.tax'

    lista_detracciones = fields.Boolean(string="Agregar a Detracciones")

#
# class inherit_account_voucher(models.Model):
#     # _name = 'new_module.new_module'
#     _inherit = 'account.voucher'
#

# class inherit_account_voucher_line(models.Model):
#     # _name = 'new_module.new_module'
#     _inherit = 'account.voucher.line'
#
#     def _compute_balance(self, cr, uid, ids, name, args, context=None):
#
#         currency_pool = self.pool.get('res.currency')
#         rs_data = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             ctx = context.copy()
#             ctx.update({'date': line.voucher_id.date})
#             voucher_rate = self.pool.get('res.currency').read(cr, uid, line.voucher_id.currency_id.id, ['rate'], context=ctx)['rate']
#             ctx.update({
#                 'voucher_special_currency': line.voucher_id.payment_rate_currency_id and line.voucher_id.payment_rate_currency_id.id or False,
#                 'voucher_special_currency_rate': line.voucher_id.payment_rate * voucher_rate})
#             res = {}
#             company_currency = line.voucher_id.journal_id.company_id.currency_id.id
#             voucher_currency = line.voucher_id.currency_id and line.voucher_id.currency_id.id or company_currency
#             move_line = line.move_line_id or False
#
#             if not move_line:
#                 res['amount_original'] = 0.0
#                 res['amount_unreconciled'] = 0.0
#             elif move_line.currency_id and voucher_currency==move_line.currency_id.id:
#                 res['amount_original'] = abs(move_line.amount_currency)
#                 res['amount_unreconciled'] = abs(move_line.amount_residual_currency)
#             else:
#                 #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
#                 res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit or move_line.debit or 0.0, context=ctx)
#                 res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)
#
#             rs_data[line.id] = res
#             print ('rfffffffffff')
#             print (res)
#         return rs_data

class account_voucher(models.Model):

    _inherit = "account.voucher"

    monto_soles = fields.Float(
        'Monto Soles',
        digits=dp.get_precision('Account'),
        required=True,
        default=0.0,  # for compatibility with other modules
        compute='_get_amount',
        states={'draft': [('readonly', False)]},
        help='Amount Paid With Journal Method',
        store=True
    )

    @api.one
    @api.depends('amount','journal_id')
    def _get_amount(self, context=None):
        obj_journal = self.env['account.journal']
        journal = obj_journal.browse([self.journal_id.id])
        # cambio = self.env['res.currency'].search([['name','=','USD']])
        if journal.currency.tc_compra:
            compra = journal.currency.tc_compra
        else:
            compra = 1
        print ('sssssssssss',str(compra))
        self.monto_soles = self.amount * compra

    @api.v7
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id,
                         context=None):
        '''
        Si al cambiar el payment_option atualizamos las cuentas acorde al diario,
        entonces debemos tambien actualizarlas cuando cambie el diario.
        Por facilidad se ha programado que al cambiar el diario el payment_option se cambie a without_writeoff
        '''
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id,
                                                            date, amount, ttype, company_id, context=context)

        if res:
            res['value'].update({'journal_id': journal_id})
            if ttype == 'receipt':
                if int(res['value']['currency_id']) == 3:
                    res['value']['currency_help_label'] = 'En la fecha de operaci\xf3n, la tasa de cambio fue\n $ 1.00 = S/. %.3f' % res['value']['payment_rate']
                elif int(res['value']['currency_id']) == 165:
                    res['value']['currency_help_label'] = 'En la fecha de operaci\xf3n, la tasa de cambio fue\n S/. 1.00 = $. %.6f' % res['value']['payment_rate']

                if int(res['value']['journal_id']) == 18:
                    res['value']['amount'] = context.get('default_detraccion_cliente')
                elif int(res['value']['journal_id']) == 14:
                    res['value']['amount'] = context.get('default_amount')
                elif int(res['value']['journal_id']) == 15:
                    res['value']['amount'] = context.get('default_amount')
                else:
                    res['value']['amount'] = context.get('default_amount')
        return res

    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('proforma', 'Pro-forma'),
         ('posted', 'Posted'),
         ('eliminado', 'Eliminado')
         ], 'Status', readonly=True, track_visibility='onchange', copy=False)

    @api.multi
    def eliminar_comprobante(self):
        self.cancel_voucher()
        self.write({'state':'eliminado'})

    @api.multi
    def reclasificar_comprobante(self):
        self.cancel_voucher()
        self.action_cancel_draft()


class res_users(models.Model):
    _inherit = 'res.users'

    # funcion que permite quitar los sheet al modulo
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            print ('usersssssssssssssssss',str(uid))
            doc = etree.XML(res['arch'])
            if uid != 1:
                for sheet in doc.xpath("//field[@name='sel_groups_3_4']"):
                    parent = sheet.getparent()
                    index = parent.index(sheet)
                    for child in sheet:
                        parent.insert(index, child)
                        index += 1
                    parent.remove(sheet)
                res['arch'] = etree.tostring(doc)
        return res