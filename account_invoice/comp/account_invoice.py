# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import tools
from openerp import api
from openerp.exceptions import except_orm, Warning, RedirectWarning
# from xml.etree.ElementTree import ElementTree
# from xml.etree.ElementTree import Element
# import xml.etree.ElementTree as etree
import base64
import zipfile
from xml.dom import minidom
from OpenSSL import crypto
from probando import Probando, webService
from openerp.exceptions import AccessError
import hashlib
import itertools
import logging
import os
import re
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from bar import BarCo


import time
import datetime
import calendar
from datetime import date,timedelta
import dateutil.parser
import unicodedata

_logger = logging.getLogger(__name__)

# pkcs12 = crypto.load_pkcs12(open(r'd:/a.pfx', 'rb').read(), 'SFSC42')
#
# cert_str = crypto.dump_certificate(crypto.FILETYPE_PEM,
# pkcs12.get_certificate())
# key_str = crypto.dump_privatekey(crypto.FILETYPE_PEM,
# pkcs12.get_privatekey())

doc = minidom.Document()


#
# pfx=open(r'd:/a.pfx', 'rb').read()
# PKCS=crypto.load_pkcs12(pfx,'SFSC42')
# cert=PKCS.get_certificate()
# PKey=cert.get_pubkey()
# pk=PKCS.get_privatekey()
# pkStr=crypto.dump_privatekey(crypto.FILETYPE_PEM,pk)

# from pysimplesoap.client import SoapClient
# from conf import SUNAT_WS


class account_invoice_line(osv.osv):
    # def _get_default_afectacion(self, cr, uid, context=None):
    #     res = self.pool.get('einvoice.catalog.07')
    #     res.search(cr, uid, [('code', '=', '10')], context=context)
    #     return res and res[0] or False

    _inherit = "account.invoice.line"
    _columns = {
        'comparacion': fields.char('Comparacion'),
        'afectacion_igv': fields.many2one('einvoice.catalog.07', u'Tipo de Afectación al IGV', required=True, default=1),
        'product_id': fields.many2one('product.product', string='Product', ondelete='restrict', index=True, required=True),
    }

    # _defaults = {
    #         'afectacion_igv': _get_default_afectacion,
    #     }


account_invoice_line()


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'credito': fields.boolean('¿Tiene Crédito?'),
        'monto': fields.float('Monto'),
        'combustible': fields.float('Litros'),
    }

    _defaults = {
        'credito': True,
    }

    @api.onchange('combustible')
    def check_change_combustible(self):
        template = self.pool.get('res.partner').search(self.env.cr, self.env.uid,
                                                       [('doc_number', '=', str(self.doc_number))])
        if template:
            self._cr.execute(""" UPDATE modulo_valorizaciones_linea_credito SET monto_galones=%s
                                                  WHERE proveedor=%s""",
                             (self.combustible, template[0]))

    @api.onchange('monto')
    def check_change_monto(self):
        template = self.pool.get('res.partner').search(self.env.cr, self.env.uid,
                                                       [('doc_number', '=', str(self.doc_number))])
        if template:
            self._cr.execute(""" UPDATE modulo_valorizaciones_linea_credito SET monto_dinero=%s
                                                              WHERE proveedor=%s""",
                             (self.combustible, template[0]))


# class account_bank_statement_line(osv.osv) :
#    _inherit = "account.bank.statement.line"
#    _columns = {
#        'entrega_factura': fields.boolean('Entrega Factura Física'),
#    }
# account_bank_statement_line()

class account_invoice_line(osv.osv):
    _inherit = "account.move.line"
    _columns = {
        'type': fields.selection(
            [('out_invoice', 'Customer Invoice'), ('in_invoice', 'Supplier Invoice'), ('out_refund', 'Customer Refund'),
             ('in_refund', 'Supplier Refund')],
            string='Type', readonly=True, index=True, change_default=True,
            default=lambda self: self._context.get('type', 'in_invoice'),
            track_visibility='always'),
        'entrega_factura_fisica': fields.float('¿Entrega Factura Física?'),
        'tipo_factura': fields.selection(
            [('factura_fisica', 'Factura Física'), ('factura_digitalizada', 'Factura Digitalizada')],
            'Tipo de Factura'),


    }


account_invoice_line()


class account_invoice_conceptos(osv.osv):
    # def _get_default_concepto(self, cr, uid, context=None):
    #     res = self.pool.get('einvoice.catalog.20').search(cr, uid, [('code', '=', '1001')], context=context)
    #     return res and res[0] or False
    def _get_default_category(self, cr, uid, context=None):
        res = self.pool.get('einvoice.catalog.20').search(cr, uid, [('code', '=', 1001)], context=context)
        return res and res[0] or False

    @api.one
    @api.depends('invoice_id.invoice_line.price_unit', 'invoice_id.invoice_line.price_subtotal',
                 'invoice_id.tax_line.amount')
    def _compute_monto(self):
        amount_untaxed = sum(line.price_subtotal for line in self.invoice_id.invoice_line)
        # amount_tax = sum(line.amount for line in self.invoice_id.tax_line)
        if self.conceptos_tributarios.code == '1001':
            self.monto_total = amount_untaxed
        if self.conceptos_tributarios.code == '1004':
            self.monto_total = sum(line.price_unit for line in self.invoice_id.invoice_line)
        if self.conceptos_tributarios.code == '1003':
            self.monto_total = sum(line.price_subtotal for line in self.invoice_id.invoice_line)
        if self.conceptos_tributarios.code == '2005':
            self.monto_total = self.invoice_id.amount_untaxed_global_discount
        if self.conceptos_tributarios.code == '2003':
            self.monto_total = self.invoice_id.detraccion_cliente

    _name = "account.invoice.conceptos"
    _columns = {
        'conceptos_tributarios': fields.many2one('einvoice.catalog.20', string='Conceptos Tributarios', required=True),
        'invoice_id': fields.many2one('account.invoice', string='Invoice Reference', ondelete='cascade', index=True),
        'monto_total': fields.float(compute='_compute_monto', string='Total')

    }
    # _defaults = {
    #     'conceptos_tributarios': _get_default_category,
    # }


account_invoice_conceptos()

typo = ''
serie = ''
nombre = ''


class account_invoice(osv.osv):


    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False,context=None):
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
                                                               date_invoice=date_invoice, payment_term=payment_term,
                                                               partner_bank_id=partner_bank_id,
                                                               company_id=company_id)

        invoice_ids = []
        product_ids = self.pool.get('einvoice.catalog.20').search(cr, uid, [], limit=1)
        fac = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)

        print (fac)
        if fac:
            if fac.parent_id.doc_number:
                res['value']['ruc'] = fac.parent_id.doc_number
            elif fac.doc_number:
                res['value']['ruc'] = fac.doc_number
            else:
                res['value']['ruc'] = ''

        # product_ids = self.pool.get('product.product').search(cr, uid, [], limit=5)
        # for p in self.pool.get('product.product').browse(cr, uid, product_ids):
        for p in self.pool.get('einvoice.catalog.20').browse(cr, uid, product_ids):
            invoice_ids.append((0, 0, {'conceptos_tributarios': p.id, 'code': p.code}))
        res['value']['invoice_ids'] = invoice_ids
        return res

    def _storage(self, cr, uid, context=None):
        return self.pool['ir.config_parameter'].get_param(cr, SUPERUSER_ID, 'ir_attachment.location', 'file')

    def _filestore(self, cr, uid, context=None):
        return tools.config.filestore(cr.dbname)

    def force_storage(self, cr, uid, context=None):
        """Force all attachments to be stored in the currently configured storage"""
        if not self.pool['res.users'].has_group(cr, uid, 'base.group_erp_manager'):
            raise AccessError(_('Only administrators can execute this action.'))

        location = self._storage(cr, uid, context)
        domain = {
            'db': [('store_fname', '!=', False)],
            'file': [('db_datas', '!=', False)],
        }[location]

        ids = self.search(cr, uid, domain, context=context)
        for attach in self.browse(cr, uid, ids, context=context):
            attach.write({'datas': attach.datas})
        return True

    def _full_path(self, cr, uid, path):
        # sanitize ath
        path = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(cr, uid), path)

    def _get_path(self, cr, uid, bin_data):
        sha = hashlib.sha1(bin_data).hexdigest()

        # retro compatibility
        fname = sha[:3] + '/' + sha
        full_path = self._full_path(cr, uid, fname)
        if os.path.isfile(full_path):
            return fname, full_path  # keep existing path

        # scatter files across 256 dirs
        # we use '/' in the db (even on windows)
        fname = sha[:2] + '/' + sha
        full_path = self._full_path(cr, uid, fname)
        dirname = os.path.dirname(full_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return fname, full_path

    def _file_read(self, cr, uid, fname, bin_size=False):
        full_path = self._full_path(cr, uid, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path, 'rb').read().encode('base64')
        except IOError:
            _logger.exception("_read_file reading %s", full_path)
        return r

    def _file_write(self, cr, uid, value):
        bin_value = value.decode('base64')
        fname, full_path = self._get_path(cr, uid, bin_value)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
            except IOError:
                _logger.exception("_file_write writing %s", full_path)
        return fname

    def _file_delete(self, cr, uid, fname):
        # using SQL to include files hidden through unlink or due to record rules
        cr.execute("SELECT COUNT(*) FROM ir_attachment WHERE store_fname = %s", (fname,))
        count = cr.fetchone()[0]
        full_path = self._full_path(cr, uid, fname)
        if not count and os.path.exists(full_path):
            try:
                os.unlink(full_path)
            except OSError:
                _logger.exception("_file_delete could not unlink %s", full_path)
            except IOError:
                # Harmless and needed for race conditions
                _logger.exception("_file_delete could not unlink %s", full_path)

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self._storage(cr, uid, context)
        file_size = len(value.decode('base64'))
        attach = self.browse(cr, uid, id, context=context)
        fname_to_delete = attach.store_fname
        if location != 'db':
            fname = self._file_write(cr, uid, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(account_invoice, self).write(cr, SUPERUSER_ID, [id],
                                             {'store_fname': fname, 'file_size': file_size, 'db_datas': False},
                                             context=context)
        else:
            super(account_invoice, self).write(cr, SUPERUSER_ID, [id],
                                             {'db_datas': value, 'file_size': file_size, 'store_fname': False},
                                             context=context)

        # After de-referencing the file in the database, check whether we need
        # to garbage-collect it on the filesystem
        if fname_to_delete:
            self._file_delete(cr, uid, fname_to_delete)
        return True


    _inherit = "account.invoice"
    _columns = {
        'entrega_factura_fisica': fields.boolean('¿Entrega Factura Física?', copy=False),
        'enviado': fields.boolean('Enviado', default=0, copy=False),
        'ruc': fields.char('RUC'),
        'monto_letras': fields.char('Monto Letras'),
        'digest_value': fields.char('Valor Resumen', copy=False),
        'tipo_factura': fields.many2one('einvoice.catalog.01', string='Tipo de Comprobante', required=True),

        'invoice_ids': fields.one2many('account.invoice.conceptos', 'invoice_id', string='Conceptos Tributarios',
                                       copy=True),
        'datas_fname': fields.char('File Name'),
        'datas': fields.function(_data_get,fnct_inv=_data_set , string='File Content', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename'),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'documentos': fields.many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                       'Documentos'),
        # 'filename': fields.char('file name', store=False, compute='legacy_doc1_getFilename')
        'mensaje_cdr': fields.char(string='Resultado CDR', readonly=True, store=True, copy=False),
        'image_bar': fields.binary(string='QR', copy=False),

    # 'conceptos_tributarios': fields.many2one('einvoice.catalog.20', string='Otros Conceptos Tributarios')

    }

    @api.model
    def create(self, vals):

        self.env.cr.execute("SELECT count(id) "
                            "FROM account_invoice "
                            "WHERE create_date "
                            "BETWEEN (SELECT date_trunc('month',current_date) - '1month' ::INTERVAL) "
                            "AND (SELECT date_trunc('month',current_date) -'1sec' ::INTERVAL)")
        data = self.env.cr.fetchall()
        # print('>>>>>>>>>>>>' + str(data))
        if len(data) == 0:
            raise osv.except_osv(_('Error!'), _("No Existen Comprobantes en el mes anterior"))

        res_id = super(account_invoice, self).create(vals)
        # self.env.cr.execute(""" INSERT INTO account_invoice_conceptos(invoice_id,catalogo20_id) VALUES (%s, %s)""",(res_id, 'conceptos_tributarios'))
        return res_id

    @api.onchange('ruc')
    def check_change_ruc(self):
        template = self.pool.get('res.partner').search(self.env.cr, self.env.uid, [('doc_number', '=', str(self.ruc))])
        if template:
            self.partner_id = template[0]



    @api.multi
    def custom_validate_tasks(self, context=None):
        global typo
        global serie
        global nombre
        for inv in self:
            if inv.internal_number:
                bandera = 1
            else:
                bandera = 0
            res = inv.onchange_payment_term_date_invoice(inv.payment_term.id, inv.date_invoice)
            if res and res.get('value'):
                inv.write(res['value'])

        factura_ultima = self.search([['es_boleta','=',False],['internal_number','!=', None],['type','=', 'out_invoice']], limit=1, order = 'internal_number desc')
        if factura_ultima:
            print (factura_ultima.internal_number)
            num_factura_ultima = factura_ultima.internal_number.split('-')
            num_factura_ultima = int(num_factura_ultima[1]) + 1
            seque = self.env['ir.sequence'].search([['code','=','factura.secue']])
            # # raise Warning(num_factura_ultima)
            # if int(self.journal_id.code) == 1:
            #     if int(seque.number_next_actual) == 384:
            #         raise Warning('Error!!!',
            #                       'Porfavor comunicarse con el administrador del Sistema Gracias')
            if int(self.journal_id.code) == 1:
                if int(seque.number_next_actual) != int(num_factura_ultima):
                    raise Warning('Aviso!!!', 'Porfavor revise la numeración de las facturas deberia ser %s y esta en %s' % (int(num_factura_ultima),int(seque.number_next_actual)))
            #         print ('Aviso!!! Porfavor revise la numeración de las facturas deberia ser %s y esta en %s' % (int(num_factura_ultima),int(seque.number_next_actual)))

        # raise Warning('stop')
        # return True
        cur_date = datetime.datetime.now().date()
        # cur_date_mas_7 = datetime.datetime.now().date() + datetime.timedelta(days=7)
        new_date = dateutil.parser.parse(self.date_invoice).date() + datetime.timedelta(days=7)
        # fech_em = dateutil.parser.parse(self.date_invoice).date()
        if bandera != 1:
            if new_date < cur_date:
                raise except_orm(_('Aviso de validacion!'),
                                 _('Usted ya no puede validar la factura ya que han pasado 7 dias. Esto segun SUNAT : %s') % 'www.sunat.com')

        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        self.env.cr.execute("SELECT count(id) "
                            "FROM account_invoice "
                            "WHERE create_date "
                            "BETWEEN (SELECT date_trunc('month',current_date) - '1month' ::INTERVAL) "
                            "AND (SELECT date_trunc('month',current_date) -'1sec' ::INTERVAL)")
        data = self.env.cr.fetchall()
        # print('>>>>>>>>>>>>'+str(data))
        if len(data) == 0:
            raise osv.except_osv(_('Error!'), _("No Existen Comprobantes en el mes anterior"))

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if not inv.invoice_ids:
                raise except_orm(_('No hay Lineas de Conceptos tributarios!'),
                                 _('Porfavor cree al menos un concepto tributario.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            company_currency = inv.company_id.currency_id
            if not inv.date_invoice:
                # FORWARD-PORT UP TO SAAS-6
                if inv.currency_id != company_currency and inv.tax_line:
                    raise except_orm(
                        _('Warning!'),
                        _('No invoice date!'
                          '\nThe invoice currency is not the same than the company currency.'
                          ' An invoice date is required to determine the exchange rate to apply. Do not forget to update the taxes!'
                          )
                    )
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (
                            inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _(
                        'Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _(
                        "Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # Force recomputation of tax_amount, since the rate potentially changed between creation
            # and validation of the invoice
            # inv._recompute_tax_amount()
            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # print ('ssssssssssssss',str(iml))
            # raise Warning('dddddddd')
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            print ('total', str(total))
            # print ('iml',str(iml))
            print ('total_currency', str(total_currency))
            print ('--------------------------------------------')
            # if self.detraccion_cliente:
            #     monto_detraccion_soles = (self.detraccion_cliente / inv.currency_id.rate) or 0.0
            #     total = total - monto_detraccion_soles
            #     total_currency = total_currency - self.detraccion_cliente or 0.0
            #     print ('monto_detraccion_soles',str(monto_detraccion_soles))
            #     print ('total',str(total))
            #     # print ('iml',str(iml))
            #     print ('total_currency',str(total_currency))
            #     raise Warning('dddddddd')

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    # print ('ssssssssssfffffffffffssss', str(amount_currency))
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                # print ('sssssscffssssssss', str(total_currency))
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })


            date = date_invoice
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            # print (iml)
            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]

            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                                 _(
                                     'You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)
            # print (line)
            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }

            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        # return True

        self.write({})

        for inv in self:
            self.write({'internal_number': inv.number})

            tipo = inv.type

            if inv.type in ('in_invoice', 'in_refund'):
                if not inv.reference:
                    ref = inv.number
                else:
                    ref = inv.reference
            else:
                ref = inv.number

            self._cr.execute(""" UPDATE account_move SET ref=%s
                                   WHERE id=%s AND (ref IS NULL OR ref = '')""",
                             (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_move_line SET ref=%s
                                   WHERE move_id=%s AND (ref IS NULL OR ref = '')""",
                             (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_move_line SET type=%s
                                   WHERE move_id=%s """,
                             (tipo, inv.move_id.id))
            self._cr.execute(""" UPDATE account_analytic_line SET ref=%s
                                   FROM account_move_line
                                   WHERE account_move_line.move_id = %s AND
                                         account_analytic_line.move_id = account_move_line.id""",
                             (ref, inv.move_id.id))
            self.invalidate_cache()

        # return True
        if bandera == 1:
            avc = self.env['warning_box'].info(title='Enviar a SUNAT', message="Comprobante Validado")
            ai = super(account_invoice, self).invoice_validate()
            self.write({'state':'open'})
        else:
            avc = self.env['warning_box'].info(title='Enviar a SUNAT', message="Usted debe enviar el documento electrónico a la Sunat.")
            ai = super(account_invoice, self).invoice_validate()
            self.write({'state': 'enviar_sunat'})
        return avc


    @api.multi
    def action_enviar_sunat(self, context=None):
        # ne = datetime.datetime.now()
        # cur_date = datetime.datetime.now().date()
        # new_date1 = dateutil.parser.parse(self.date_invoice).date()
        # a = self.search([('state', '=', 'open'),('date_invoice','<=',(cur_date-datetime.timedelta(days=7)).strftime('%Y-%m-%d'))])
        # raise Warning(a)
        cur_date = datetime.datetime.now().date()
        # cur_date_mas_7 = datetime.datetime.now().date() + datetime.timedelta(days=7)
        new_date = dateutil.parser.parse(self.date_invoice).date() + datetime.timedelta(days=7)
        # fech_em = dateutil.parser.parse(self.date_invoice).date()
        if new_date < cur_date:
            print 'Usted ya no puede validar la factura ya que han pasado 7 dias. Esto segun SUNAT : %s' % 'www.sunat.com'

        user_obj = self.pool.get('res.users')
        user = user_obj.browse(self.env.cr, self.env.uid, self.env.uid, context=context)
        if user.company_id.x_ruc and user.company_id.name and user.company_id.partner_id.street and user.company_id.partner_id.city and user.company_id.country_id.code and user.company_id.partner_id.zip:
            ruc = user.company_id.x_ruc
            nombreEmpresa = user.company_id.name
            direccion = user.company_id.partner_id.street
            ciudad = user.company_id.partner_id.city
            codigo_code = user.company_id.partner_id.country_id.code
            zip_company = user.company_id.partner_id.zip
        else:
            raise except_orm(_('Error!'), _('Porfavor llene los datos de su Empresa Gracias!'))

        # ruc = self.pool.get('res.company').browse(self.env.cr, self.env.uid, self.env.uid, context=context)
        # nombreEmpresa = self.pool.get('res.company').browse(self.env.cr, self.env.uid, self.env.uid,context=context)

        print (ruc, nombreEmpresa)


        base_dir = r'd:/'
        abc_zip = base_dir + str(ruc) + '-01-' + str(self.number) + '.zip'
        abc_zip_b = base_dir + str(ruc) + '-03-' + str(self.number) + '.zip'
        abc_xml = base_dir + str(ruc) + '-01-' + str(self.number) + '.xml'
        abc_xml_b = base_dir + str(ruc) + '-03-' + str(self.number) + '.xml'
        # print('Eliminandoooo...ZIP111', str(abc_zip))
        # print('Eliminandoooo... XML1111', str(abc_xml))
        if os.path.isfile(abc_zip):
            # print('Eliminandoooo...ZIP', str(abc_zip))
            os.remove(abc_zip)
        if os.path.isfile(abc_xml):
            # print('Eliminandoooo... XML', str(abc_xml))
            os.remove(abc_xml)

        if os.path.isfile(abc_zip_b):
            print('Eliminandoooo...ZIP', str(abc_zip_b))
            os.remove(abc_zip_b)
        if os.path.isfile(abc_xml_b):
            print('Eliminandoooo... XML', str(abc_xml_b))
            os.remove(abc_xml_b)

        # raise Warning('elimsmsmms')

        # partner_id = self.env['account.invoice'].browse(self.id)

        for invoice in self.env['account.invoice'].browse(self.id):
            partner_id = invoice.partner_id
            # p = self.pool.get('res.partner').browse(self.env.cr, partner_id, context=context).name

            idadicional = ''
            count = 0
            if int(invoice.journal_id.code) == 3:
                typo = '03'
                serie = 'BB'
                idadicional = '1'

            elif int(invoice.journal_id.code) == 1:
                if partner_id.parent_id:
                    if str(partner_id.parent_id.doc_type) == 'dni':
                        raise except_orm(('Error!'), ('No se puede generar comprobante: el cliente no tiene RUC'))
                    else:
                        typo = '01'
                        serie = 'FF'
                        idadicional = '6'
                elif str(partner_id.doc_type) == 'dni':
                    raise except_orm(('Error!'), ('No se puede generar comprobante: el cliente no tiene RUC'))
                else:
                    typo = '01'
                    serie = 'FF'
                    idadicional = '6'

            correlativo = invoice.number.split('-')
            print ('>>>>>correlativo>>>>', str(correlativo))

            self.write({'monto_letras': str(self.numero_to_letras(invoice.amount_total))})

            # a = inicio()
            c = firmandoXML()
            d = UBLVersion()
            n = customizationID()
            o = id(correlativo[0], correlativo[1])
            e = issueDate(str(invoice.date_invoice))
            g = invoiceTypeCode(typo)
            h = documentCurrencyCode(str(invoice.currency_id.name))
            i = declaracionFirma(ruc, ruc, nombreEmpresa, 'SIGN')
            j = DatosProveedor(ruc, '6', elimina_tildes(str(nombreEmpresa).decode('utf-8')), str(zip_company), elimina_tildes(str(direccion).decode('utf-8')),str(ciudad), str(ciudad), str(ciudad), 'nombreRegistro', str(codigo_code))
            if partner_id.parent_id:
                k = DatosCliente(str(partner_id.parent_id.doc_number), idadicional, elimina_tildes(str(partner_id.parent_id.name).decode('utf-8')))
            else:
                k = DatosCliente(str(partner_id.doc_number), idadicional, elimina_tildes(str(partner_id.name).decode('utf-8')))
            l = sumatoriaIGV(str(invoice.amount_tax), '1000', str(invoice.currency_id.name))
            q = importeTotal(str(invoice.amount_untaxed_global_discount), str(invoice.amount_total),
                             str(invoice.currency_id.name))

            nombre = self.generate_document_name(ruc, int(invoice.journal_id.code), correlativo[1])
            f = open(nombre, 'w')
            xm = doc.toprettyxml()
            xm = xm.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?>')
            f.write(xm)
            f.write(
                '<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sac="urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')
            f.write('<ext:UBLExtensions>\n')
            f.write('<ext:UBLExtension>\n')
            f.write('<ext:ExtensionContent>\n')
            f.write('<sac:AdditionalInformation>\n')
            for conceptos in invoice.invoice_ids:
                b = pago(str(conceptos.conceptos_tributarios.code),
                         str(conceptos.monto_total),
                         str(invoice.currency_id.name))
                f.write(b)

            # esto convertir a dinamico mas adelante
            for conceptos in invoice.invoice_ids:
                print ('>>>>>>', str(conceptos.conceptos_tributarios.code))
                if '1004' in conceptos.conceptos_tributarios.code:
                    ad = '1002'
                    adici = 'Artículos gratuitos'
                else:
                    ad = '1000'
                    adici = self.numero_to_letras(invoice.amount_total)

            f.write('<sac:AdditionalProperty>\n<cbc:ID>' + str(ad) + '</cbc:ID>\n<cbc:Value>' + str(
                adici) + '</cbc:Value>\n</sac:AdditionalProperty>\n')
            f.write('</sac:AdditionalInformation>\n')
            f.write('</ext:ExtensionContent>\n')
            f.write('</ext:UBLExtension>\n')
            f.write(c)
            f.write('</ext:UBLExtensions>\n')
            f.write(d)
            f.write(n)
            f.write(o)
            f.write(e)
            f.write(g)
            f.write(h)
            f.write(i)
            f.write(j)
            f.write(k)
            f.write(l)
            f.write(q)
            for line in invoice.invoice_line:
                count += 1
                unidad_medidad = str(line.uos_id.code) if line.uos_id.code else 'NIU'
                print (str(unidad_medidad))
                m = Producto(str(count),
                             str(unidad_medidad),
                             str(line.quantity),
                             str(line.price_subtotal),
                             str(round((line.price_subtotal * 0.18), 2)),
                             str(line.product_id.name),
                             '00' + str(line.product_id.id),
                             str(line.price_unit),
                             str(line.product_id.name),
                             '1000',
                             str(line.afectacion_igv.code),
                             str(invoice.currency_id.name))
                f.write(m)
            f.write('</Invoice>')
            f.close()

            r = Probando()
            valor_resumen = r.sign_xml(fichero_xml=nombre)

            self.write({'digest_value': str(valor_resumen)})

            base_dir = r'd:/'
            filename = ruc + '-' + typo + '-' + correlativo[0] + '-' + correlativo[1] + '.zip'
            # filename = ruc + '-' + '001-1.ZIP'

            base_dir_r = r'd:/'
            filename_R = 'R-' + ruc + '-' + typo + '-' + correlativo[0] + '-' + correlativo[1] + '.zip'

            zf = zipfile.ZipFile(os.path.join(base_dir, filename), mode='w')
            # zf.writestr(zipfile.ZipInfo('dummy/'), '')
            zf.write(nombre)
            zf.close()


            idModel = self.pool.get('ir.model').search(self.env.cr, self.env.uid,
                                                    [('model', '=', 'account.invoice')])
            idTemplate = self.pool.get('ir.actions.report.xml').search(self.env.cr, self.env.uid,
                                                    [('name', '=', 'Factura SF')])
            idValue = self.pool.get('ir.values').search(self.env.cr, self.env.uid,
                                                    [('name', '=', 'Factura SF')])

            template = self.pool.get('email.template')
            attachment_obj = self.pool.get('ir.attachment')
            imagen_firma = attachment_obj.search(self.env.cr, self.env.uid,[('name', '=', 'firma_correos')])
            # raise Warning(imagen_firma[0])
            # prefix = this.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field: 'name'});

            if self.es_boleta:
                document = 'Boleta'
            else:
                document = 'Factura'
            valsMail = \
                {'name': invoice.number
                    , 'auto_delete': True
                    , 'partner_to': '${object.partner_id.id}'
                 # , 'ref_ir_act_window': 668
                    , 'subject': '${object.company_id.name|safe} %s (Ref ${object.number or \'n/a\'})' % document
                    # , 'subject': '${object.company_id.name|safe} Factura (Ref ${object.number or \'n/a\'})'
                    , 'report_template': idTemplate[0]
                    , 'ref_ir_value': idValue[0]
                    , 'user_signature': False
                    , 'model_id': idModel[0]
                    , 'lang': '${object.partner_id.lang}'
                    , 'report_name': '%s_${(object.number or \'\').replace(\'/\',\'_\')}_${object.state == \'draft\' and \'draft\' or \'\'}' % document
                    , 'use_default_to': False
                    , 'model': 'account.invoice'
                    , 'email_from': '${(object.user_id.email or object.company_id.email or \'noreply@localhost\')|safe}'
                    ,
                 'body_html': '<div style="font-family: \'Lucica Grande\', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; "> \n <p>Sr(es). \n % if object.partner_id.parent_id: \n ${object.partner_id.parent_id.name} \n % else: \n ${object.partner_id.name} \n % endif \n </p> \n <p>Hay una nueva '+str(document)+' disponible para usted: </p> \n <p style="border-left: 1px solid #8e0000; margin-left: 30px;"> \n &nbsp;&nbsp;<strong>REFERENCIAS</strong><br> \n &nbsp;&nbsp;'+str(document)+': <strong>${object.number}</strong><br> \n &nbsp;&nbsp;Total: <strong>${object.amount_total} ${object.currency_id.name}</strong><br> \n &nbsp;&nbsp;Fecha: ${object.date_invoice.split(\'-\')[2] + \'/\' + object.date_invoice.split(\'-\')[1] + \'/\' + object.date_invoice.split(\'-\')[0]}<br> \n % if object.origin: \n  &nbsp;&nbsp;Origen: ${object.origin}<br> \n % endif \n </p> \n % if object.paypal_url: \n <br> \n <p>También es posible realizar el pago directamente con Paypal:</p> \n <a style="margin-left: 120px;" href="${object.paypal_url}"> \n <img class="oe_edi_paypal_button" src="/account/static/src/img/btn_paynowcc_lg.gif"> \n </a> \n % endif \n <br> \n <p>Si tiene cualquier pregunta, no dude en contactarnos.</p> \n <img src="/web/binary/image?model=ir.attachment&amp;field=datas&amp;id=1763&amp;resize=850,150" title=""> \n <br/> Realizado por <a href="http://www.scientechperu.com" target="_blank">Scientech S.R.L</a></div>'}
                 #    ,
                 # 'body_html': '<div style="font-family: \'Lucica Grande\', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; "> \n <p>Sr(es). \n % if object.partner_id.parent_id: \n ${object.partner_id.parent_id.name} \n % else: \n ${object.partner_id.name} \n % endif \n </p> \n <p>Hay una nueva '+str(document)+' disponible para usted: </p> \n <p style="border-left: 1px solid #8e0000; margin-left: 30px;"> \n &nbsp;&nbsp;<strong>REFERENCIAS</strong><br> \n &nbsp;&nbsp;'+str(document)+': <strong>${object.number}</strong><br> \n &nbsp;&nbsp;Total: <strong>${object.amount_total} ${object.currency_id.name}</strong><br> \n &nbsp;&nbsp;Fecha: ${object.date_invoice.split(\'-\')[2] + \'/\' + object.date_invoice.split(\'-\')[1] + \'/\' + object.date_invoice.split(\'-\')[0]}<br> \n % if object.origin: \n  &nbsp;&nbsp;Origen: ${object.origin}<br> \n % endif \n </p> \n % if object.paypal_url: \n <br> \n <p>También es posible realizar el pago directamente con Paypal:</p> \n <a style="margin-left: 120px;" href="${object.paypal_url}"> \n <img class="oe_edi_paypal_button" src="/account/static/src/img/btn_paynowcc_lg.gif"> \n </a> \n % endif \n <br> \n <p>Si tiene cualquier pregunta, no dude en contactarnos.</p> \n <p>Gracias por elegir ${object.company_id.name or \'nos\'}</p> \n <br> \n <br> \n <div style="width: 375px; margin: 0px; padding: 0px; background-color: #8E0000; border-top-left-radius: 5px 5px; border-top-right-radius: 5px 5px; background-repeat: repeat no-repeat;"> \n <h3 style="margin: 0px; padding: 2px 14px; font-size: 12px; color: #DDD;"> \n <strong style="text-transform:uppercase;">${object.company_id.name}</strong></h3> \n </div> \n <div style="width: 347px; margin: 0px; padding: 5px 14px; line-height: 16px; background-color: #F2F2F2;"> \n <span style="color: #222; margin-bottom: 5px; display: block; "> \n % if object.company_id.street: \n ${object.company_id.street}<br> \n % endif \n % if object.company_id.street2: \n ${object.company_id.street2}<br> \n  % endif \n % if object.company_id.city or object.company_id.zip: \n ${object.company_id.zip} ${object.company_id.city}<br> \n % endif \n  % if object.company_id.country_id: \n ${object.company_id.state_id and (\'%s, \' % object.company_id.state_id.name) or \'\'} ${object.company_id.country_id.name or \'\'}<br> \n % endif \n </span> \n % if object.company_id.phone: \n <div style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; "> \n  Teléfono:&nbsp; ${object.company_id.phone} \n </div> \n % endif \n % if object.company_id.website: \n <div> \n Web :&nbsp;<a href="${object.company_id.website}">${object.company_id.website}</a> \n </div> \n %endif \n <p></p> \n </div> \n </div>'}

            resMail = template.create(self.env.cr, self.env.uid, valsMail, context=context)

            # raise Warning(resMail)
            f_e = open(os.path.join(base_dir, filename), 'rb')
            data_file = f_e.read()

            vals = \
                {'name': filename
                    , 'datas': base64.b64encode(str(data_file))
                    , 'datas_fname': filename
                    , 'res_model': 'account.invoice'
                    , 'type': 'binary'
                    , 'res_id': invoice.id
                    , 'description': False
                 }
            res = attachment_obj.create(self.env.cr, self.env.uid, vals, context=context)

            self._cr.execute(""" INSERT INTO email_template_attachment_rel(email_template_id, attachment_id)
                                                       VALUES(%s, %s)""",
                             (resMail, res))
            f_e.close()

            base_dir_valorizacion = r'c:\\xampp\htdocs\valorizaciones\valorizaciones'
            filename_valorizacion = 'Valorizacion_' + str(invoice.id) + '.pdf'
            if (os.path.exists(os.path.join(base_dir_valorizacion, filename_valorizacion))):
                f_valorizacion = open(os.path.join(base_dir_valorizacion, filename_valorizacion), 'rb')
                data_valorizacion = f_valorizacion.read()

                attachment_obj = self.pool.get('ir.attachment')
                vals = \
                    {'name': filename_valorizacion
                        , 'datas': base64.b64encode(str(data_valorizacion))
                        , 'datas_fname': filename_valorizacion
                        , 'res_model': 'account.invoice'
                        , 'type': 'binary'
                        , 'res_id': invoice.id
                        , 'description': False
                     }
                res = attachment_obj.create(self.env.cr, self.env.uid, vals, context=context)

                self._cr.execute(""" INSERT INTO email_template_attachment_rel(email_template_id, attachment_id)
                                                                       VALUES(%s, %s)""",
                                 (resMail, res))
                f_valorizacion.close()

            ws = webService()
            print (base_dir_r, filename_R, filename, base_dir)
            ws.consumir(os.path.join(base_dir, filename), os.path.join(base_dir_r, filename_R), filename)

            f_e = open(os.path.join(base_dir_r, filename_R), 'rb')
            data_file = f_e.read()
            attachment_obj = self.pool.get('ir.attachment')
            vals = \
                {'name': 'R' + filename
                    , 'datas': base64.b64encode(str(data_file))
                    , 'datas_fname': 'R' + filename
                    , 'res_model': 'account.invoice'
                    , 'type': 'binary'
                    , 'res_id': invoice.id
                    , 'description': False
                 }
            res = attachment_obj.create(self.env.cr, self.env.uid, vals, context=context)

            self._cr.execute(""" INSERT INTO email_template_attachment_rel(email_template_id, attachment_id)
                                                                   VALUES(%s, %s)""",
                             (resMail, res))
            f_e.close()

            # Actualizar el estado del tareo de los clientes al momento de validar la factura
            self._cr.execute("""UPDATE modulo_valorizaciones_tareo_mensual SET estado=%s WHERE n_factura=%s""",
                             ('Facturado', invoice.id))

            bar = BarCo()
            imagen = bar.generate_image(str(valor_resumen.encode(encoding="ISO-8859-1").strip()))
            # print (imagen)z
            self.write({'image_bar': imagen})

            # leer el cdr y sacr el mensaje que trae
            dir_rep = base_dir + '' + filename_R
            zipe = zipfile.ZipFile(dir_rep)
            cortando2 = dir_rep.replace('.zip', '.xml')
            cortando3 = cortando2.replace(base_dir, '')
            file = zipe.read(cortando3)
            g = file.find('<cbc:ResponseCode>')
            f = file.find('</cbc:ResponseCode>')
            cadena = file[g + 18:f]
            zipe.close()

            if int(cadena) == 0:
                ge = file.find('<cbc:Description>')
                fe = file.find('</cbc:Description>')
                cadena2 = file[ge + 17:fe]
                print (cadena2)
                self.write({'mensaje_cdr': str(cadena2)})
                return self.write({'enviado_sunat': True, 'state': 'open'})
            else:
                errores = self.env['catalogo.errores.sunat'].search([['code', '=', int(cadena)]])
                if 2000 <= int(cadena) <= 3999:
                    if errores.name:
                        print (errores.name)
                        obj_move = self.env['account.move'].search([['id', '=', self.move_id.id]])
                        obj_move.button_cancel()
                        self.write({'move_id': ''})
                        obj_move.unlink()
                        obj_move_line = self.env['account.move.line'].search([['id', '=', self.move_id.id]])
                        for line in obj_move_line:
                            line.unlink()

                        self.write({'mensaje_cdr': str(errores.name)})
                        return self.write({'enviado_sunat': True, 'state': 'error_rechazo'})
                        # raise Warning(str(errores.name))
                        # self.write({'mensaje_cdr': str(errores.name)})

        # print ('openopenopenopenopenopenopenopen')


    @api.multi
    def action_invoice_sent(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.pool.get('email.template').search(self.env.cr, self.env.uid, [('name', '=', str(self.number))])
        # template = self.env.ref('account.email_template_edi_invoice', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)

        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_new_template_id=template[0],
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        print (ctx)
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        # return super(account_invoice, self).action_invoice_sent()

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'account.report_without_prices')

    def generate_document_name(self, ruc, doc_type, correlativo):
        """
        Tipo de comprobante
        01: Factura electronica
        03: Boleta de venta
        07: Nota de credito
        08: Nota de debito
        Serie del comprobante
        FAAA: Facturas
        BAAA: Boletas
        """
        id_account = self.env['account.invoice'].browse(self.id)
        typo = ''
        serie = ''
        if doc_type == 3:
            typo = '03'
            serie = id_account.journal_id.sequence_id.prefix
            # serie = 'BB'
        elif doc_type == 1:
            typo = '01'
            serie = id_account.journal_id.sequence_id.prefix
            # serie = 'FF'

        base_dir = r'd:/'
        filename = ruc + '-' + typo + '-' + serie + correlativo + '.xml'

        # TODO: Add types as constants in diferent classes
        return os.path.join(base_dir, filename)

    def numero_to_letras(self, numero):
        indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero) * 100))
        # print 'decimal : ',decimal
        contador = 0
        numero_letras = ""
        while entero > 0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a, 1).strip()
            else:
                en_letras = self.convierte_cifra(a, 0).strip()
            if a == 0:
                numero_letras = en_letras + " " + numero_letras
            elif a == 1:
                if contador in (1, 3):
                    numero_letras = indicador[contador][0] + " " + numero_letras
                else:
                    numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras + " con " + str(decimal) + "/100"
        # print 'numero: ', numero
        return numero_letras

    def convierte_cifra(self, numero, sw):
        lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                         "SEISCIENTOS",
                         "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        lista_decena = ["", (
            "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        lista_unidad = ["CERO", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        centena = int(numero / 100)
        decena = int((numero - (centena * 100)) / 10)
        unidad = int(numero - (centena * 100 + decena * 10))
        # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""

        # Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad) != 0:
                texto_centena = texto_centena[1]
            else:
                texto_centena = texto_centena[0]

        # Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1:
            texto_decena = texto_decena[unidad]
        elif decena > 1:
            if unidad != 0:
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        # Validar las unidades
        # print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]

        return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)


def inicio():
    root = doc.createElement('Invoice')
    doc.appendChild(root)
    root.setAttribute('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2')
    root.setAttribute('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
    root.setAttribute('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
    root.setAttribute('xmlns:ccts', 'urn:un:unece:uncefact:documentation:2')
    root.setAttribute('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
    root.setAttribute('xmlns:ext', 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2')
    root.setAttribute('xmlns:qdt', 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2')
    root.setAttribute('xmlns:sac', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1')
    root.setAttribute('xmlns:udt', 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2')
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    xml_str = doc.toprettyxml(indent="  ")
    return xml_str


def pago(id1, monto,currency):
    sacAdditionalMonetaryTotal = doc.createElement('sac:AdditionalMonetaryTotal')
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(id1)
    cbcID.appendChild(text)
    sacAdditionalMonetaryTotal.appendChild(cbcID)
    cbcPayableAmount = doc.createElement('cbc:PayableAmount')
    cbcPayableAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcPayableAmount.appendChild(text)
    sacAdditionalMonetaryTotal.appendChild(cbcPayableAmount)
    xml_str = sacAdditionalMonetaryTotal.toprettyxml(indent="  ")
    return xml_str


# def pago(numero, id1, total, concepto):
# # extUBLExtensions = doc.createElement('ext:UBLExtensions')
# extUBLExtension = doc.createElement('ext:UBLExtension')
# # extUBLExtensions.appendChild(extUBLExtension)
# extExtensionContent = doc.createElement('ext:ExtensionContent')
# extUBLExtension.appendChild(extExtensionContent)
# sacAdditionalInformation = doc.createElement('sac:AdditionalInformation')
# extExtensionContent.appendChild(sacAdditionalInformation)
# while numero >= 1:
#     id = concepto
#     pago = id1
#     sacAdditionalMonetaryTotal = doc.createElement('sac:AdditionalMonetaryTotal')
#     cbcID = doc.createElement('cbc:ID')
#     text = doc.createTextNode(id)
#     cbcID.appendChild(text)
#     sacAdditionalMonetaryTotal.appendChild(cbcID)
#     cbcPayableAmount = doc.createElement('cbc:PayableAmount')
#     cbcPayableAmount.setAttribute('currencyID', 'PEN')
#     text = doc.createTextNode(pago)
#     cbcPayableAmount.appendChild(text)
#     sacAdditionalMonetaryTotal.appendChild(cbcPayableAmount)
#     sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal)
#     numero = numero - 1
# sacAdditionalProperty = doc.createElement('sac:AdditionalProperty')
# sacAdditionalInformation.appendChild(sacAdditionalProperty)
# cbcID = doc.createElement('cbc:ID')
# text = doc.createTextNode('1000')
# cbcID.appendChild(text)
# sacAdditionalProperty.appendChild(cbcID)
# cbcValue = doc.createElement('cbc:Value')
# text = doc.createTextNode(total)
# cbcValue.appendChild(text)
# sacAdditionalProperty.appendChild(cbcValue)
# xml_str = extUBLExtension.toprettyxml(indent="  ")
# return xml_str


def firmandoXML():
    extUBLExtension = doc.createElement('ext:UBLExtension')
    extExtensionContent = doc.createElement('ext:ExtensionContent')
    text = doc.createTextNode('')
    extExtensionContent.appendChild(text)
    extUBLExtension.appendChild(extExtensionContent)

    xml_str = extUBLExtension.toprettyxml(indent="  ")
    return xml_str


def declaracionFirma(id, identificacion, nombre, firma):
    cacSignature = doc.createElement('cac:Signature')
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(id)
    cbcID.appendChild(text)
    cacSignature.appendChild(cbcID)
    cacSignatoreParty = doc.createElement('cac:SignatoryParty')
    cacSignature.appendChild(cacSignatoreParty)
    cacPartyIdentification = doc.createElement('cac:PartyIdentification')
    cacSignatoreParty.appendChild(cacPartyIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacPartyIdentification.appendChild(cbcID)
    cacPartyName = doc.createElement('cac:PartyName')
    cacSignatoreParty.appendChild(cacPartyName)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode(nombre)
    # text = doc.createCDATASection(nombre)
    cbcName.appendChild(text)
    cacPartyName.appendChild(cbcName)
    cacDigitalSignatureAttachment = doc.createElement('cac:DigitalSignatureAttachment')
    cacSignature.appendChild(cacDigitalSignatureAttachment)
    cacExternalReference = doc.createElement('cac:ExternalReference')
    cacDigitalSignatureAttachment.appendChild(cacExternalReference)
    cbcURI = doc.createElement('cbc:URI')
    text = doc.createTextNode(firma)
    cbcURI.appendChild(text)
    cacExternalReference.appendChild(cbcURI)
    xml_str = cacSignature.toprettyxml(indent="  ")
    return xml_str


def DatosProveedor(id, idAdicional, nombre, idDireccion, nombreCalle, nombreCiudad, nombreDepartamento,
                   nombreDistrito, nombreRegistro, codigoID):
    cacAccountingSupplierParty = doc.createElement('cac:AccountingSupplierParty')
    cbcCustomerAssignedAccountID = doc.createElement('cbc:CustomerAssignedAccountID')
    text = doc.createTextNode(id)
    cbcCustomerAssignedAccountID.appendChild(text)
    cacAccountingSupplierParty.appendChild(cbcCustomerAssignedAccountID)
    cbcAdditionalAccountID = doc.createElement('cbc:AdditionalAccountID')
    text = doc.createTextNode(idAdicional)
    cbcAdditionalAccountID.appendChild(text)
    cacAccountingSupplierParty.appendChild(cbcAdditionalAccountID)
    cacParty = doc.createElement('cac:Party')
    cacAccountingSupplierParty.appendChild(cacParty)
    cacPartyName = doc.createElement('cac:PartyName')
    cacParty.appendChild(cacPartyName)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode(nombre)
    # text = doc.createCDATASection(nombre)
    cbcName.appendChild(text)
    cacPartyName.appendChild(cbcName)
    cacPostalAddress = doc.createElement('cac:PostalAddress')
    cacParty.appendChild(cacPostalAddress)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idDireccion)
    cbcID.appendChild(text)
    cacPostalAddress.appendChild(cbcID)
    cbcStreetName = doc.createElement('cbc:StreetName')
    text = doc.createTextNode(nombreCalle)
    cbcStreetName.appendChild(text)
    cacPostalAddress.appendChild(cbcStreetName)
    cbcCitySubdivisionName = doc.createElement('cbc:CitySubdivisionName')
    text = doc.createTextNode(' ')
    cbcCitySubdivisionName.appendChild(text)
    cacPostalAddress.appendChild(cbcCitySubdivisionName)
    cbcCityName = doc.createElement('cbc:CityName')
    text = doc.createTextNode(nombreCiudad)
    cbcCityName.appendChild(text)
    cacPostalAddress.appendChild(cbcCityName)
    cbcCountrySubentity = doc.createElement('cbc:CountrySubentity')
    text = doc.createTextNode(nombreDepartamento)
    cbcCountrySubentity.appendChild(text)
    cacPostalAddress.appendChild(cbcCountrySubentity)
    cbcDistrict = doc.createElement('cbc:District')
    text = doc.createTextNode(nombreDistrito)
    cbcDistrict.appendChild(text)
    cacPostalAddress.appendChild(cbcDistrict)
    cacCountry = doc.createElement('cac:Country')
    cacPostalAddress.appendChild(cacCountry)
    cbcIdentificationCode = doc.createElement('cbc:IdentificationCode')
    text = doc.createTextNode(codigoID)
    cbcIdentificationCode.appendChild(text)
    cacCountry.appendChild(cbcIdentificationCode)
    cacPartyLegalEntity = doc.createElement('cac:PartyLegalEntity')
    cacParty.appendChild(cacPartyLegalEntity)
    cbcRegistrationName = doc.createElement('cbc:RegistrationName')
    text = doc.createTextNode(nombre)
    # text = doc.createCDATASection(nombre)
    cbcRegistrationName.appendChild(text)
    cacPartyLegalEntity.appendChild(cbcRegistrationName)
    xml_str = cacAccountingSupplierParty.toprettyxml(indent="  ")
    return xml_str


def UBLVersion():
    UBLVersion = doc.createElement('cbc:UBLVersionID')
    text = doc.createTextNode('2.0')
    UBLVersion.appendChild(text)
    xml_str = UBLVersion.toprettyxml(indent="  ")
    return xml_str


def customizationID():
    cbcCustomizationID = doc.createElement('cbc:CustomizationID')
    text = doc.createTextNode('1.0')
    cbcCustomizationID.appendChild(text)
    xml_str = cbcCustomizationID.toprettyxml(indent="  ")
    return xml_str


def id(serie, correlativo):
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(serie + '-' + correlativo)
    cbcID.appendChild(text)
    xml_str = cbcID.toprettyxml(indent="  ")
    return xml_str


def issueDate(fecha):
    cbcIssueDate = doc.createElement('cbc:IssueDate')
    text = doc.createTextNode(fecha)
    cbcIssueDate.appendChild(text)
    xml_str = cbcIssueDate.toprettyxml(indent="  ")
    return xml_str


def invoiceTypeCode(tipo):
    cbcInvoiceTypeCode = doc.createElement('cbc:InvoiceTypeCode')
    text = doc.createTextNode(tipo)
    cbcInvoiceTypeCode.appendChild(text)
    xml_str = cbcInvoiceTypeCode.toprettyxml(indent="  ")
    return xml_str


def documentCurrencyCode(currency):
    cbcDocumentCurrencyCode = doc.createElement('cbc:DocumentCurrencyCode')
    text = doc.createTextNode(currency)
    cbcDocumentCurrencyCode.appendChild(text)
    xml_str = cbcDocumentCurrencyCode.toprettyxml(indent="  ")
    return xml_str


def DatosCliente(id, idAdicional, nombre):
    cacAccountingCustomerParty = doc.createElement('cac:AccountingCustomerParty')
    cbcCustomerAssignedAccountID = doc.createElement('cbc:CustomerAssignedAccountID')
    text = doc.createTextNode(id)
    cbcCustomerAssignedAccountID.appendChild(text)
    cacAccountingCustomerParty.appendChild(cbcCustomerAssignedAccountID)
    cbcAdditionalAccountID = doc.createElement('cbc:AdditionalAccountID')
    text = doc.createTextNode(idAdicional)
    cbcAdditionalAccountID.appendChild(text)
    cacAccountingCustomerParty.appendChild(cbcAdditionalAccountID)
    cacParty = doc.createElement('cac:Party')
    cacAccountingCustomerParty.appendChild(cacParty)
    cacPartyLegalEntity = doc.createElement('cac:PartyLegalEntity')
    cacParty.appendChild(cacPartyLegalEntity)
    cbcRegistrationName = doc.createElement('cbc:RegistrationName')
    text = doc.createTextNode(nombre)
    cbcRegistrationName.appendChild(text)
    cacPartyLegalEntity.appendChild(cbcRegistrationName)
    xml_str = cacAccountingCustomerParty.toprettyxml(indent="  ")
    return xml_str


def sumatoriaIGV(monto, idtax, currency):
    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idtax)
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('IGV')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('VAT')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)
    xml_str = cacTaxTotal.toprettyxml(indent="  ")
    return xml_str


def importeTotal(montoDesc, monto, currency):
    cacLegalMonetaryTotal = doc.createElement('cac:LegalMonetaryTotal')
    print ('>>>>>' + str(montoDesc))
    if montoDesc == '0.0':
        cbcPayableAmount = doc.createElement('cbc:PayableAmount')
        cbcPayableAmount.setAttribute('currencyID', currency)
        text = doc.createTextNode(monto)
        cbcPayableAmount.appendChild(text)
        cacLegalMonetaryTotal.appendChild(cbcPayableAmount)
    else:
        cbcAllowanceTotalAmount = doc.createElement('cbc:AllowanceTotalAmount')
        cbcAllowanceTotalAmount.setAttribute('currencyID', currency)
        text = doc.createTextNode(montoDesc)
        cbcAllowanceTotalAmount.appendChild(text)
        cacLegalMonetaryTotal.appendChild(cbcAllowanceTotalAmount)
        cbcPayableAmount = doc.createElement('cbc:PayableAmount')
        cbcPayableAmount.setAttribute('currencyID', currency)
        text = doc.createTextNode(monto)
        cbcPayableAmount.appendChild(text)
        cacLegalMonetaryTotal.appendChild(cbcPayableAmount)
    xml_str = cacLegalMonetaryTotal.toprettyxml(indent="  ")
    return xml_str


def datosProducto(nombre, identificacion):
    cacItem = doc.createElement('cac:Item')
    cbcDescription = doc.createElement('cbc:Description')
    text = doc.createTextNode(nombre)
    cbcDescription.appendChild(text)
    cacItem.appendChild(cbcDescription)
    cacSellersItemIdentification = doc.createElement('cac:SellersItemIdentification')
    cacItem.appendChild(cacSellersItemIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacSellersItemIdentification.appendChild(cbcID)
    xml_str = cacItem.toprettyxml(indent="  ")
    return xml_str


def precioProducto(precio, currency):
    cacPrice = doc.createElement('cac:Price')
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)
    xml_str = cacPrice.toprettyxml(indent="  ")
    return xml_str


def Producto(idP, unidad_medida,cantidad, montoT, monto, nombre, identificacion, precio, descripcion, idtax, afectacion_igv,currency):
    cacInvoiceLine = doc.createElement('cac:InvoiceLine')
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idP)
    cbcID.appendChild(text)
    cacInvoiceLine.appendChild(cbcID)
    cbcInvoiceQuantity = doc.createElement('cbc:InvoicedQuantity')
    cbcInvoiceQuantity.setAttribute('unitCode', unidad_medida)
    text = doc.createTextNode(cantidad)
    cbcInvoiceQuantity.appendChild(text)
    cacInvoiceLine.appendChild(cbcInvoiceQuantity)
    cbcLineExtensionAmount = doc.createElement('cbc:LineExtensionAmount')
    cbcLineExtensionAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(montoT)
    cbcLineExtensionAmount.appendChild(text)
    cacInvoiceLine.appendChild(cbcLineExtensionAmount)
    cacPricingReference = doc.createElement('cac:PricingReference')
    cacInvoiceLine.appendChild(cacPricingReference)
    if montoT == '0.0':
        cacAlternativeConditionPrice = doc.createElement('cac:AlternativeConditionPrice')
        cacPricingReference.appendChild(cacAlternativeConditionPrice)
        cbcPriceAmount = doc.createElement('cbc:PriceAmount')
        cbcPriceAmount.setAttribute('currencyID', currency)
        text = doc.createTextNode(montoT)
        cbcPriceAmount.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceAmount)
        cbcPriceTypeCode = doc.createElement('cbc:PriceTypeCode')
        text = doc.createTextNode('01')
        cbcPriceTypeCode.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)
        cacAlternativeConditionPrice2 = doc.createElement('cac:AlternativeConditionPrice')
        cacPricingReference.appendChild(cacAlternativeConditionPrice2)
        cbcPriceAmount2 = doc.createElement('cbc:PriceAmount')
        cbcPriceAmount2.setAttribute('currencyID', currency)
        text = doc.createTextNode(precio)
        cbcPriceAmount2.appendChild(text)
        cacAlternativeConditionPrice2.appendChild(cbcPriceAmount2)
        cbcPriceTypeCode = doc.createElement('cbc:PriceTypeCode')
        text = doc.createTextNode('02')
        cbcPriceTypeCode.appendChild(text)
        cacAlternativeConditionPrice2.appendChild(cbcPriceTypeCode)
    else:
        cacAlternativeConditionPrice = doc.createElement('cac:AlternativeConditionPrice')
        cacPricingReference.appendChild(cacAlternativeConditionPrice)
        cbcPriceAmount = doc.createElement('cbc:PriceAmount')
        cbcPriceAmount.setAttribute('currencyID', currency)
        text = doc.createTextNode(precio)
        cbcPriceAmount.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceAmount)
        cbcPriceTypeCode = doc.createElement('cbc:PriceTypeCode')
        text = doc.createTextNode('01')
        cbcPriceTypeCode.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)

    cacTaxTotal = doc.createElement('cac:TaxTotal')
    cacInvoiceLine.appendChild(cacTaxTotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxTotal.appendChild(cbcTaxAmount)
    cacTaxSubtotal = doc.createElement('cac:TaxSubtotal')
    cacTaxTotal.appendChild(cacTaxSubtotal)
    cbcTaxAmount = doc.createElement('cbc:TaxAmount')
    cbcTaxAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(monto)
    cbcTaxAmount.appendChild(text)
    cacTaxSubtotal.appendChild(cbcTaxAmount)
    cacTaxCategory = doc.createElement('cac:TaxCategory')
    cacTaxSubtotal.appendChild(cacTaxCategory)
    cbcTaxExemptionReasonCode = doc.createElement('cbc:TaxExemptionReasonCode')
    text = doc.createTextNode(afectacion_igv)
    cbcTaxExemptionReasonCode.appendChild(text)
    cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
    cacTaxScheme = doc.createElement('cac:TaxScheme')
    cacTaxCategory.appendChild(cacTaxScheme)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(idtax)
    cbcID.appendChild(text)
    cacTaxScheme.appendChild(cbcID)
    cbcName = doc.createElement('cbc:Name')
    text = doc.createTextNode('IGV')
    cbcName.appendChild(text)
    cacTaxScheme.appendChild(cbcName)
    cbcTaxTypeCode = doc.createElement('cbc:TaxTypeCode')
    text = doc.createTextNode('VAT')
    cbcTaxTypeCode.appendChild(text)
    cacTaxScheme.appendChild(cbcTaxTypeCode)

    cacItem = doc.createElement('cac:Item')
    cacInvoiceLine.appendChild(cacItem)
    cbcDescription = doc.createElement('cbc:Description')
    text = doc.createTextNode(descripcion)
    cbcDescription.appendChild(text)
    cacItem.appendChild(cbcDescription)
    cacSellersItemIdentification = doc.createElement('cac:SellersItemIdentification')
    cacItem.appendChild(cacSellersItemIdentification)
    cbcID = doc.createElement('cbc:ID')
    text = doc.createTextNode(identificacion)
    cbcID.appendChild(text)
    cacSellersItemIdentification.appendChild(cbcID)

    # cacPrice = doc.createElement('cac:Price')
    # cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    # cbcPriceAmount.setAttribute('currencyID', currency)
    # text = doc.createTextNode(montoT)
    # cbcPriceAmount.appendChild(text)
    # cacPrice.appendChild(cbcPriceAmount)

    cacPrice = doc.createElement('cac:Price')
    cacInvoiceLine.appendChild(cacPrice)
    cbcPriceAmount = doc.createElement('cbc:PriceAmount')
    cbcPriceAmount.setAttribute('currencyID', currency)
    text = doc.createTextNode(precio)
    cbcPriceAmount.appendChild(text)
    cacPrice.appendChild(cbcPriceAmount)

    xml_str = cacInvoiceLine.toprettyxml(indent="  ")
    return xml_str


def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD', unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()


account_invoice()
