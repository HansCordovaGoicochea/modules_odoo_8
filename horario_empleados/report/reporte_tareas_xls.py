# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import calendar
from PIL import Image
import xlwt
from datetime import datetime, date
# from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from .nominas_empleados_init import general_nominas_empleados
from openerp.tools.translate import translate, _
import logging
# from xlwt.Style import default_style

_logger = logging.getLogger(__name__)
_ir_translation_name = 'horario_empleados.report_tareas_personal_xls'
cnt = 0

class reporte_tareas_xls_parser(general_nominas_empleados):

    def __init__(self, cr, uid, name, context):
        super(reporte_tareas_xls_parser, self).__init__(cr, uid, name,context=context)
        wizard_obj = self.pool.get('reporte.tareas.personal')
        self.context = context
        wanted_list = wizard_obj._report_xls_fields(cr, uid, context)
        template_changes = wizard_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src

class reporte_tareas_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(reporte_tareas_xls, self).__init__(
            name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
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
        ajustar_texto = _xs['center'] + _xs['wrap'] + _xs['bold'] + _xs['fill'] + _xs['borders_all']+ _xs['vert_center']
        self.ajustar_texto_style = xlwt.easyxf(ajustar_texto)

        # XLS Template Journal Items
        self.col_specs_lines_template = {
            # 'empleado': {
            #     'header': [1, 10, 'text', _render("_('Empleado')"), None, self.ajustar_texto_style],
            #     'lines': [1, 0, 'text', _render('ddd')],
            # }
            # 'dias': {
            #     'header': [1, 13, 'text', _render("_('F. Emisión')"), None, self.ajustar_texto_style],
            #     'lines':
            #         [1, 0, 'date',
            #          _render("datetime.strptime(l['date_invoice'],'%Y-%m-%d')"),
            #          None, self.aml_cell_style_date],
            # },
        }


    def _titulo_documento(self, titulo, ws, _p, row_pos, _xs):
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', titulo),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        return row_pos + 1

    def _lineas_documento(self, o, ws, _p, row_pos, _xs, d):
        # print (o)
        # aca traigo las cabeceras
        wanted_list = self.wanted_list
        # length_dict = ([len(v) for v in _p.probando_empleados(o['desde'], o['hasta'], d)])[0]
        # print (length_dict)
        for l in _p.probando_empleados(o['desde'], o['hasta'], d):
            # print (l)
            cou = len(l.keys()) - 1
            global cnt
            cnt += 1
            count = cnt
            # datos enviados directamente
            abc = l['name_related']
            codigo_dias = l['1']
            # print (codigo_dias)

            c_specs = map(lambda x: self.render(x, self.col_specs_lines_template, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.aml_cell_style)

        return row_pos + 0

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        wanted_list = _p.wanted_list
        self.wanted_list = wanted_list
        self.col_specs_lines_template.update(_p.template_changes)

        border_totales = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')

        # agregar nuevo color de la paleta y setear RGB el calor del color
        xlwt.add_palette_colour("custom_colour", 0x21)
        wb.set_colour_RGB(0x21, 101, 217, 229)

        amarillo = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                 left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour yellow;')
        verde = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                 left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour green;')
        rojo = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                 left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour red;')
        naranja = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                 left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour orange;')

        celeste = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                 left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour custom_colour;')

        # ultimo dia entre fechas
        spli_date_to = data['desde'].split('-')
        ultimo_dia = calendar.monthrange(int(data['anio']), int(spli_date_to[1]))
        # print (ultimo_dia)

        ws = wb.add_sheet(data['mes'])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 11

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # tl = xlwt.easyxf('font: bold on; borders: bottom dashed')

        # titulo
        # row_pos = self._titulo_documento(data['mes'], ws, _p, row_pos, _xs)
        # insertar imgen
        fh = open("D:/imageToSave.png", "wb")
        fh.write(data['companyimage'].decode('base64'))
        fh.close()

        img = Image.open("D:/imageToSave.png")
        r, g, b = img.split()
        img = Image.merge("RGB", (r, g, b))
        img.save('d:/imagetoadd.bmp')
        ws.insert_bitmap('d:/imagetoadd.bmp', 1, 0, x=10, scale_x=0.3, scale_y=0.9)

        # informacion adicioanl merge
        """
        top_row = 1
        bottom_row = 1
        left_column = 20
        right_column = 23
        ws.merge(top_row, bottom_row, left_column, right_column)
        """
        tl = xlwt.easyxf('font: bold on; border: left thick, top thick, left thick, right thick')
        tr = xlwt.easyxf('border: right thick, top thick')
        r = xlwt.easyxf('border: right thick')
        br = xlwt.easyxf('border: right thick, bottom thick')
        bl = xlwt.easyxf('font: bold on; border: left thick, bottom thick, right thick')
        l = xlwt.easyxf('font: bold on; border: left thick, right thick')

        ws.write_merge(1, 1, 5, 9, 'RUC', style=tl)
        ws.write_merge(1, 1, 10, 16, str(data['companyruc']), style=tr)
        ws.write_merge(2, 2, 5, 9, 'DIR', style=l)
        ws.write_merge(2, 2, 10, 16, str(data['companydir']), style=r)
        ws.write_merge(3, 3, 5, 9, 'FECHA INICIO', style=l)
        ws.write_merge(3, 3, 10, 16, _p.try_parsing_date(str(data['desde'])), style=r)
        ws.write_merge(4, 4, 5, 9, 'FECHA FIN', style=bl)
        ws.write_merge(4, 4, 10, 16, _p.try_parsing_date(str(data['hasta'])), style=br)

        #  leyenda de colores
        ws.write_merge(1, 1, 20, 26, 'LEYENDA', style= self.ajustar_texto_style)
        ws.write_merge(2, 2, 20, 20, 'T', style= border_totales)
        ws.write_merge(2, 2, 21, 21, '', style= border_totales)
        ws.write_merge(2, 2, 22, 26, 'TRABAJO', style= border_totales)
        ws.write_merge(3, 3, 20, 20, 'NT', style= border_totales)
        ws.write_merge(3, 3, 21, 21, '', style= amarillo)
        ws.write_merge(3, 3, 22, 26, 'NO TRABAJO', style= border_totales)
        ws.write_merge(4, 4, 20, 20, 'FI', style= border_totales)
        ws.write_merge(4, 4, 21, 21, '', style= rojo)
        ws.write_merge(4, 4, 22, 26, 'FALTA INJUSTIFICADA', style= border_totales)
        ws.write_merge(5, 5, 20, 20, 'V', style= border_totales)
        ws.write_merge(5, 5, 21, 21, '', style= verde)
        ws.write_merge(5, 5, 22, 26, 'VACACIONES', style= border_totales)
        ws.write_merge(6, 6, 20, 20, 'DM', style= border_totales)
        ws.write_merge(6, 6, 21, 21, '', style= celeste)
        ws.write_merge(6, 6, 22, 26, 'DESCANSO MEDICO', style= border_totales)
        ws.write_merge(7, 7, 20, 20, 'PS', style= border_totales)
        ws.write_merge(7, 7, 21, 21, '', style= naranja)
        ws.write_merge(7, 7, 22, 26, 'TODO PERMISOS', style= border_totales)


        # cabeceras extras
        c_specs = [
            ('fy', 1, 150, 'text', _('EMPLEADO'), None, self.ajustar_texto_style),
            ('af', int(ultimo_dia[1]), 0, 'text', _('HOJA DEL TAREO DEL MES DE '+str(data['mes']).upper()+' DEL 2017'), None, self.ajustar_texto_style),


        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.aml_cell_style)

        # cabeceras extras
        c_specs = [
            ('fy', 1, 150, 'text', _(''), None, self.ajustar_texto_style),
        ]


        for i in range(1,int(ultimo_dia[1])+1,1):
            c_specs.append(('af'+str(i), 1, 0, 'text', _(str(i)), None,
             self.ajustar_texto_style),)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.aml_cell_style)

        # Column headers
        c_specs = map(lambda x: self.render(x, self.col_specs_lines_template, 'header', render_space={'_': _p._}), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)  # seteamos la posicion estatica de bajada
        ws.set_vert_split_pos(1) # seteamos la posicion estatica de izquierda a derecha

        # data
        row = 13
        for d in data['ids_emp']:
            # row_pos = self._lineas_documento(data, ws, _p, row_pos, _xs, d)
            # length_dict = (([len(v) for v in _p.probando_empleados(data['desde'], data['hasta'], d)])[0]) or 0
            for l in _p.probando_empleados(data['desde'], data['hasta'], d):
                row = row + 1
                leng = len(l) - 1
                cou = 0
                ws.write(row, 0, l['name_related'] or '', style=border_totales)
                for le in range(1, leng+1, 1):
                    cou += 1
                    if l[str(cou)] == 'DM':
                        ws.write(row, cou, l[str(cou)] or '', style=celeste)
                    elif l[str(cou)] == 'NT':
                        ws.write(row, cou, l[str(cou)] or '', style=amarillo)
                    elif l[str(cou)] == 'FI':
                        ws.write(row, cou, l[str(cou)] or '', style=rojo)
                    elif l[str(cou)] == 'V':
                        ws.write(row, cou, l[str(cou)] or '', style=verde)
                    elif l[str(cou)] == 'PS':
                        ws.write(row, cou, l[str(cou)] or '', style=naranja)
                    else:
                        ws.write(row, cou, l[str(cou)] or '', style=border_totales)
                # for index, col in enumerate(d):

reporte_tareas_xls('report.reporte.tareas.xls', 'reporte.tareas.personal',
                    parser=reporte_tareas_xls_parser)