# -*- coding: utf-8 -*-
import time
import xlwt
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.osv import orm
from openerp.tools.translate import translate, _
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'account_invoice.report_facturas_diario_pdf'
_ir_translation_name_ventas = 'account_invoice.report_facturas_diario_ventas_pdf'

class general_factura_diario(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(general_factura_diario, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'get_data_fac': self.get_data_fac,
            'tipo_comprobante_compra': self.tipo_comprobante_compra,
            'try_parsing_date': self.try_parsing_date,
            'currency_rate': self.currency_rate,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src

    def currency_rate(self, id_wizard):
        sql = """SELECT rcr.* as name FROM res_currency rc INNER JOIN res_currency_rate rcr on rc.id = rcr.currency_id WHERE rc.id=%s"""
        self.cr.execute(sql, [id_wizard])
        rate_line = self.cr.dictfetchall()
        return rate_line

    def get_data_fac(self, id_wizard, fi, ff):
        sql = """
                   SELECT ai.*, rp.name as nombre_proveedor, rp.display_name as nombre_proveedor2, 
                   rp.doc_type, rp.doc_number, tc_venta, tc_compra, rc.name as codecambio, rc.id as idcurrency, ai.comment, cast('' as text) as r_fecha, cast('' as text) as r_doc, '' as r_num, '' as descripcion FROM account_invoice ai 
                   LEFT JOIN res_partner rp ON  ai.partner_id = rp.id 
                   LEFT JOIN res_currency rc ON  ai.currency_id = rc.id 
                   where tipo_factura = %s and date_invoice >= %s and date_invoice <= %s and ai.type = 'in_invoice' and ai.state in ('open','paid')
                   ORDER by ai.id
               """
        self.cr.execute(sql, (id_wizard.id, fi, ff))
        wizard_data = self.cr.dictfetchall()
        # print (wizard_data)
        return wizard_data

    def tipo_comprobante_compra(self, id_wizard):
        student_obj = self.pool.get('einvoice.catalog.01')
        tipos = student_obj.browse(self.cr, self.uid, id_wizard)
        # print (tipos)
        return tipos

    def try_parsing_date(self, text):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
            try:
                date2 = datetime.strptime(text, fmt)
                return date2.strftime('%d/%m/%Y')
            except ValueError:
                pass
        raise ValueError('no valid date format found')


class report_factura_diario(osv.AbstractModel):
    _name = 'report.account_invoice.report_facturas_diario_pdf'
    _inherit = 'report.abstract_report'
    _template = 'account_invoice.report_facturas_diario_pdf'
    _wrapped_report_class = general_factura_diario

class general_factura_diario_ventas(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(general_factura_diario_ventas, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'get_data_fac': self.get_data_fac,
            'tipo_comprobante_venta': self.tipo_comprobante_venta,
            'try_parsing_date': self.try_parsing_date,
            'currency_rate': self.currency_rate,
            '_get_serie': self._get_serie,
            '_get_numeracion': self._get_numeracion,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name_ventas, 'report', lang, src) or src

    def currency_rate(self, id_wizard):
        sql = """SELECT rcr.* as name FROM res_currency rc INNER JOIN res_currency_rate rcr on rc.id = rcr.currency_id WHERE rc.id=%s"""
        self.cr.execute(sql, [id_wizard])
        rate_line = self.cr.dictfetchall()
        return rate_line

    def get_data_fac(self, id_wizard, fi, ff):
        # print (id_wizard, fi, ff)
        sql = """
                   (SELECT ai.*, cast(aj.code as int) as code, aj.type, rp.name as nombre_proveedor, rp.display_name as nombre_proveedor2, rp.doc_type, rp.doc_number, tc_venta, tc_compra, rc.name as codecambio, rc.id as idcurrency, ai.comment, cast('' as text) as r_fecha, cast('' as text) as r_doc, '' as r_num, '' as descripcion
                   FROM account_invoice ai 
                   LEFT JOIN account_journal aj ON aj.id = ai.journal_id 
                   LEFT JOIN res_partner rp ON  ai.partner_id = rp.id 
                   LEFT JOIN res_currency rc ON  ai.currency_id = rc.id 
                   where CAST(coalesce(aj.code, '0') AS integer) = %s and  aj.type = 'sale' and  ai.type = 'out_invoice' and ai.state in ('open','paid','anulado','cancel') and date_invoice >= %s and date_invoice <= %s ORDER BY internal_number)
                   UNION
                   (SELECT ai.*, 7, aj.type, rp.name as nombre_proveedor, rp.display_name as nombre_proveedor2, rp.doc_type, rp.doc_number, tc_venta, tc_compra, rc.name as codecambio, rc.id as idcurrency, ai.comment, cast(einc.fecha_emision as text), cast(aj.code as text) as code, einc.numeracion, einc.descripcion
                   FROM account_invoice ai 
                   INNER JOIN einvoice_nota_credito einc ON einc.referencia = ai.id
                   LEFT JOIN account_journal aj ON aj.id = ai.journal_id 
                   LEFT JOIN res_partner rp ON  ai.partner_id = rp.id 
                   LEFT JOIN res_currency rc ON  ai.currency_id = rc.id 
                   where CAST(coalesce('7', '0') AS integer) = %s and  aj.type = 'sale' and  ai.type = 'out_invoice' and ai.state in ('open','paid','anulado','cancel') and fecha_emision >= %s and fecha_emision <= %s and einc.state != 'error' ORDER BY internal_number) ORDER BY internal_number
               """
        self.cr.execute(sql, (id_wizard, fi, ff, id_wizard, fi, ff))
        wizard_data = self.cr.dictfetchall()
        # print (wizard_data)
        return wizard_data

    def tipo_comprobante_venta(self, id_wizard):
        print (id_wizard)
        # str1 = ','.join(e for e in id_wizard)
        # sql = 'SELECT DISTINCT cast(code as int) as code, id FROM account_journal WHERE id = ANY(%s)'
        # self.cr.execute(sql, [id_wizard])
        # tipos = self.cr.dictfetchall()
        student_obj = self.pool.get('account.journal')
        tipos = student_obj.browse(self.cr, self.uid, id_wizard)
        print (tipos)
        return tipos

    def try_parsing_date(self, text):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
            try:
                date2 = datetime.strptime(text, fmt)
                return date2.strftime('%d/%m/%Y')
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def _get_serie(self, serie):
        n = serie.split('-')
        return n[0]

    def _get_numeracion(self, numeracion):
        n = numeracion.split('-')
        return n[1]


class report_factura_diario_ventas(osv.AbstractModel):
    _name = 'report.account_invoice.report_facturas_diario_ventas_pdf'
    _inherit = 'report.abstract_report'
    _template = 'account_invoice.report_facturas_diario_ventas_pdf'
    _wrapped_report_class = general_factura_diario_ventas

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
