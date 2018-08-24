# -*- coding: utf-8 -*-

import xlwt
import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _
import datetime
from datetime import date
import calendar
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render


class reporte_libro_diario(osv.osv_memory):
    _name = "reporte.libro.diario"
    _description = "Facturas Libro diario Report"

    def DiasMes(self):
        anho= date.today().strftime('%Y')
        mes = date.today().strftime('%m')
        firstweekday, days = calendar.monthrange(int(anho), int(mes))
        return date.today().strftime('%Y-%m-'+str(days))

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Año Fiscal',  help='Keep empty for all open fiscal year'),
        'period_from': fields.many2one('account.period', 'Inicio', required=True),
        'period_to': fields.many2one('account.period', 'Fin', required=True),
        'journal_ids': fields.many2many('account.journal', 'account_print_libro_diario_rel', 'account_id', 'journal_id', 'Diarios', required=True),

        }

    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        # use current company id
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[])

    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
        'journal_ids': _get_all_journal,
    }

    def check_report(self,cr,uid,ids,context=None):

        Mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
               "Noviembre", "Diciembre"]

        data = self.read(cr, uid, ids, ['fiscalyear_id', 'journal_ids', 'period_from', 'period_to'], context=context)
        date_from = data[0]['period_from']
        date_to = data[0]['period_to']

        fiscalyear_id = data[0]['fiscalyear_id']
        journal_ids = data[0]['journal_ids']
        spli_date_to = date_to.split('/')

        mes_de = 'REGISTRO DE COMPRAS DEL MES DE '+ str(Mes[int(spli_date_to[1])-1])

        data={'mes':mes_de.upper(),'fiscalyear':fiscalyear_id,'journals':journal_ids,'tipo':'posted','fi':str(date_from + ' 00:00:00'),'ff':str(date_to + ' 23:59:59'),'ids':ids}
        # if context.get('xls_export'):
        #     return {'type': 'ir.actions.report.xml',
        #             'report_name': 'facturas.diario.xls',
        #             'datas': data}
        # else:
        return self.pool['report'].get_action(cr,uid,[],'account_invoice.report_libro_diario_pdf',data=data,context=context)
