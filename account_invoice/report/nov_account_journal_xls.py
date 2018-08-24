# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xlwt
from datetime import datetime
# from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from .account_factura_diario_init import general_factura_diario, general_factura_diario_ventas
from openerp.tools.translate import _
import logging

# from xlwt.Style import default_style

_logger = logging.getLogger(__name__)
totales_generales = ''
VAR_SUBTOTAL = 0
VAR_IGV = 0
VAR_TOTAL = 0
cnt = 0


class facturas_diario_xls_parser(general_factura_diario):

    def __init__(self, cr, uid, name, context):
        super(facturas_diario_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        wizard_obj = self.pool.get('reporte.facturas.diario')
        self.context = context
        wanted_list = wizard_obj._report_xls_fields(cr, uid, context)
        template_changes = wizard_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,

        })


class facturas_diario_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(facturas_diario_xls, self).__init__(
            name, table, rml, parser, header, store)
        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(
            aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(
            aml_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # personalizados
        ajustar_texto = _xs['center'] + _xs['wrap'] + _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs[
            'vert_center']
        self.ajustar_texto_style = xlwt.easyxf(ajustar_texto)

        # XLS Template Journal Items
        self.col_specs_lines_template = {
            'o': {
                'header': [1, 4, 'text', _render("_('O.')"), None],
                'lines': [1, 0, 'text', _render("('01')")],
                'totals': [1, 0, 'text', None]
            },
            'nro_voucher': {
                'header': [1, 4, 'text', _render("_('Vou.')"), None],
                'lines': [1, 0, 'text', _render("(str(count)) or None")],
                'totals': [1, 0, 'text', None]
            },
            'fecha_emision': {
                'header': [1, 13, 'text', _render("_('Fecha D.')"), None],
                'lines':
                    [1, 0, 'date',
                     _render("datetime.strptime(fecha_emision,'%Y-%m-%d') or None"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'fecha_vencimiento': {
                'header': [1, 13, 'text', _render("_('Fecha V.')"), None],
                'lines':
                    [1, 0, 'date',
                     _render("datetime.strptime(fecha_venc,'%Y-%m-%d') or None"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'tipo_documento': {
                'header': [1, 6, 'text', _render("_('Doc')"), None],
                'lines': [1, 0, 'text', _render("tipo_comprobante['code'] or None"), None,
                          self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]
            },
            'serie_documento': {
                'header': [1, 10, 'text', _render("_('Serie')"), None],
                'lines': [1, 0, 'text', _render("l['serie_factura_proveedor'] or None")],
                'totals': [1, 0, 'text', None]
            },
            'correlativo_documento': {
                'header': [1, 12, 'text', _render("_('Número')"), None],
                'lines': [1, 0, 'text', _render("l['correlativo_factura_proveedor'] or None")],
                'totals': [1, 0, 'text', None]
            },
            'r_fecha': {
                'header': [1, 13, 'text', _render("_('R.Fecha.')"), None],
                'lines':
                    [1, 0, 'text', _render("r_fecha or None")],
                'totals': [1, 0, 'text', None]
            },
            'r_doc': {
                'header': [1, 7, 'text', _render("_('R.Doc.')"), None],
                'lines': [1, 0, 'text', _render("str(r_doc) or None")],
                'totals': [1, 0, 'text', None]
            },
            'r_numero': {
                'header': [1, 15, 'text', _render("_('R. Número')"), None],
                'lines': [1, 0, 'text', _render("str(r_num) or None")],
                'totals': [1, 0, 'text', None]
            },
            'tipo_documento_identidad': {
                'header': [1, 5, 'text', _render("_('Doc')"), None],
                'lines': [1, 0, 'text', _render("str(tipo_doc) or None")],
                'totals': [1, 0, 'text', None]
            },
            'numero_documento_identidad': {
                'header': [1, 15, 'text', _render("_('Número')"), None],
                'lines': [1, 0, 'text', _render("l['doc_number'] or None")],
                'totals': [1, 0, 'text', None]
            },
            'nombre_proveedor': {
                'header': [1, 25, 'text', _render("_('Razón')"), None],
                'lines': [1, 0, 'text', _render("l['nombre_proveedor'] or None")],
                'totals': [1, 0, 'number', None]
            },
            'valor_exportacion': {
                'header': [1, 10, 'text', _render("_('Valor Exp.')"), None],
                'lines': [1, 0, 'text', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'importe_sin_igv': {
                'header': [1, 15, 'text', _render("_('B.Imp.')"), None],
                'lines': [1, 0, 'number', _render("subtotal"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("credit_formula or None"),
                           self.rt_cell_style_decimal]
            },
            'inafecto': {
                'header': [1, 15, 'text', _render("_('Inafecto')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None]
            },
            'campo_vacio4': {
                'header': [1, 10, 'text', _render("_('I.S.C')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'igv': {
                'header': [1, 15, 'text', _render("_('I.G.V')"), None],
                'lines': [1, 0, 'number', _render("igv"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("igv_formula or None"),
                           self.rt_cell_style_decimal]
            },
            'campo_vacio5': {
                'header': [1, 10, 'text', _render("_('Otros')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'campo_vacio6': {
                'header': [1, 12, 'text', _render("_('Exonerado')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'importe_total': {
                'header': [1, 15, 'text', _render("_('Total')"), None],
                'lines': [1, 0, 'number', _render("total"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("total_formula or None"),
                           self.rt_cell_style_decimal]
                # 'totals': [1, 0, 'number', None, _render("total_formula"),
                # self.rt_cell_style_decimal]
            },
            'tipo_cambio': {
                'header': [1, 10, 'text', _render("_('T/C')"), None],
                'lines': [1, 0, 'number', _render("tipo_cambio or None"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]
            },
            'glosa': {
                'header': [1, 20, 'text', _render("_('Glosa')"), None],
                'lines': [1, 0, 'text', _render("glosa or None")],
                'totals': [1, 0, 'text', None]
            },
        }

        # XLS Template VAT Summary
        self.col_specs_vat_summary_template = {
            'CAMPO0': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO1': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO2': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO3': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO4': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO5': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO6': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO7': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO8': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO9': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO10': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO11': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO12': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO13': {
                'tax_totals': [1, 0, 'text', None]},
            'tax_amount': {
                'tax_totals': [1, 0, 'number', _render("self.VAR_SUBTOTAL or None"), None,
                               self.rt_cell_style_decimal]},
            'CAMPO15': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'CAMPO16': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'igv_tax': {
                'tax_totals': [1, 0, 'number', _render("self.VAR_IGV or None"), None, self.rt_cell_style_decimal]},
            'CAMPO18': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'CAMPO19': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'total_total': {
                'tax_totals': [1, 0, 'number', _render("self.VAR_TOTAL or None"), None, self.rt_cell_style_decimal]},
            'CAMPO21': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO22': {
                'tax_totals': [1, 0, 'text', None]},
        }

    def _titulo_documento(self, titulo, ws, _p, row_pos, _xs):
        global VAR_SUBTOTAL
        global VAR_IGV
        global VAR_TOTAL
        global cnt
        cnt = 0
        VAR_SUBTOTAL = 0
        VAR_IGV = 0
        VAR_TOTAL = 0
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', titulo),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        return row_pos + 1

    def _lineas_documento(self, o, ws, _p, row_pos, _xs, data):
        global VAR_SUBTOTAL
        global VAR_IGV
        global VAR_TOTAL
        fila_inicial = row_pos
        # aca traigo las cabeceras
        wanted_list = self.wanted_list
        col_sub = 'importe_sin_igv' in wanted_list and wanted_list.index('importe_sin_igv')
        col_igv = 'igv' in wanted_list and wanted_list.index('igv')
        col_importe_total = 'importe_total' in wanted_list and wanted_list.index('importe_total')
        # print (o)
        # lineas de facturas
        tipo_comprobante = _p.tipo_comprobante_compra(o)
        aml_start_pos = row_pos
        aml_cnt = len(_p.get_data_fac(tipo_comprobante, data['fi'], data['ff'], data['filter']))
        # cnt = 0
        for tipo in tipo_comprobante:
            # cnt = 0
            # row_pos = self._titulo_documento(str('Tipo Doc.:' + ' ' + str(tipo['code'] + ' ' + tipo['name'])), ws, _p, row_pos, _xs)
            for l in _p.get_data_fac(tipo, data['fi'], data['ff'], data['filter']):
                for rate in _p.currency_rate(l['idcurrency']):
                    if rate['name'] == l['date_invoice']:
                        global cnt
                        cnt += 1
                        # print ('dsdddddddddddddddddddd', str(cnt))
                        count = cnt
                        # datos enviados directamente
                        tipo_cambio = rate['tc_venta_rate'] if l['codecambio'] == 'USD' else ''
                        subtotal = '%.2f' % (l['amount_untaxed'] * rate['tc_venta_rate'])
                        igv = '%.2f' % (l['amount_tax'] * rate['tc_venta_rate'])
                        total = '%.2f' % (l['amount_total'] * rate['tc_venta_rate'])
                        tipo_doc = '6' if l['doc_type'] == 'ruc' else '1'

                        fecha_emision = l['date_invoice']
                        fecha_venc = l['date_due']
                        r_fecha = l['fecha_documento_ref']
                        r_doc = l['r_doc']
                        r_num = l['reference']
                        glosa = l['comment']
                        subtotal = subtotal if l['state'] != 'cancel' else str('0.00')
                        igv = igv if l['state'] != 'cancel' else str('0.00')
                        total = total if l['state'] != 'cancel' else str('0.00')
                        #################
                        VAR_SUBTOTAL += float(subtotal)
                        VAR_IGV += float(igv)
                        VAR_TOTAL += float(total)
                        self.VAR_SUBTOTAL = VAR_SUBTOTAL
                        self.VAR_IGV = VAR_IGV
                        self.VAR_TOTAL = VAR_TOTAL

                        c_specs = map(
                            lambda x: self.render(x, self.col_specs_lines_template, 'lines'), wanted_list)

                        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                        row_pos = self.xls_write_row(
                            ws, row_pos, row_data, row_style=self.aml_cell_style)
                        # print (row_data)
                        # #separa lineas
                        # if cnt != aml_cnt:
                        # row_pos += 1
        print ('-------------------------------------')
        # print ('subtotal')
        # credit_start = rowcol_to_cell(fila_inicial, col_sub)
        # credit_stop = rowcol_to_cell(row_pos - 1, col_sub)
        # credit_formula = 'SUM(%s:%s)' % (credit_start, credit_stop)
        # print ('credit_formula', str(credit_formula))
        # print ('igv')
        # igv_start = rowcol_to_cell(fila_inicial, col_igv)
        # igv_stop = rowcol_to_cell(row_pos - 1, col_igv)
        # igv_formula = 'SUM(%s:%s)' % (igv_start, igv_stop)
        # print ('igv_formula', str(igv_formula))
        # print ('importe_total')
        # importe_total_start = rowcol_to_cell(fila_inicial, col_importe_total)
        # importe_total_stop = rowcol_to_cell(row_pos - 1, col_importe_total)
        # total_formula = 'SUM(%s:%s)' % (importe_total_start, importe_total_stop)
        # print ('total_formula', str(total_formula))
        # c_specs = map(lambda x: self.render(x, self.col_specs_lines_template, 'totals'), wanted_list)
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        # print ('-------------------------------------')
        # return row_pos + 1
        return row_pos

    def _totales_documento(self, titulo, ws, _p, row_pos, _xs):
        global totales_generales
        wanted_list = self.wanted_list
        vat_summary_wanted_list = ['CAMPO1',
                                   'CAMPO2',
                                   'CAMPO3',
                                   'CAMPO4',
                                   'CAMPO5',
                                   'CAMPO6',
                                   'CAMPO7',
                                   'CAMPO8',
                                   'CAMPO9',
                                   'CAMPO10',
                                   'CAMPO11',
                                   'CAMPO12',
                                   'CAMPO13',
                                   'tax_amount',
                                   'CAMPO15',
                                   'CAMPO16',
                                   'igv_tax',
                                   'CAMPO18',
                                   'CAMPO19',
                                   'total_total',
                                   'CAMPO21',
                                   'CAMPO22', ]
        cell_style = xlwt.easyxf(_xs['xls_title'])

        c_specs = map(lambda x: self.render(x, self.col_specs_vat_summary_template, 'tax_totals'),
                      vat_summary_wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.aml_cell_style)

        return row_pos + 1

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        global cnt
        cnt = 0
        wanted_list = _p.wanted_list
        self.wanted_list = wanted_list
        self.col_specs_lines_template.update(_p.template_changes)

        # for o in data['tipos']:
        if str(data['tipo']) == 'purchase':
            sheet_name = 'Compras - '
        else:
            sheet_name = 'Ventas'
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # titulo
        # row_pos = self._titulo_documento(data['mes'], ws, _p, row_pos, _xs)

        # Column headers
        c_specs = map(lambda x: self.render(x, self.col_specs_lines_template, 'header', render_space={'_': _p._}),
                      wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)  # seteamos la posicion estatica de bajada

        # data
        for o in data['tipos']:
            row_pos = self._lineas_documento(o, ws, _p, row_pos, _xs, data)


facturas_diario_xls('report.facturas.diario.xls', 'reporte.facturas.diario',
                    parser=facturas_diario_xls_parser)


class facturas_diario_xls_parser_compras(general_factura_diario):  # compras

    def __init__(self, cr, uid, name, context):
        super(facturas_diario_xls_parser_compras, self).__init__(cr, uid, name,
                                                                 context=context)
        wizard_obj = self.pool.get('reporte.facturas.diario.compras')
        self.context = context
        wanted_list = wizard_obj._report_xls_fields(cr, uid, context)
        template_changes = wizard_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,

        })


class facturas_diario_xls_compras(report_xls):  # compras

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(facturas_diario_xls_compras, self).__init__(
            name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(
            aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(
            aml_cell_format + _xs['left'],
            num_format_str='DD/MM/YYYY')

        xlwt.add_palette_colour("custom_colour", 0x21)
        # 'pattern: pattern solid, fore_colour yellow;font: name Arial Black, color-index custom_colour;'
        self.amarillo = xlwt.easyxf(
            aml_cell_format + _xs['right'] + 'font:color-index custom_colour, height 220;',
            num_format_str='#,##0.00')
        self.amarillo2_header = xlwt.easyxf(rh_cell_format + _xs['center'] + 'font: color-index custom_colour, height 220;',)  # 16 * 20, for 16 point
        self.amarillo2 = xlwt.easyxf(aml_cell_format + _xs['right'] + 'font: color-index custom_colour, height 220;',)  # 16 * 20, for 16 point

        self.red_header = xlwt.easyxf(rh_cell_format + _xs['center'] + 'font: color-index red,',)  # 16 * 20, for 16 point
        self.red = xlwt.easyxf(aml_cell_format + _xs['right'] + 'font: color-index red,',)  # 16 * 20, for 16 point
        # self.aml_cell_style_date = xlwt.easyxf(
        #     aml_cell_format + _xs['left'],
        #     num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(
            aml_cell_format + _xs['right'] ,
            num_format_str='#,##0.000')
        self.aml_cell_style_decimal2 = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str='#,##0.00')
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # personalizados
        ajustar_texto = _xs['center'] + _xs['wrap'] + _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs[
            'vert_center']
        self.ajustar_texto_style = xlwt.easyxf(ajustar_texto)

        # XLS Template Journal Items
        self.col_specs_lines_template = {
            'o': {
                'header': [1, 4, 'text', _render("_('O.')"), None],
                'lines': [1, 0, 'text', _render("('01')")],
                'totals': [1, 0, 'text', None]
            },
            'nro_voucher': {
                'header': [1, 4, 'text', _render("_('Vou.')"), None],
                'lines': [1, 0, 'text', _render("(str(count)) or None")],
                'totals': [1, 0, 'text', None]
            },
            'fecha_emision': {
                'header': [1, 13, 'text', _render("_('Fecha D.')"), None],
                'lines':
                    [1, 0, 'date',
                     _render("datetime.strptime(fecha_emision,'%Y-%m-%d') or None"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'tipo_documento': {
                'header': [1, 6, 'text', _render("_('Doc')"), None],
                'lines': [1, 0, 'text', _render("tipo_comprobante['code'] or None"), None,
                          self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]
            },
            'serie_documento': {
                'header': [1, 10, 'text', _render("_('Serie')"), None],
                'lines': [1, 0, 'text', _render("l['serie_factura_proveedor'] or None")],
                'totals': [1, 0, 'text', None]
            },
            'correlativo_documento': {
                'header': [1, 12, 'text', _render("_('Número')"), None],
                'lines': [1, 0, 'text', _render("l['correlativo_factura_proveedor'] or None")],
                'totals': [1, 0, 'text', None]
            },
            'r_fecha': {
                'header': [1, 13, 'text', _render("_('R.Fecha.')"), None, self.red_header],
                'lines':
                    [1, 0, 'text', _render("datetime.strftime(datetime.strptime(r_fecha,'%Y-%m-%d'), '%d/%m/%Y') if r_fecha  else ' / / '"), None, self.red],
                'totals': [1, 0, 'text', None]
            },
            'r_doc': {
                'header': [1, 7, 'text', _render("_('R.Doc.')"), None, self.red_header],
                'lines': [1, 0, 'text', _render("str(r_doc)"), None, self.red],
                'totals': [1, 0, 'text', None]
            },
            'r_numero': {
                'header': [1, 15, 'text', _render("_('R. Número')"), None, self.red_header],
                'lines': [1, 0, 'text', _render("str(r_num) or '-'"), None, self.red],
                'totals': [1, 0, 'text', None]
            },
            'tipo_documento_identidad': {
                'header': [1, 5, 'text', _render("_('Doc')"), None],
                'lines': [1, 0, 'text', _render("str(tipo_doc) or None")],
                'totals': [1, 0, 'text', None]
            },
            'numero_documento_identidad': {
                'header': [1, 15, 'text', _render("_('Número')"), None],
                'lines': [1, 0, 'text', _render("l['doc_number'] or None")],
                'totals': [1, 0, 'text', None]
            },
            'nombre_proveedor': {
                'header': [1, 25, 'text', _render("_('Razón Social')"), None],
                'lines': [1, 0, 'text', _render("l['nombre_proveedor'] or None")],
                'totals': [1, 0, 'number', None]
            },
            'base_imponible_og': {
                'header': [1, 10, 'text', _render("_('B.I. A')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("subtotal_gravada_exportacion"), None, self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'base_imponible_ag_exp': {
                'header': [1, 10, 'text', _render("_('B.I. B')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("exportacion_nograbadas"), None, self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'base_imponible_a_sind': {
                'header': [1, 10, 'text', _render("_('B.I. C')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("adquisicion_sinderecho"), None, self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'base_imponible_a_ng': {
                'header': [1, 10, 'text', _render("_('A.no.G')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("adquisicion_nograbada"), None, self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'isc': {
                'header': [1, 10, 'text', _render("_('I.S.C')"), None, self.amarillo2_header],
                'lines': [1, 0, 'text', _render("str('-')"), None, self.amarillo2],
                'totals': [1, 0, 'number', None]
            },
            'igv_base_imponible_og': {
                'header': [1, 10, 'text', _render("_('I.G.V. A')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("igv"), None, self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'igv_base_imponible_ag_exp': {
                'header': [1, 10, 'text', _render("_('I.G.V. B')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("igv_exportacion_nograbadas"), None,
                          self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'igv_base_imponible_a_sind': {
                'header': [1, 10, 'text', _render("_('I.G.V. C')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("igv_adquisicion_sinderecho"), None,
                          self.amarillo],
                'totals': [1, 0, 'number', None, ]
            },
            'otros_impuestos': {
                'header': [1, 10, 'text', _render("_('Otros T.')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("otros_tributos"), None,
                          self.amarillo],
                'totals': [1, 0, 'number', None]
            },
            'importe_total': {
                'header': [1, 15, 'text', _render("_('Total')"), None, self.amarillo2_header],
                'lines': [1, 0, 'number', _render("total"), None,
                          self.amarillo],
                'totals': [1, 0, 'number', None, _render("total_formula or None"),
                           self.amarillo]
            },
            'moneda': {
                'header': [1, 10, 'text', _render("_('Moneda')"), None],
                'lines': [1, 0, 'text', _render("moneda")],
                'totals': [1, 0, 'number', None]
            },
            'tipo_cambio': {
                'header': [1, 10, 'text', _render("_('T/C')"), None],
                'lines': [1, 0, 'number', _render("tipo_cambio or None"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]
            },
            'd_fecha': {
                'header': [1, 13, 'text', _render("_('D. Fecha')"), None],
                'lines':
                    [1, 0, 'text',
                     _render("datetime.strftime(datetime.strptime(otras_ref_fecha,'%Y-%m-%d'), '%d/%m/%Y') if otras_ref_fecha  else ' / / '"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'd_numero': {
                'header': [1, 10, 'text', _render("_('D. Número')"), None],
                'lines': [1, 0, 'text',
                          _render("otras_ref_numero or None")],
                'totals': [1, 0, 'text', None]
            },
            'fecha_vencimiento': {
                'header': [1, 13, 'text', _render("_('Fecha Ven.')"), None],
                'lines':
                    [1, 0, 'date',
                     _render("datetime.strptime(fecha_venc,'%Y-%m-%d')"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'glosa': {
                'header': [1, 20, 'text', _render("_('Glosa')"), None],
                'lines': [1, 0, 'text', _render("glosa or None")],
                'totals': [1, 0, 'text', None]
            },
        }

        # XLS Template VAT Summary
        self.col_specs_vat_summary_template = {
        }

    def _titulo_documento(self, titulo, ws, _p, row_pos, _xs):
        global VAR_SUBTOTAL
        global VAR_IGV
        global VAR_TOTAL
        global cnt
        cnt = 0
        VAR_SUBTOTAL = 0
        VAR_IGV = 0
        VAR_TOTAL = 0
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', titulo),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        return row_pos + 1

    def _lineas_documento(self, o, ws, _p, row_pos, _xs, data):
        global VAR_SUBTOTAL
        global VAR_IGV
        global VAR_TOTAL
        fila_inicial = row_pos
        # aca traigo las cabeceras
        wanted_list = self.wanted_list
        col_sub = 'importe_sin_igv' in wanted_list and wanted_list.index('importe_sin_igv')
        col_igv = 'igv' in wanted_list and wanted_list.index('igv')
        col_importe_total = 'importe_total' in wanted_list and wanted_list.index('importe_total')
        # print (o)
        # lineas de facturas
        tipo_comprobante = _p.tipo_comprobante_compra(o)
        aml_start_pos = row_pos
        aml_cnt = len(_p.get_data_fac(tipo_comprobante, data['fi'], data['ff'], data['filter']))
        # cnt = 0
        for tipo in tipo_comprobante:
            # cnt = 0
            # row_pos = self._titulo_documento(str('Tipo Doc.:' + ' ' + str(tipo['code'] + ' ' + tipo['name'])), ws, _p, row_pos, _xs)
            for l in _p.get_data_fac(tipo, data['fi'], data['ff'], data['filter']):
                for rate in _p.currency_rate(l['idcurrency']):
                    if rate['name'] == l['date_invoice']:
                        global cnt
                        cnt += 1
                        # print ('dsdddddddddddddddddddd', str(cnt))
                        count = cnt
                        # datos enviados directamente
                        tipo_cambio = rate['tc_venta_rate'] if l['codecambio'] == 'USD' else ''
                        moneda = 'D' if l['codecambio'] == 'USD' else 'S'
                        subtotal = '%.2f' % (l['amount_untaxed'] * rate['tc_venta_rate'])
                        exportacion_nograbadas = '%.2f' % ((l['exportacion_nograbadas'] or 0) * rate['tc_venta_rate'])
                        adquisicion_sinderecho = '%.2f' % ((l['adquisicion_sinderecho'] or 0) * rate['tc_venta_rate'])
                        adquisicion_nograbada = '%.2f' % ((l['adquisicion_nograbada'] or 0) * rate['tc_venta_rate'])

                        igv = '%.2f' % (l['amount_tax'] * rate['tc_venta_rate'])
                        igv_exportacion_nograbadas = '%.2f' % (
                                    (l['igv_exportacion_nograbadas'] or 0) * rate['tc_venta_rate'])
                        igv_adquisicion_sinderecho = '%.2f' % (
                                    (l['igv_adquisicion_sinderecho'] or 0) * rate['tc_venta_rate'])
                        otros_tributos = '%.2f' % ((l['otros_tributos'] or 0) * rate['tc_venta_rate'])
                        total = '%.2f' % (l['amount_total'] * rate['tc_venta_rate'])
                        tipo_doc = '6' if l['doc_type'] == 'ruc' else '1'

                        fecha_emision = l['date_invoice']
                        fecha_venc = l['date_due']
                        r_fecha = l['fecha_documento_ref']
                        r_doc = l['r_doc'] if l['r_doc'] else str(' ')
                        r_num = l['reference'] if l['r_doc'] else str(' ')
                        glosa = l['comment']
                        otras_ref_fecha = l['otra_fecha_documento_ref']
                        otras_ref_numero = l['otro_correlativo_documento_ref']

                        subtotal = subtotal if l['state'] != 'cancel' else str('0.00')
                        exportacion_nograbadas = exportacion_nograbadas if l['state'] != 'cancel' else str('0.00')
                        adquisicion_sinderecho = adquisicion_sinderecho if l['state'] != 'cancel' else str('0.00')
                        adquisicion_nograbada = adquisicion_nograbada if l['state'] != 'cancel' else str('0.00')

                        igv = igv if l['state'] != 'cancel' else str('0.00')
                        igv_exportacion_nograbadas = igv_exportacion_nograbadas if l['state'] != 'cancel' else str(
                            '0.00')
                        igv_adquisicion_sinderecho = igv_adquisicion_sinderecho if l['state'] != 'cancel' else str(
                            '0.00')
                        otros_tributos = otros_tributos if l['state'] != 'cancel' else str('0.00')
                        total = (float(total) +
                                 float(exportacion_nograbadas) +
                                 float(adquisicion_sinderecho) +
                                 float(adquisicion_nograbada) +
                                 float(igv_exportacion_nograbadas) +
                                 float(igv_adquisicion_sinderecho) +
                                 float(otros_tributos)) if l['state'] != 'cancel' else str('0.00')

                        subtotal_gravada_exportacion = subtotal
                        # subtotal_gravada_exportacion = subtotal if l['estado_expostacion_gravada_adqui'] == 'gravada_exportacion' else str('0.00')
                        #################
                        VAR_SUBTOTAL += float(subtotal)
                        VAR_IGV += float(igv)
                        VAR_TOTAL += float(total)
                        self.VAR_SUBTOTAL = VAR_SUBTOTAL
                        self.VAR_IGV = VAR_IGV
                        self.VAR_TOTAL = VAR_TOTAL

                        c_specs = map(
                            lambda x: self.render(x, self.col_specs_lines_template, 'lines'), wanted_list)
                        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                        row_pos = self.xls_write_row(
                            ws, row_pos, row_data, row_style=self.aml_cell_style)
                        # print (row_data)
                        # #separa lineas
                        # if cnt != aml_cnt:
                        # row_pos += 1
        print ('-------------------------------------')
        return row_pos

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        global cnt
        cnt = 0
        wanted_list = _p.wanted_list
        self.wanted_list = wanted_list
        self.col_specs_lines_template.update(_p.template_changes)

        # crear colores

        wb.set_colour_RGB(0x21, 142, 169, 219)

        # for o in data['tipos']:
        if str(data['tipo']) == 'purchase':
            sheet_name = 'Compras - '
        else:
            sheet_name = 'Ventas'
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # ws.write(20, 20, 'ghghgh', self.red)

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # titulo
        # row_pos = self._titulo_documento(data['mes'], ws, _p, row_pos, _xs)

        # Column headers
        c_specs = map(lambda x: self.render(
            x, self.col_specs_lines_template, 'header', render_space={'_': _p._}), wanted_list)
        print(c_specs)
        # for x in c_specs:
        #     print(x[0])
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # print(row_data)
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)  # seteamos la posicion estatica de bajada




        # data
        for o in data['tipos']:
            row_pos = self._lineas_documento(o, ws, _p, row_pos, _xs, data)


facturas_diario_xls_compras('report.facturas.diario.xls.compras', 'reporte.facturas.diario.compras',
                            parser=facturas_diario_xls_parser_compras)


class facturas_diario_xls_parser_ventas(general_factura_diario_ventas):

    def __init__(self, cr, uid, name, context):
        super(facturas_diario_xls_parser_ventas, self).__init__(cr, uid, name,
                                                                context=context)
        wizard_obj = self.pool.get('reporte.facturas.diario.ventas')
        self.context = context
        wanted_list = wizard_obj._report_xls_fields(cr, uid, context)
        template_changes = wizard_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,

        })


class facturas_diario_ventas_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(facturas_diario_ventas_xls, self).__init__(
            name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['borders_all']
        # rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(
            aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(
            aml_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # personalizados
        ajustar_texto = _xs['center'] + _xs['wrap'] + _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs[
            'vert_center']
        self.ajustar_texto_style = xlwt.easyxf(ajustar_texto)

        textonegrita = _xs['bold']
        self.textonegrita_style = xlwt.easyxf(textonegrita)

        # XLS Template Journal Items
        self.col_specs_lines_template = {
            'o': {
                'header': [1, 4, 'text', _render("_('O.')"), None],
                'lines': [1, 0, 'text', _render("('02')")],
                'totals': [1, 0, 'text', None]
            },
            'nro_voucher': {
                'header': [1, 4, 'text', _render("_('Vou.')"), None],
                'lines': [1, 0, 'text', _render("(str(count)) or None")],
                'totals': [1, 0, 'text', None]
            },
            'fecha_emision': {
                'header': [1, 13, 'text', _render("_('Fecha D.')"), None],
                'lines':
                    [1, 0, 'date',
                     _render("datetime.strptime(fecha_emision,'%Y-%m-%d') or None"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'fecha_vencimiento': {
                'header': [1, 13, 'text', _render("_('Fecha V.')"), None],
                'lines':
                    [1, 0, 'date',
                     _render("datetime.strptime(fecha_venc,'%Y-%m-%d') or None"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'tipo_documento': {
                'header': [1, 6, 'text', _render("_('Doc')"), None],
                'lines': [1, 0, 'text', _render("str(o).zfill(2) or None"), None,
                          self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]
            },
            'serie_documento': {
                'header': [1, 10, 'text', _render("_('Serie')"), None],
                'lines': [1, 0, 'text', _render("str(serie_d) or None")],
                'totals': [1, 0, 'text', None]
            },
            'correlativo_documento': {
                'header': [1, 12, 'text', _render("_('Número')"), None],
                'lines': [1, 0, 'text', _render("str(number_d) or None")],
                'totals': [1, 0, 'text', None]
            },
            'r_fecha': {
                'header': [1, 13, 'text', _render("_('R.Fecha.')"), None],
                'lines':
                    [1, 0, 'text', _render("r_fecha or None"),
                     None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]
            },
            'r_doc': {
                'header': [1, 7, 'text', _render("_('R.Doc.')"), None],
                'lines': [1, 0, 'text', _render("str(r_doc).zfill(2) if r_doc != '' else ''")],
                'totals': [1, 0, 'text', None]
            },
            'r_numero': {
                'header': [1, 15, 'text', _render("_('R.Número')"), None],
                'lines': [1, 0, 'text', _render("str(r_num) or None")],
                'totals': [1, 0, 'text', None]
            },
            'tipo_documento_identidad': {
                'header': [1, 5, 'text', _render("_('Doc')"), None],
                'lines': [1, 0, 'text', _render("str(tipo_doc) or None")],
                'totals': [1, 0, 'text', None]
            },
            'numero_documento_identidad': {
                'header': [1, 15, 'text', _render("_('Número')"), None],
                'lines': [1, 0, 'text', _render("l['doc_number'] if l['state'] != 'cancel' else '00000000000'")],
                'totals': [1, 0, 'text', None]
            },
            'nombre_proveedor': {
                'header': [1, 25, 'text', _render("_('Razón')"), None],
                'lines': [1, 0, 'text',
                          _render("l['nombre_proveedor'] if l['state'] != 'cancel' else 'COMPROBANTE ANULADO'")],
                'totals': [1, 0, 'text', None]
            },
            'valor_exportacion': {
                'header': [1, 13, 'text', _render("_('Valor Exp.')"), None],
                'lines': [1, 0, 'text', _render("str('0.00') or None")],
                'totals': [1, 0, 'number', None]
            },
            'importe_sin_igv': {
                'header': [1, 15, 'text', _render("_('B.Imp.')"), None],
                'lines': [1, 0, 'number', _render("subtotal"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("credit_formula if credit_formula > 0 else '0.00'"),
                           self.rt_cell_style_decimal]
            },
            'inafecto': {
                'header': [1, 15, 'text', _render("_('Inafecto')")],
                'lines': [1, 0, 'number', _render("str('0.00')"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None]
            },
            'campo_vacio4': {
                'header': [1, 10, 'text', _render("_('I.S.C')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'igv': {
                'header': [1, 15, 'text', _render("_('I.G.V')"), None],
                'lines': [1, 0, 'number', _render("igv"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("igv_formula if igv_formula > 0 else '0.00'"),
                           self.rt_cell_style_decimal]
            },
            'campo_vacio5': {
                'header': [1, 10, 'text', _render("_('Otros')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'campo_vacio6': {
                'header': [1, 12, 'text', _render("_('Exonerado')"), None],
                'lines': [1, 0, 'number', _render("str('0.00')")],
                'totals': [1, 0, 'number', None]
            },
            'importe_total': {
                'header': [1, 15, 'text', _render("_('Total')"), None],
                'lines': [1, 0, 'number', _render("total"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("total_formula if total_formula > 0 else '0.00'"),
                           self.rt_cell_style_decimal]
                # 'totals': [1, 0, 'number', None, _render("total_formula"),
                # self.rt_cell_style_decimal]
            },
            'tipo_cambio': {
                'header': [1, 10, 'text', _render("_('T/C')"), None],
                'lines': [1, 0, 'text', _render("str(tipo_cambio) if l['state'] != 'cancel' else str('')"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]
            },
            'glosa': {
                'header': [1, 20, 'text', _render("_('Glosa')"), None],
                'lines': [1, 0, 'text', _render("glosa or None")],
                'totals': [1, 0, 'text', None]
            },
        }

        # XLS Template VAT Summary
        self.col_specs_vat_summary_template = {
            'CAMPO0': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO1': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO2': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO3': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO4': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO5': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO6': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO7': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO8': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO9': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO10': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO11': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO12': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO13': {
                'tax_totals': [1, 0, 'text', None]},
            'tax_amount': {
                'tax_totals': [1, 0, 'number', _render("self.VAR_SUBTOTAL if self.VAR_SUBTOTAL > 0 else '0.00'"), None,
                               self.rt_cell_style_decimal]},
            'CAMPO15': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'CAMPO16': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'igv_tax': {
                'tax_totals': [1, 0, 'number', _render("self.VAR_IGV if self.VAR_IGV > 0 else '0.00'"), None,
                               self.rt_cell_style_decimal]},
            'CAMPO18': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'CAMPO19': {
                'tax_totals': [1, 0, 'text', _render("str('0.00')"), None, self.rt_cell_style_decimal]},
            'total_total': {
                'tax_totals': [1, 0, 'number', _render("self.VAR_TOTAL if self.VAR_TOTAL > 0 else '0.00'"), None,
                               self.rt_cell_style_decimal]},
            'CAMPO21': {
                'tax_totals': [1, 0, 'text', None]},
            'CAMPO22': {
                'tax_totals': [1, 0, 'text', None]},
        }

    def _titulo_documento(self, titulo, ws, _p, row_pos, _xs):
        global VAR_SUBTOTAL
        global VAR_IGV
        global VAR_TOTAL
        VAR_SUBTOTAL = 0
        VAR_IGV = 0
        VAR_TOTAL = 0
        # cell_style = xlwt.easyxf(_xs['xls_title'])
        # c_specs = [
        #     ('report_name', 1, 0, 'text', titulo),
        # ]
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(
        #     ws, row_pos, row_data, row_style=cell_style)
        return row_pos

    def _lineas_documento(self, o, ws, _p, row_pos, _xs, data):
        global totales_generales
        global VAR_SUBTOTAL
        global VAR_IGV
        global VAR_TOTAL
        fila_inicial = row_pos
        # aca traigo las cabeceras
        wanted_list = self.wanted_list
        col_sub = 'importe_sin_igv' in wanted_list and wanted_list.index('importe_sin_igv')
        col_igv = 'igv' in wanted_list and wanted_list.index('igv')
        col_importe_total = 'importe_total' in wanted_list and wanted_list.index('importe_total')
        # lineas de facturas
        tipo_n = ''
        aml_cnt = len(_p.get_data_fac(o, data['fi'], data['ff']))
        # print ('tamaños ',str(o),'---->>>',str(aml_cnt))
        # if aml_cnt > 0:
        #     if int(o) == 1:
        #         tipo_n = 'Tipo Doc.: 01 Factura'
        #     if int(o) == 3:
        #         tipo_n = 'Tipo Doc.: 03 Boleta de Ventas'
        #     if int(o) == 7:
        #         tipo_n = 'Tipo Doc.: 07 Notas de Credito'
        row_pos = self._titulo_documento(tipo_n, ws, _p, row_pos, _xs)
        # c_specs = [
        #     ('fy', 1, 0, 'text', _(str(tipo_n)), None, self.textonegrita_style),
        # ]
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(
        #     ws, row_pos, row_data, row_style=self.aml_cell_style)
        # cnt = 0
        for l in _p.get_data_fac(o, data['fi'], data['ff']):
            # number_d = str(l['internal_number']).split('-')
            # number_d = number_d[1]
            # print (number_d)
            for rate in _p.currency_rate(l['idcurrency']):
                if int(l['code']) != 7:
                    fecha = l['date_invoice']
                else:
                    fecha = l['r_fecha']
                if rate['name'] == fecha:
                    # print (l)

                    global cnt
                    cnt += 1
                    # print ('dsdddddddddddddddddddd', str(cnt))
                    count = cnt
                    tipo_cambio = rate['tc_venta_rate'] if l['codecambio'] == 'USD' else ''
                    subtotal = '%.2f' % (l['amount_untaxed'] * rate['tc_venta_rate'])
                    igv = '%.2f' % (l['amount_tax'] * rate['tc_venta_rate'])
                    total = '%.2f' % (l['amount_total'] * rate['tc_venta_rate'])
                    if o != 7:
                        serie_d = str(l['internal_number']).split('-')
                        serie_d = serie_d[0]
                        number_d = str(l['internal_number']).split('-')
                        number_d = number_d[1]
                        fecha_emision = l['date_invoice']
                        fecha_venc = l['date_due']
                        r_fecha = ''
                        r_doc = ''
                        r_num = ''
                        glosa = l['comment']
                        subtotal = subtotal if l['state'] != 'cancel' else str('0.00')
                        igv = igv if l['state'] != 'cancel' else str('0.00')
                        total = total if l['state'] != 'cancel' else str('0.00')
                    else:
                        serie_d = str(l['r_num']).split('-')
                        serie_d = serie_d[0]
                        number_d = str(l['r_num']).split('-')
                        number_d = number_d[1]
                        fecha_emision = l['r_fecha']
                        fecha_venc = l['r_fecha']
                        r_fecha = l['date_invoice']
                        r_doc = l['r_doc']
                        r_num = l['internal_number']
                        glosa = l['descripcion']
                        subtotal = -(float(subtotal))
                        igv = -(float(igv))
                        total = -(float(total))
                    # print (number_d)
                    # datos enviados directamente
                    if l['state'] == 'cancel':
                        tipo_doc = '0'
                    else:
                        tipo_doc = '6' if l['doc_type'] == 'ruc' else '1'
                    #################
                    VAR_SUBTOTAL += float(subtotal)
                    VAR_IGV += float(igv)
                    VAR_TOTAL += float(total)
                    self.VAR_SUBTOTAL = VAR_SUBTOTAL
                    self.VAR_IGV = VAR_IGV
                    self.VAR_TOTAL = VAR_TOTAL
                    # print ('self.VAR_SUBTOTAL----->', str(self.VAR_SUBTOTAL))
                    c_specs = map(
                        lambda x: self.render(x, self.col_specs_lines_template, 'lines'), wanted_list)

                    row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(
                        ws, row_pos, row_data, row_style=self.aml_cell_style)

                    # print (row_data)
                    # #separa lineas
                    # if cnt != aml_cnt:
                    #     cnt += 1
                    # Totals
        # if aml_cnt > 0:
        #     credit_start = rowcol_to_cell(fila_inicial, col_sub)
        #     credit_stop = rowcol_to_cell(row_pos - 1, col_sub)
        #     credit_formula = 'SUM(%s:%s)' % (credit_start, credit_stop)
        #     print ('credit_formula', str(credit_formula))
        #     print ('igv')
        #     igv_start = rowcol_to_cell(fila_inicial, col_igv)
        #     igv_stop = rowcol_to_cell(row_pos - 1, col_igv)
        #     igv_formula = 'SUM(%s:%s)' % (igv_start, igv_stop)
        #     importe_total_start = rowcol_to_cell(fila_inicial, col_importe_total)
        #     importe_total_stop = rowcol_to_cell(row_pos - 1, col_importe_total)
        #     total_formula = 'SUM(%s:%s)' % (importe_total_start, importe_total_stop)
        #     c_specs = map(lambda x: self.render(x, self.col_specs_lines_template, 'totals'), wanted_list)
        #     row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        #     row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        # return row_pos + 1 umentar una linea por tipo
        return row_pos

    def _totales_documento(self, titulo, ws, _p, row_pos, _xs):
        wanted_list = self.wanted_list
        vat_summary_wanted_list = ['CAMPO1',
                                   'CAMPO2',
                                   'CAMPO3',
                                   'CAMPO4',
                                   'CAMPO5',
                                   'CAMPO6',
                                   'CAMPO7',
                                   'CAMPO8',
                                   'CAMPO9',
                                   'CAMPO10',
                                   'CAMPO11',
                                   'CAMPO12',
                                   'CAMPO13',
                                   'tax_amount',
                                   'CAMPO15',
                                   'CAMPO16',
                                   'igv_tax',
                                   'CAMPO18',
                                   'CAMPO19',
                                   'total_total',
                                   'CAMPO21',
                                   'CAMPO22', ]

        c_specs = map(lambda x: self.render(x, self.col_specs_vat_summary_template, 'tax_totals'),
                      vat_summary_wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.aml_cell_style)

        return row_pos + 1

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        global cnt
        cnt = 0
        wanted_list = _p.wanted_list
        self.wanted_list = wanted_list
        self.col_specs_lines_template.update(_p.template_changes)

        # for o in data['tipos']:
        if str(data['tipo']) == 'purchase':
            sheet_name = 'Compras - '
        else:
            sheet_name = 'Ventas'
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # titulo
        # row_pos = self._titulo_documento(data['mes'], ws, _p, row_pos, _xs)

        # Column headers
        c_specs = map(lambda x: self.render(
            x, self.col_specs_lines_template, 'header', render_space={'_': _p._}), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)  # seteamos la posicion estatica de bajada

        # data
        for o in data['tiposc']:
            row_pos = self._lineas_documento(o, ws, _p, row_pos, _xs, data)

        # row_pos = self._totales_documento(data['mes'], ws, _p, row_pos, _xs)


facturas_diario_ventas_xls('report.facturas.diario.ventas.xls', 'reporte.facturas.diario.ventas',
                           parser=facturas_diario_xls_parser_ventas)
