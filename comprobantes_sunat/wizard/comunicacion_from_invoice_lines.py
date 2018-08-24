# -*- coding: utf-8 -*-
from __future__ import print_function
import time
from openerp.osv import fields, osv
from openerp.exceptions import except_orm
from openerp.tools.translate import _

class comunicacion_from_invoice_lines(osv.osv_memory):
    """
    Generate Entries by Statement from Invoices
    """
    _name = "comunicacion.from.invoice.lines"
    _description = "Comunicaciones from Invoices"

    _columns = {
        'comunicacion_ids': fields.many2many('account.invoice', 'move_line_relation', 'move_id', 'line_id',
                                             'Invoices'),
        # 'comunicacion_ids': fields.many2many('account.move.line', 'move_line_relation', 'move_id', 'line_id',
        #                                      'Invoices'),
    }

    def pasar_datos(self, cr, uid, ids, context=None):

        print('>>>>>>>>>>>Ya entre pero no soy correcto<<<<<<<<<<<<<<<<<')
        context = dict(context or {})
        comunicacion_id = context.get('comunicacion_id', False)
        if not comunicacion_id:
            return {'type': 'ir.actions.act_window_close'}
        data = self.read(cr, uid, ids, context=context)[0]
        comunicacion_ids = data['comunicacion_ids']
        if not comunicacion_ids:
            return {'type': 'ir.actions.act_window_close'}

        # line_obj = self.pool.get('account.move.line')
        line_obj = self.pool.get('account.invoice')
        print('>>>>>1>>>>>>' + str(line_obj) + '<<<ff<<<<<lineobj<<<<<')
        statement_obj = self.pool.get('einvoice.comunicacion.baja')
        print('>>>>>2>>>>>' + str(statement_obj) + '<<<ff<<<<<<<<<<')
        statement_line_obj = self.pool.get('einvoice.detalle.comunicacion.baja')
        print('>>>>3>>>>>>>' + str(statement_line_obj) + '<<<ff<<<<<<<<<<')
        currency_obj = self.pool.get('res.currency')
        print('>>>>4>>>>>>>' + str(currency_obj) + '<<<ff<<<<<<<<<<')
        statement = statement_obj.browse(cr, uid, comunicacion_id, context=context)
        print('>>>>5>>>>>>>' + str(statement) + '<<<ff<<<<<<<<<<')
        line_date = statement.fecha_doc
        print('>>>>6>>>>>>>' + str(line_date) + '<<<ff<<<<<<<<<<')

        # for each selected move lines
        for line in line_obj.browse(cr, uid, comunicacion_ids, context=context):
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date

            # context.update({'move_line_ids': [line.id],
            #                 'invoice_id': line.id})

            referencia = self.pool.get('account.invoice').search(cr, uid, [('number', '=', line.number),
                                                                           ('date_invoice', '=', line.date_invoice),
                                                                           ('journal_id', '=', line.journal_id.code)],
                                                                 context=None)
            empresa = self.pool.get('account.invoice').browse(cr, uid, referencia, context)
            # print('>>>>8>>>>>>>' + str(empresa.id) + '<<<ff<<<<<<<<<<')

            if line.date_invoice != statement.fecha_doc:
                raise osv.except_osv(_('Error!'), _("No puede Elegir Fechas Diferentes a la seleccionada anteriormente"))
            # for idx, item in enumerate(comunicacion_ids):
            #     item = idx + 1
            codigo_documento = int(line.journal_id.code)
            statement_line_obj.create(cr, uid, {
                'comprobante': line.number,
                'tipo_documento': str(codigo_documento).zfill(2),
                'serie': line.number[0:4],
                'correlativo': line.number[5::],
                'fecha_doc': line.date_invoice,
                # 'motivo': '',
                'comunicacion_id': comunicacion_id,
                'count_letras': 100,
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
