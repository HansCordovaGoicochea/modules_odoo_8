# -*- coding: utf-8 -*-
import logging
import base64
from openerp import api, models, fields
from openerp.tools.translate import _
import datetime
import time
import calendar
import locale
locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
from datetime import date
from dateutil.relativedelta import relativedelta
from ..report.nominas_empleados_init import general_nominas_empleados

import unicodedata

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

anio = ''
date_to = ''

class reporte_tareas_personal(models.TransientModel):
    _name = "reporte.tareas.personal"
    _description = "Tareas del Personal"

    def _get_fiscalyear(self):
        global anio
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', 1), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.env['account.fiscalyear'].search(domain, limit=1)
        anio = fiscalyears.name
        return fiscalyears.id and fiscalyears[0] or False

    # @api.onchange('fiscalyear_id')
    def onchange_fiscalyear_id(self):
        global anio, date_to
        res = {'value': {}}
        start_period = end_period = False
        abc = self._get_fiscalyear()
        # print (abc)
        anio = abc.name
        self._cr.execute('''
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
                                       LIMIT 1) AS period_stop''', (abc.id, abc.id))
        periods = [i[0] for i in self._cr.fetchall()]
        # print (periods)
        if periods and len(periods) > 1:
            start_period = periods[0]
            end_period = periods[1]
        res['value'] = {'period_to': end_period}
        # self.period_to = end_period
        date_to = self.env['account.period'].search([['id','=',end_period]]).date_start
        # print (date_to)
        return end_period


    company_id = fields.Many2one('res.company', 'Empresa', default=1)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Año Fiscal', default=_get_fiscalyear)
    period_to = fields.Many2one('account.period', 'Periodo', default=onchange_fiscalyear_id)

    @api.onchange('period_to')
    def onchange_period_to(self):
        global date_to
        date_to = self.period_to.date_start

    @api.multi
    def check_report_tareas(self):
        empleados_obj = self.env['hr.employee']
        Mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
               "Noviembre", "Diciembre"]
        fecha_desde = self.period_to.date_start
        # print (fecha_desde)
        # print (self._context)
        fecha_hasta = self.period_to.date_stop
        spli_date_to = fecha_desde.split('-')
        # mes_de = 'REGISTRO DE COMPRAS DEL MES DE '+ str(Mes[int(spli_date_to[1])-1])
        em = []
        empleados = empleados_obj.search([])
        for e in empleados:
            em.append(e.id)

        # print (tipos)
        data = {'company': self.company_id.partner_id.name, 'companyruc': self.company_id.x_ruc, 'companydir': self.company_id.partner_id.street, 'companyimage': self.company_id.logo_web, 'mes': str(Mes[int(spli_date_to[1])-1]), 'anio': self.fiscalyear_id.name, 'desde': fecha_desde, 'hasta': fecha_hasta, 'ids_emp': em}
        if self._context.get('xls_export'):
            # print ('ddddddddddddddddddddddddddddddddddd')
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'reporte.tareas.xls',
                    'datas': data}

    @api.multi
    def _report_xls_fields(self):
        global anio, date_to
        fecha_desde = date_to
        spli_date_to = fecha_desde.split('-')
        ultimo_dia = calendar.monthrange(int(anio), int(spli_date_to[1]))
        desde = date(int(fecha_desde[0:4]), int(fecha_desde[5:7]), int(1))
        hasta = date(int(fecha_desde[0:4]), int(fecha_desde[5:7]), int(ultimo_dia[1]))
        dias_totales = (hasta - desde).days

        header_list = ['empleado']
        for t in range(int(dias_totales)+1):
            fecha = desde + relativedelta(days=t)
            dia_str = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%a').upper()
            header_list.append(str(t))
        # print (header_list)
        return header_list


     # Change/Add Template entries
    @api.multi
    def _report_xls_template(self):
        from openerp.addons.report_xls.utils import rowcol_to_cell, _render
        global anio, date_to
        fecha_desde = date_to
        spli_date_to = fecha_desde.split('-')
        ultimo_dia = calendar.monthrange(int(anio), int(spli_date_to[1]))
        desde = date(int(fecha_desde[0:4]), int(fecha_desde[5:7]), int(1))
        hasta = date(int(fecha_desde[0:4]), int(fecha_desde[5:7]), int(ultimo_dia[1]))
        dias_totales = (hasta - desde).days
        # em = general_nominas_empleados.probando_empleados()
        # for e in em:
        #     abc = e['name_related']
        # print (_render("codigo_dias or ''"))
        my_change = {
            'empleado':{
                'header': [1, 50, 'text', _render("_('')")],
                'lines': [1, 0, 'text', _render("abc")]
            },
        }
        for t in range(int(dias_totales) + 1):
            fecha = desde + relativedelta(days=t)
            dia_str = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%a').upper().decode('latin-1')
            # letras_dia = self.elimina_tildes(str(dia_str).decode('utf-8'))

            my_change[str(t)] = {
                'header': [1, 7, 'text', _render("_('" + str(dia_str) + "')")],
                'lines': [1, 0, 'text', _render("codigo_dias or ''")]
            }
        return my_change
        # return {}

    def elimina_tildes(self, cadena):
        s = ''.join((c for c in unicodedata.normalize('NFD', unicode(cadena)) if unicodedata.category(c) != 'Mn'))
        return s.decode()
