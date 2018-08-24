# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from openerp.osv import fields, osv

class account_statement_from_invoice_lines2(osv.osv_memory):
    """
    Generate Entries by Statement from Invoices
    """
    _name = "account.statement.from.invoice.lines2"
    _description = "Entries by Statement from Invoices"
    _columns = {
        'line_ids': fields.many2many('account.move.line', 'account_move_line_relation2', 'move_id', 'line_id', 'Invoices'),
    }

    def populate_statement2(self, cr, uid, ids, context=None):
        context = dict(context or {})
        print (context)
        # raise Warning('ss')
        line_detail = context.get('line_detail', False)
        id_extracto = context.get('id_extracto', False)
        if not line_detail:
            return {'type': 'ir.actions.act_window_close'}
        # raise Warning(context)
        data = self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_detail_line_obj = self.pool.get('einvoice.extract.line.detail')
        currency_obj = self.pool.get('res.currency')
        # currency = self.pool.get('res.currency').search([('id','=',165)]) # para soles
        line_date = time.strftime('%Y-%m-%d')
        statement = statement_line_obj.browse(cr, uid, line_detail, context=context)
        extracto = statement_obj.browse(cr, uid, id_extracto, context=context)

        res_users_obj = self.pool.get('res.users')
        currency = res_users_obj.browse(cr, uid, uid, context=context).company_id.currency_id

        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line.date
            amount = 0.0
            amount_nacional = 0.0

            # factura_id = invoice_obj.search(cr, uid, [('move_id.id', '=', line.move_id.id)])
            # factura = invoice_obj.browse(cr, uid, factura_id)
            # print (factura)

            if line.invoice.existe_detraccion_cliente and line.invoice.currency_id.id == 3:
                monto_currency = line.invoice.monto_sin_detraccion
                amount_nacional = conv_dolares_soles = currency_obj.compute(cr, uid, 3, 165, line.invoice.monto_sin_detraccion, context=ctx)
                if line.debit > 0:
                    amount = conv_dolares_soles
                    amount_extranjero = line.invoice.monto_sin_detraccion
                    amount_nacional = amount_nacional
                elif line.credit > 0:
                    amount = -conv_dolares_soles
                    amount_extranjero = line.invoice.monto_sin_detraccion
                    amount_nacional = -amount_nacional
            elif line.invoice.existe_detraccion_cliente and line.invoice.currency_id.id == 165:
                amount_extranjero = currency_obj.compute(cr, uid, 165, 3, line.invoice.monto_sin_detraccion, context=ctx)
                if line.debit > 0:
                    amount = line.invoice.monto_sin_detraccion
                    amount_nacional = line.invoice.monto_sin_detraccion
                    amount_extranjero = amount_extranjero
                elif line.credit > 0:
                    amount = -line.invoice.monto_sin_detraccion
                    amount_nacional = -line.invoice.monto_sin_detraccion
                    amount_extranjero = -amount_extranjero
            elif not line.invoice.existe_detraccion_cliente:
                monto_currency = line.amount_currency
                if line.debit > 0:
                    amount = line.debit
                    amount_nacional = line.debit
                    amount_extranjero = currency_obj.compute(cr, uid, 165, 3, line.debit, context=ctx)
                elif line.credit > 0:
                    amount = -line.credit
                    amount_nacional = -line.credit
                    amount_extranjero = -(currency_obj.compute(cr, uid, 165, 3, line.credit, context=ctx))

            if line.amount_currency:
                amount = currency_obj.compute(cr, uid, line.currency_id.id, extracto.currency.id, monto_currency, context=ctx)
            elif line.invoice and line.invoice.currency_id.id != extracto.currency.id:
                amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id, extracto.currency.id, amount, context=ctx)

            context.update({'move_line_ids': [line.id],
                            'invoice_id': line.invoice.id})

            statement_detail_line_obj.create(cr, uid, {
                'name': line.name or '?',
                'amount': amount,
                'importe_nacional': amount_nacional,
                'importe_extranjera': amount_extranjero,
                'partner_id': line.partner_id.id,
                'line_detail_id': line_detail,
                'ref': line.ref,
                'date': statement.date,
                'amount_currency': monto_currency,
                'currency_id': line.currency_id.id,
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
