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


class reporte_facturas_diario(osv.osv_memory):
    _name = "reporte.facturas.diario"
    _description = "Facturas diario Report"

    def DiasMes(self):
        anho= date.today().strftime('%Y')
        mes = date.today().strftime('%m')
        firstweekday, days = calendar.monthrange(int(anho), int(mes))
        return date.today().strftime('%Y-%m-'+str(days))

    _columns = {
        # 'journal_ids': fields.many2many('account.journal', 'account_print_factura_diario_rel', 'account_id', 'journal_id', 'Diarios', required=True),
        'compra_venta': fields.selection(string="Reporte de compras o Ventas", selection=[('purchase', 'Compra'), ('sale', 'Venta'), ], required=True, default='purchase'),

        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Año Fiscal',
                                         help='Keep empty for all open fiscal year'),
        'filter': fields.selection([('filter_date', 'Fecha'), ('filter_period', 'Periodos')], "Filtro", required=True),
        'date_from': fields.date('Fecha Inicial', default=date.today().strftime('%Y-%m-01')),
        'date_to': fields.date('Fecha Final', default=lambda self: self.DiasMes()),
        'period_from': fields.many2one('account.period', 'Inicio Periodo'),
        'period_to': fields.many2one('account.period', 'Fin Periodo'),
        }

    def onchange_filter(self, cr, uid, ids, filter='filter_date', fiscalyear_id=False, context=None):
        res = {'value': {}}
        # if filter == 'filter_no':
        #     res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
            # res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res


    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
        'filter': 'filter_date',
    }

    def check_report(self,cr,uid,ids,context=None):
        reporte_data=self.browse(cr,uid,ids,context=context)
        student_obj = self.pool.get('account.invoice')
        Mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
               "Noviembre", "Diciembre"]
        data = self.read(cr, uid, ids, ['date_from', 'date_to','compra_venta',  'fiscalyear_id', 'period_from', 'period_to',  'filter'], context=context)

        if data[0]['filter'] == 'filter_period':
            periodo_inicio = self.pool.get('account.period').browse(cr, uid, data[0]['period_from'][0])
            periodo_fin = self.pool.get('account.period').browse(cr, uid, data[0]['period_to'][0])
            date_from = periodo_inicio.id
            date_to = periodo_fin.id
            spli_date_to = periodo_inicio.date_stop.split('-')
            comprobantes = student_obj.search(cr, uid,[('period_id','>=',date_from), ('period_id','<=',date_to),('journal_id.type', '=', 'purchase'),('state', 'in', ('open','paid'))], context=context)
            tipos = []
        # print (periodo_fin.id)
        else:
            date_from = data[0]['date_from']
            date_from = str(date_from)
            date_to = data[0]['date_to']
            date_to = str(date_to)
            spli_date_to = date_to.split('-')
            comprobantes = student_obj.search(cr, uid,[('date_invoice','>=', str(date_from + ' 00:00:00')), ('date_invoice','<=',str(date_to + ' 23:59:59')),('journal_id.type', '=', 'purchase'),('state', 'in', ('open','paid'))], context=context)
            tipos = []

        compra_venta = data[0]['compra_venta']
        filter = data[0]['filter']

        mes_de = 'REGISTRO DE COMPRAS DEL MES DE '+ str(Mes[int(spli_date_to[1])-1])
        # print (comprobantes)
        for t in student_obj.browse(cr,uid,comprobantes,context=context):
            tipos.append(t.tipo_factura.id)

        print (tipos)
        data={'mes':mes_de.upper(),
              'tipos':list(set(tipos)),
              'facs': comprobantes,
              'tipo':'purchase',
              'fi':date_from,
              'ff':date_to,
              'ids':ids,
              'filter': str(filter),}
        print (data)
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'facturas.diario.xls',
                    'datas': data}
        else:
            return self.pool['report'].get_action(cr,uid,[],'account_invoice.report_facturas_diario_pdf',data=data,context=context)

    def _report_xls_fields(self, cr, uid, context=None):
        header_list = ['o',
                       'nro_voucher',
                       'fecha_emision',
                       'fecha_vencimiento',
                       'tipo_documento',
                       'serie_documento',
                       'correlativo_documento',
                       'r_fecha',
                       'r_doc',
                       'r_numero',
                       'tipo_documento_identidad',
                       'numero_documento_identidad',
                       'nombre_proveedor',
                       'valor_exportacion',
                       'importe_sin_igv',
                       'inafecto',
                       'campo_vacio4',
                       'igv',
                       'campo_vacio5',
                       'campo_vacio6',
                       'importe_total',
                       'tipo_cambio',
                       'glosa',
                       ]
        return header_list


    # Change/Add Template entries
    def _report_xls_template(self, cr, uid, context=None):
        """
        Template updates, e.g.
        my_change = {
            'move_name':{
                'header': [1, 20, 'text', _render("_('My Move Title')")],
                'lines': [1, 0, 'text', _render("l['move_name'] != '/' and l['move_name'] or ('*'+str(l['move_id']))")],
                'totals': [1, 0, 'text', None]},
        }
        return my_change
        """
        return {}


class reporte_facturas_diario_compras(osv.osv_memory):
    _name = "reporte.facturas.diario.compras"
    _description = "Facturas diario Report Compras"

    def DiasMes(self):
        anho= date.today().strftime('%Y')
        mes = date.today().strftime('%m')
        firstweekday, days = calendar.monthrange(int(anho), int(mes))
        return date.today().strftime('%Y-%m-'+str(days))

    _columns = {
        # 'journal_ids': fields.many2many('account.journal', 'account_print_factura_diario_rel', 'account_id', 'journal_id', 'Diarios', required=True),
        'compra_venta': fields.selection(string="Reporte de compras o Ventas", selection=[('purchase', 'Compra'), ('sale', 'Venta'), ], required=True, default='purchase'),

        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Año Fiscal',
                                         help='Keep empty for all open fiscal year'),
        'filter': fields.selection([('filter_date', 'Fecha'), ('filter_period', 'Periodos')], "Filtro", required=True),
        'date_from': fields.date('Fecha Inicial', default=date.today().strftime('%Y-%m-01')),
        'date_to': fields.date('Fecha Final', default=lambda self: self.DiasMes()),
        'period_from': fields.many2one('account.period', 'Inicio Periodo'),
        'period_to': fields.many2one('account.period', 'Fin Periodo'),
        }

    def onchange_filter(self, cr, uid, ids, filter='filter_date', fiscalyear_id=False, context=None):
        res = {'value': {}}
        # if filter == 'filter_no':
        #     res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res

    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
        'filter': 'filter_date',
    }

    def check_report(self,cr,uid,ids,context=None):
        reporte_data=self.browse(cr,uid,ids,context=context)
        student_obj = self.pool.get('account.invoice')
        Mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
               "Noviembre", "Diciembre"]
        data = self.read(cr, uid, ids, ['date_from', 'date_to','compra_venta',  'fiscalyear_id', 'period_from', 'period_to',  'filter'], context=context)

        if data[0]['filter'] == 'filter_period':
            periodo_inicio = self.pool.get('account.period').browse(cr, uid, data[0]['period_from'][0])
            periodo_fin = self.pool.get('account.period').browse(cr, uid, data[0]['period_to'][0])
            date_from = periodo_inicio.id
            date_to = periodo_fin.id
            spli_date_to = periodo_inicio.date_stop.split('-')
            comprobantes = student_obj.search(cr, uid,[('period_id','>=',date_from), ('period_id','<=',date_to),('journal_id.type', '=', 'purchase'),('state', 'in', ('open','paid'))], context=context)
            tipos = []
        # print (periodo_fin.id)
        else:
            date_from = data[0]['date_from']
            date_from = str(date_from)
            date_to = data[0]['date_to']
            date_to = str(date_to)
            spli_date_to = date_to.split('-')
            comprobantes = student_obj.search(cr, uid,[('date_invoice','>=', str(date_from + ' 00:00:00')), ('date_invoice','<=',str(date_to + ' 23:59:59')),('journal_id.type', '=', 'purchase'),('state', 'in', ('open','paid'))], context=context)
            tipos = []

        compra_venta = data[0]['compra_venta']
        filter = data[0]['filter']

        mes_de = 'REGISTRO DE COMPRAS DEL MES DE '+ str(Mes[int(spli_date_to[1])-1])
        # print (comprobantes)
        for t in student_obj.browse(cr,uid,comprobantes,context=context):
            tipos.append(t.tipo_factura.id)

        # print (tipos)
        data={'mes':mes_de.upper(),
              'tipos':list(set(tipos)),
              'facs': comprobantes,
              'tipo':'purchase',
              'fi':date_from,
              'ff':date_to,
              'ids':ids,
              'filter': str(filter),}
        # print (data)
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'facturas.diario.xls.compras',
                    'datas': data}
        else:
            return False
            # return self.pool['report'].get_action(cr,uid,[],'account_invoice.report_facturas_diario_compras_pdf',data=data,context=context)

    def _report_xls_fields(self, cr, uid, context=None):
        header_list = ['o',
                       'nro_voucher',
                       'fecha_emision',
                       'tipo_documento',
                       'serie_documento',
                       'correlativo_documento',
                       'r_fecha',
                       'r_doc',
                       'r_numero',
                       'tipo_documento_identidad',
                       'numero_documento_identidad',
                       'nombre_proveedor',
                       'base_imponible_og',
                       'base_imponible_ag_exp',
                       'base_imponible_a_sind',
                       'base_imponible_a_ng',
                       'isc',
                       'igv_base_imponible_og',
                       'igv_base_imponible_ag_exp',
                       'igv_base_imponible_a_sind',
                       'otros_impuestos',
                       'importe_total',
                       'moneda', #preguntar que es
                       'tipo_cambio',
                       'd_fecha',
                       'd_numero',
                       'fecha_vencimiento',
                       'glosa',
                       ]
        return header_list


    # Change/Add Template entries
    def _report_xls_template(self, cr, uid, context=None):
        """
        Template updates, e.g.
        my_change = {
            'move_name':{
                'header': [1, 20, 'text', _render("_('My Move Title')")],
                'lines': [1, 0, 'text', _render("l['move_name'] != '/' and l['move_name'] or ('*'+str(l['move_id']))")],
                'totals': [1, 0, 'text', None]},
        }
        return my_change
        """
        return {}

class reporte_facturas_diario_ventas(osv.osv_memory):
    _name = "reporte.facturas.diario.ventas"
    _description = "Facturas diario ventas"

    def DiasMes(self):
        anho = date.today().strftime('%Y')
        mes = date.today().strftime('%m')
        firstweekday, days = calendar.monthrange(int(anho), int(mes))
        return date.today().strftime('%Y-%m-' + str(days))

    _columns = {
        'date_from': fields.date('Fecha Inicial', default=date.today().strftime('%Y-%m-01')),
        'date_to': fields.date('Fecha Final', default=lambda self: self.DiasMes()),
        'journal_ids': fields.many2many('account.journal', 'account_factura_diario_ventas_rel', 'account_id', 'journal_id', 'Diario Ventas', required=True),
        # 'compra_venta': fields.selection(string="Reporte de compras o Ventas",
        #                                  selection=[('purchase', 'Compra'), ('sale', 'Venta'), ], required=True,
        #                                  default='purchase'),
    }
    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[('type', '=', 'sale')])

    _defaults = {
            'journal_ids': _get_all_journal,
    }

    def check_report_ventas(self, cr, uid, ids, context=None):
        student_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        Mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
               "Octubre",
               "Noviembre", "Diciembre"]
        data = self.read(cr, uid, ids, ['date_from', 'date_to', 'journal_ids'], context=context)
        # print (data)
        date_from = data[0]['date_from']
        date_to = data[0]['date_to']
        journal_ids = data[0]['journal_ids']

        # compra_venta = data[0]['compra_venta']
        spli_date_to = date_to.split('-')

        mes_de = 'REGISTRO DE VENTAS E INGRESOS DEL MES DE ' + str(Mes[int(spli_date_to[1]) - 1])
        #
        comprobantes = student_obj.search(cr, uid, [('date_invoice', '>=', str(date_from + ' 00:00:00')),
                                                    ('date_invoice', '<=', str(date_to + ' 23:59:59')),
                                                    ('journal_id', 'in', (journal_ids)),
                                                    ('state', 'in', ('open', 'paid'))], context=context)
        tipos = []
        # print (comprobantes)
        # print (journal_ids)
        for t in journal_obj.browse(cr, uid, journal_ids, context=context):
            tipos.append(int(t.code))
        tipos.append(int(7))
        data = {'mes': mes_de.upper(), 'tiposc': sorted(list(set(tipos))), 'journals': journal_ids, 'facs': comprobantes, 'tipo': 'sale','fi':str(date_from + ' 00:00:00'),'ff':str(date_to + ' 23:59:59'),
                'ids': ids}
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'facturas.diario.ventas.xls',
                    'datas': data}
        else:
            return self.pool['report'].get_action(cr, uid, [], 'account_invoice.report_facturas_diario_ventas_pdf',
                                                  data=data, context=context)

    def _report_xls_fields(self, cr, uid, context=None):
        header_list = ['o',
                       'nro_voucher',
                       'fecha_emision',
                       'fecha_vencimiento',
                       'tipo_documento',
                       'serie_documento',
                       'correlativo_documento',
                       'r_fecha',
                       'r_doc',
                       'r_numero',
                       'tipo_documento_identidad',
                       'numero_documento_identidad',
                       'nombre_proveedor',
                       'valor_exportacion',
                       'importe_sin_igv',
                       'inafecto',
                       'campo_vacio4',
                       'igv',
                       'campo_vacio5',
                       'campo_vacio6',
                       'importe_total',
                       'tipo_cambio',
                       'glosa',
                       ]
        return header_list

    # Change/Add Template entries
    def _report_xls_template(self, cr, uid, context=None):
        """
        Template updates, e.g.
        my_change = {
            'move_name':{
                'header': [1, 20, 'text', _render("_('My Move Title')")],
                'lines': [1, 0, 'text', _render("l['move_name'] != '/' and l['move_name'] or ('*'+str(l['move_id']))")],
                'totals': [1, 0, 'text', None]},
        }
        return my_change
        """
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: